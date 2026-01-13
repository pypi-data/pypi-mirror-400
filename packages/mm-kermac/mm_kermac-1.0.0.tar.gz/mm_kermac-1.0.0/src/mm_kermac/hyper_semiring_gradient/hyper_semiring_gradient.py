# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

from cuda.core import Device, LaunchConfig, Stream, launch, ObjectCode

from mm_kermac.ptx_inject_cache.ptx_inject_cache import *
from mm_kermac.ptx_inject_cache.ptx_inject_types import DataTypeInfo
from mm_kermac.common import *

import torch
import numpy as np

import mm_ptx.ptx_inject as ptx_inject
import mm_ptx.stack_ptx as stack_ptx

from mm_kermac.stack_ptx_types import Stack
from mm_kermac.stack_ptx_types import compiler as stack_ptx_compiler

class HyperSemiringGradientKernel():
    def __init__(
        self,
        multiply_lambda,
        accumulate_lambda,
        epilogue_lambda,
        execution_limit=100,
        max_ast_size=100,
        max_ast_to_visit_stack_depth=20,
        stack_size=128,
        max_frame_depth=4
    ):
        self.multiply_lambda = multiply_lambda
        self.accumulate_lambda = accumulate_lambda
        self.epilogue_lambda = epilogue_lambda

        self.cubin_kernels_dict = {}

        self.execution_limit = execution_limit
        self.max_ast_size = max_ast_size
        self.max_ast_to_visit_stack_depth = max_ast_to_visit_stack_depth
        self.stack_size = stack_size
        self.max_frame_depth = max_frame_depth

    def _validate_and_collect_hypers(
        self,
        hyper_dict: dict[str, torch.Tensor] | None,
        L: int,
        tensor_device: torch.device
    ):
        """
        - Merges batch size over all hyper tensors (expected scalar or length-L).
        - Ensures each value is a CUDA float32 tensor on the same device.
        - Returns updated L and a list[(name, tensor)] preserving dict insertion order.
        """
        if hyper_dict is None:
            return L, []

        if not isinstance(hyper_dict, dict):
            raise TypeError("hyper_dict must be a dict[str, torch.Tensor]")

        # 1) Merge batch size
        for name, t in hyper_dict.items():
            if not isinstance(t, torch.Tensor):
                raise TypeError(f"hyper_dict['{name}'] must be a torch.Tensor")
            # Scalars (0-D) or per-batch (1-D) supported, same behavior as inner_p/outer_p/etc
            L = merge_batch_size(f"hyper_dict['{name}']", L, t, expected_dims=0, can_be_none=False)

        # 2) Dtype / CUDA / device checks
        for name, t in hyper_dict.items():
            if t.dtype != torch.float32:
                raise TypeError(f"hyper_dict['{name}'] must have dtype torch.float32")
            if not t.is_cuda:
                raise ValueError(f"hyper_dict['{name}'] must be on a CUDA device")
            if t.device != tensor_device:
                raise ValueError(
                    f"hyper_dict['{name}'] must be on device {tensor_device}, got {t.device}"
                )

        # Keep the (name, tensor) pairs in insertion order
        return L, list(hyper_dict.items())

    def _render_function_name(
        self,
        num : int,
    ):
        function_name = f'cute_hyper_semiring_gradient_{num}'
        return function_name
    
    def _create_hyper_semiring_template(
        self,
        num : int
    ):
        template_source_file = get_local_cuda_kernel_dir() / 'template_hyper_semiring_gradient.cuh'

        with open(template_source_file, "r") as f:
            content = f.read()
            num_sites = 11

            def _ptx_in_block(indent: int) -> str:
                if num == 0:
                    return ""
                return "".join(
                    f",\n{' ' * indent}PTX_IN(F32, hyper{i})" for i in range(num)
                )
            
            templates = [
                "\n\t".join(f"class HYPER{i}Stride," for i in range(num)),
                f"{num}",
                "\n\t".join(f", T* HYPER{i}, HYPER{i}Stride dHYPER{i}" for i in range(num)),
                "\n\t".join(f" Tensor mHYPER{i} = make_tensor(make_gmem_ptr(HYPER{i}), select<3>(shape_MNOKL), dHYPER{i});" for i in range(num)),
                "\n\t".join(f"T hyper{i} = mHYPER{i}(bidw);" for i in range(num)),
                _ptx_in_block(24),
                _ptx_in_block(28),
                _ptx_in_block(12),
                "\n\t".join(f", float *hyper{i},    uint64_t batch_stride_hyper{i}" for i in range(num)),
                "\n\t".join(f"auto d_hyper{i} = make_stride(batch_stride_hyper{i});" for i in range(num)),
                "\n\t\t".join(f", hyper{i}, d_hyper{i}" for i in range(num)),
            ]

            for i in range(num_sites):
                content = content.replace(f"@{i}@", templates[i])

            # Prints the generated template
            # with open(get_top_level_repo_dir('') / f'rendered_hyper_semiring_gradient_{num}.cuh', 'w') as file:
            #     file.write(content)

            return content
    
    def __call__(
        self,
        a : torch.Tensor,           # [K,M]     # M-major # [N,M]   # kernel_matrix
        b : torch.Tensor,           # [N,K]     # K-major # [D,N]   # x
        c : torch.Tensor,           # [O,K]     # K-major # [C,N]   # coefs
        d : torch.Tensor,           # [N,M]     # M-major # [D,M]   # z
        hyper_dict : dict[str, torch.Tensor] = None,
        out : torch.Tensor = None,  # [O,N,M]   # M-major # [C,D,M] # grad
        debug = False
    ):
        # Check if inputs are tensors
        if not all(isinstance(x, torch.Tensor) for x in (a, b, c, d)):
            raise TypeError("All inputs must be PyTorch tensors")
        if out is not None and not isinstance(out, torch.Tensor):
            raise TypeError("out must be a PyTorch tensor if provided")
        
        # Check dtype for a, b, c, d
        if not all(x.dtype == torch.float32 for x in (a, b, c, d)):
            raise TypeError("All inputs must have dtype torch.float32")
        # Check dtype for out, if provided
        if out is not None and out.dtype != torch.float32:
            raise TypeError("out must have dtype torch.float32")
        
        # Check number of dimensions for a, b, c, d
        if not all((x.dim() == 2 or x.dim() == 3) for x in (a, b, c, d)):
            raise ValueError("All inputs must be 2-dimensional or 3-dimensional with a batch mode")
        # Check number of dimensions for out, if provided
        if out is not None and (out.dim() != 3 and out.dim() != 4):
            raise ValueError("out must be 3-dimensional or 4-dimensional with a batch mode")

        # Check CUDA device for a, b, c, d
        if not all(x.is_cuda for x in (a, b, c, d)):
            raise ValueError("All inputs must be on a CUDA device")
        # Check CUDA device for out, if provided
        if out is not None and not out.is_cuda:
            raise ValueError("out must be on a CUDA device")

        tensor_device = a.device
        # Check device consistency for a, b, c, d
        if not all(x.device == tensor_device for x in (a, b, c, d)):
            raise ValueError(f"All inputs must be on the same CUDA device: got {[x.device for x in (a, b, c, d)]}")
        # Check device consistency for out, if provided
        if out is not None and out.device != tensor_device:
            raise ValueError(f"out must be on the same CUDA device as inputs: got {out.device}, expected {tensor_device}")
        
        tensor_stats_a = tensor_stats(a)
        tensor_stats_b = tensor_stats(b)
        tensor_stats_c = tensor_stats(c)
        tensor_stats_d = tensor_stats(d)
        
        _, K_a, M_a = tensor_stats_a.shape
        _, N_b, K_b = tensor_stats_b.shape
        _, O_c, K_c = tensor_stats_c.shape
        _, N_d, M_d = tensor_stats_d.shape

        L = 1
        L = merge_batch_size('a', L, a, expected_dims=2, can_be_none=False)
        L = merge_batch_size('b', L, b, expected_dims=2, can_be_none=False)
        L = merge_batch_size('c', L, c, expected_dims=2, can_be_none=False)
        L = merge_batch_size('d', L, d, expected_dims=2, can_be_none=False)
        L = merge_batch_size('out', L, out, expected_dims=3, can_be_none=True)

        L, hyper_items = self._validate_and_collect_hypers(hyper_dict, L, tensor_device)
        num_hypers = len(hyper_items)

        if out is not None:
            L_e = 1 if out.dim() == 2 else out.size(0)
            if L_e != L and L != 1:
                raise ValueError(f"out must have batch dimension (L={L}), got {(L_e)}")

        # L is decided
        K = K_a
        M = M_a
        N = N_b
        O = O_c

        shape_a = (K_a, M_a)
        shape_b = (N_b, K_b)
        shape_c = (O_c, K_c)
        shape_d = (N_d, M_d)

        # Check shapes
        if shape_a != (K, M):
            raise ValueError(f"Expected shape {(K, M)} for a, got {shape_a}")
        if shape_b != (N, K):
            raise ValueError(f"Expected shape {(N, K)} for b, got {shape_b}")
        if shape_c != (O, K):
            raise ValueError(f"Expected shape {(O, K)} for c, got {shape_c}")
        if shape_d != (N, M):
            raise ValueError(f"Expected shape {(N, M)} for d, got {shape_d}")
        if out is not None:
            if L == 1:
                if (out.shape != (O, N, M) and out.shape != (1, O, N, M)):
                    raise ValueError(f"Expected shape {(O, N, M)} or {(L, O, N, M)} for out, got {out.shape}")
            else:
                if (out.shape != (L, O, N, M)):
                    raise ValueError(f"Expected shape {(L, O, N, M)} for out, got {out.shape}")

        # Check strides (stride 1 in last dimension)
        if a.stride(-1) != 1:
            raise ValueError("a must have stride 1 in last dimension")
        if b.stride(-1) != 1:
            raise ValueError("b must have stride 1 in last dimension")
        if c.stride(-1) != 1:
            raise ValueError("c must have stride 1 in last dimension")
        if d.stride(-1) != 1:
            raise ValueError("d must have stride 1 in last dimension")
        if out is not None and out.stride(-1) != 1:
            raise ValueError("out must have stride 1 in last dimension")
        
        out = torch.zeros((L, O, N, M), dtype=torch.float32, device=tensor_device) if out is None else out

        pt_stream = torch.cuda.current_stream()
        pt_device = pt_stream.device
        device = Device(pt_device.index)
        device.set_current()
        stream = Stream.from_handle(int(pt_stream.cuda_stream))

        if tensor_device != pt_device:
            raise ValueError("cuda stream must be on the same device as the tensors: got {pt_device}, expected {tensor_device}")

        function_name = self._render_function_name(num_hypers)
        dict_key = device, function_name
        kernel = None
        if (dict_key in self.cubin_kernels_dict):
            # We found the kernel already loaded for this majorness and alignment
            # (With the same injected PTX)
            kernel = self.cubin_kernels_dict[dict_key]
        else:
            def get_cuda_source_lambda():
                return self._create_hyper_semiring_template(num_hypers)
            # We did not find the kernel for the number of hyper parameters requested.
            # Go ahead and grab the PTX out of the database, inject it,
            # get the kernel and cache it locally to the class.
            # If the PTX wasn't already compiled the ptx_inject_cache will 
            # handle it and store in DB.
                
            ptx_inject_cache = PtxInjectCache(debug)
            annotated_ptx, lowered_name = \
                ptx_inject_cache.get_function(
                    device,
                    function_name, 
                    get_cuda_source_lambda,
                    debug=debug
                )
            inject = ptx_inject.PTXInject(annotated_ptx)

            multiply = inject['multiply']
            accumulate = inject['accumulate']
            epilogue = inject['epilogue']

            assert( multiply['a'].mut_type == ptx_inject.MutType.IN )
            assert( multiply['a'].data_type == DataTypeInfo.F32 )

            assert( multiply['b'].mut_type == ptx_inject.MutType.IN )
            assert( multiply['b'].data_type == DataTypeInfo.F32 )

            assert( multiply['d'].mut_type == ptx_inject.MutType.IN )
            assert( multiply['d'].data_type == DataTypeInfo.F32 )

            assert( multiply['diff'].mut_type == ptx_inject.MutType.OUT )
            assert( multiply['diff'].data_type == DataTypeInfo.F32 )

            assert( accumulate['c'].mut_type == ptx_inject.MutType.IN )
            assert( accumulate['c'].data_type == DataTypeInfo.F32 )

            assert( accumulate['diff'].mut_type == ptx_inject.MutType.IN )
            assert( accumulate['diff'].data_type == DataTypeInfo.F32 )

            assert( accumulate['e'].mut_type == ptx_inject.MutType.MOD )
            assert( accumulate['e'].data_type == DataTypeInfo.F32 )

            assert( epilogue['e'].mut_type == ptx_inject.MutType.MOD )
            assert( epilogue['e'].data_type == DataTypeInfo.F32 )

            # assert the types for each hyper parameter found in the inject.
            hyper_names = [f"hyper{i}" for i in range(num_hypers)]
            for h in hyper_names:
                for group, gname in (
                    (multiply, "multiply"),
                    (accumulate, "accumulate"),
                    (epilogue, "epilogue")
                ):
                    assert group[h].mut_type == ptx_inject.MutType.IN,  f"{gname}['{h}'] must be IN"
                    assert group[h].data_type == DataTypeInfo.F32,      f"{gname}['{h}'] must be F32"

            registry = stack_ptx.RegisterRegistry()
            registry.add(multiply['a'].reg,     Stack.f32,  name = "multiply_a")
            registry.add(multiply['b'].reg,     Stack.f32,  name = "multiply_b")
            registry.add(multiply['d'].reg,     Stack.f32,  name = "multiply_d")
            registry.add(multiply['diff'].reg,  Stack.f32,  name = "multiply_diff")
            registry.add(accumulate['c'].reg,  Stack.f32,  name = "accumulate_c")
            registry.add(accumulate['diff'].reg,  Stack.f32,  name = "accumulate_diff")
            registry.add(accumulate['e'].reg,  Stack.f32,  name = "accumulate_e")
            registry.add(epilogue['e'].reg,  Stack.f32,  name = "epilogue_e")

            # Add the register names from the hyper parameters.
            for h in hyper_names:
                registry.add(multiply[h].reg,     Stack.f32, name=f"multiply_{h}")
                registry.add(accumulate[h].reg,   Stack.f32, name=f"accumulate_{h}")
                registry.add(epilogue[h].reg,     Stack.f32, name=f"epilogue_{h}")

            registry.freeze()

            multiply_requests =     [registry.multiply_diff]
            accumulate_requests =   [registry.accumulate_e]
            epilogue_requests =     [registry.epilogue_e]

            def _build_stage_register_dict(stage: str) -> dict[str, object]:
                """
                Map user-provided names to the corresponding stage register *invocations*.
                Example: {"my_beta": registry.multiply_hyper0(), "gamma": registry.multiply_hyper1(), ...}
                """
                out: dict[str, object] = {}
                for i, (user_name, _tensor) in enumerate(hyper_items):
                    attr = f"{stage}_hyper{i}"
                    try:
                        sym = getattr(registry, attr)
                    except AttributeError as e:
                        raise AttributeError(f"Registry missing '{attr}' for hyper index {i}") from e
                    out[user_name] = sym  # call to produce the StackPtxInstruction for this input
                return out

            multiply_register_dict   = _build_stage_register_dict("multiply")
            accumulate_register_dict = _build_stage_register_dict("accumulate")
            epilogue_register_dict   = _build_stage_register_dict("epilogue")

            multiply_instructions = \
                self.multiply_lambda(
                    registry.multiply_d, 
                    registry.multiply_b, 
                    registry.multiply_a,
                    multiply_register_dict
                )
            
            accumulate_instructions = \
                self.accumulate_lambda(
                    registry.accumulate_c, 
                    registry.accumulate_diff, 
                    registry.accumulate_e,
                    accumulate_register_dict
                )
            
            epilogue_instructions = \
                self.epilogue_lambda(
                    registry.epilogue_e,
                    epilogue_register_dict
                )

            multiply_ptx_stub = \
                stack_ptx_compiler.compile(
                    registry=registry,
                    instructions=multiply_instructions, 
                    requests=multiply_requests,
                    execution_limit=self.execution_limit,
                    max_ast_size=self.max_ast_size,
                    max_ast_to_visit_stack_depth=self.max_ast_to_visit_stack_depth,
                    stack_size=self.stack_size,
                    max_frame_depth=self.max_frame_depth
                )
            
            accumulate_ptx_stub = \
                stack_ptx_compiler.compile(
                    registry=registry,
                    instructions=accumulate_instructions, 
                    requests=accumulate_requests,
                    execution_limit=self.execution_limit,
                    max_ast_size=self.max_ast_size,
                    max_ast_to_visit_stack_depth=self.max_ast_to_visit_stack_depth,
                    stack_size=self.stack_size,
                    max_frame_depth=self.max_frame_depth
                )
            
            epilogue_ptx_stub = \
                stack_ptx_compiler.compile(
                    registry=registry,
                    instructions=epilogue_instructions, 
                    requests=epilogue_requests,
                    execution_limit=self.execution_limit,
                    max_ast_size=self.max_ast_size,
                    max_ast_to_visit_stack_depth=self.max_ast_to_visit_stack_depth,
                    stack_size=self.stack_size,
                    max_frame_depth=self.max_frame_depth
                )
            
            ptx_stubs = {
                'multiply':     multiply_ptx_stub,
                'accumulate':   accumulate_ptx_stub,
                'epilogue':     epilogue_ptx_stub,
            }

            rendered_ptx = inject.render_ptx(ptx_stubs)
            
            arch = get_compute_capability(device)
            module_cubin = Program(
                rendered_ptx,
                code_type="ptx", 
                options= \
                    ProgramOptions(
                        arch=f"sm_{arch}",
                        ptxas_options=['-O2', '-v'],
                    )
            ).compile(
                "cubin", 
                logs=sys.stdout,
                name_expressions=[function_name]
            )

            loaded_module = ObjectCode.from_cubin(module_cubin.code)
            symbol_map = {function_name: lowered_name}
            loaded_module._sym_map = symbol_map

            kernel = loaded_module.get_kernel(function_name)

            self.cubin_kernels_dict[dict_key] = kernel

        if debug:
            print(f'(Kermac Debug) Launching kernel: {function_name}')

        num_blocks_M = ceil_div(M, 32)
        num_blocks_N = ceil_div(N, 32)
        num_blocks_O = ceil_div(O, 32)
        num_blocks_L = L

        grid = (num_blocks_L*num_blocks_M, num_blocks_N, num_blocks_O)
        config = LaunchConfig(grid=grid, block=256)

        ld_a = np.uint64(tensor_stats_a.leading_dimension_stride)
        batch_stride_a = np.uint64(tensor_stats_a.batch_stride)

        ld_b = np.uint64(tensor_stats_b.leading_dimension_stride)
        batch_stride_b = np.uint64(tensor_stats_b.batch_stride)

        ld_c = np.uint64(tensor_stats_c.leading_dimension_stride)
        batch_stride_c = np.uint64(tensor_stats_c.batch_stride)

        ld_d = np.uint64(tensor_stats_d.leading_dimension_stride)
        batch_stride_d = np.uint64(tensor_stats_d.batch_stride)

        ld_e_N = np.uint64(out.stride(-2))
        ld_e_O = np.uint64(out.stride(-3)) # outer-most/slowest-moving/left-most stride
        batch_stride_e = np.uint64(0 if L == 1 else out.stride(-4))

        kernel_args = (
            M, N, O, K, L,
            np.int32(num_blocks_M), # Need this to index num_blocks_L by division
            a.data_ptr(),       ld_a,                   batch_stride_a,
            b.data_ptr(),       ld_b,                   batch_stride_b,
            c.data_ptr(),       ld_c,                   batch_stride_c,
            d.data_ptr(),       ld_d,                   batch_stride_d,
            out.data_ptr(),     ld_e_N,     ld_e_O,     batch_stride_e,
        )

        if num_hypers:
            hyper_args = []
            for name, t in hyper_items:
                bs = np.uint64(0 if t.dim() == 0 or t.numel() == 1 else 1)  # scalar -> 0, [L] -> 0
                hyper_args.extend([t.data_ptr(), bs])
            kernel_args = (*kernel_args, *hyper_args)

        launch(stream, config, kernel, *kernel_args)

        return out
