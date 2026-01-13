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

class HyperSemiringKernel():
    def __init__(
        self,
        mma_lambda,
        epilogue_lambda,
        execution_limit=100,
        max_ast_size=100,
        max_ast_to_visit_stack_depth=20,
        stack_size=128,
        max_frame_depth=4
    ):
        self.mma_lambda = mma_lambda
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
        majorness_A,
        majorness_B,
        align_A,
        align_B,
    ):
        kernel_name_str = f'cute_hyper_semiring_{num}'
        template_parameters = [
            f'Majorness::{majorness_A.name}',
            f'Majorness::{majorness_B.name}',
            f'Alignment::{align_A.name}',
            f'Alignment::{align_B.name}'
        ]
        function_name = f'{kernel_name_str}<{",".join(template_parameters)}>'
        return function_name
    
    def _create_hyper_semiring_template(
        self,
        num : int
    ):
        template_source_file = get_local_cuda_kernel_dir() / 'template_hyper_semiring.cuh'

        with open(template_source_file, "r") as f:
            content = f.read()
            num_sites = 11

            def _ptx_in_block(indent: int) -> str:
                if num == 0:
                    return ""
                return "".join(
                    f",\n{' ' * indent}PTX_IN(F32, hyper{i})" for i in range(num)
                )

            mma_hypers = _ptx_in_block(24)
            epilogue_hypers = _ptx_in_block(12)
            
            templates = [
                "\n\t".join(f"class HYPER{i}Stride," for i in range(num)),
                f"{num}",
                "\n\t".join(f", T* HYPER{i}, HYPER{i}Stride dHYPER{i}" for i in range(num)),
                "\n\t".join(f" Tensor mHYPER{i} = make_tensor(make_gmem_ptr(HYPER{i}), select<3>(shape_MNKL), dHYPER{i});" for i in range(num)),
                "\n\t".join(f"T hyper{i} = mHYPER{i}(bidz);" for i in range(num)),
                mma_hypers,
                "",
                epilogue_hypers,
                "\n\t".join(f", float *hyper{i},    uint64_t batch_stride_hyper{i}" for i in range(num)),
                "\n\t".join(f"auto d_hyper{i} = make_stride(batch_stride_hyper{i});" for i in range(num)),
                "\n\t\t".join(f", hyper{i}, d_hyper{i}" for i in range(num)),
            ]

            for i in range(num_sites):
                content = content.replace(f"@{i}@", templates[i])

            # # Prints the generated template
            # with open(get_top_level_repo_dir('') / f'rendered_hyper_semiring_{num}.cuh', 'w') as file:
            #     file.write(content)

            return content
    
    def __call__(
        self,
        a : torch.Tensor,
        b : torch.Tensor,
        hyper_dict : dict[str, torch.Tensor] = None,
        out : torch.Tensor = None,
        try_to_align : bool = False,
        debug = False
    ):
        L = 1
        L = merge_batch_size('a', L, a, expected_dims=2, can_be_none=False)
        L = merge_batch_size('b', L, b, expected_dims=2, can_be_none=False)
        L = merge_batch_size('out', L, out, expected_dims=2, can_be_none=True)
            
        # Check if inputs are tensors
        if not isinstance(a, torch.Tensor) or not isinstance(b, torch.Tensor):
            raise TypeError("a and b must be PyTorch tensors")
        if out is not None and not isinstance(out, torch.Tensor):
            raise TypeError("out must be a PyTorch tensor if provided")

        # Check dtype
        if a.dtype != torch.float32 or b.dtype != torch.float32:
            raise TypeError("a and b must have dtype torch.float32")
        if out is not None and out.dtype != torch.float32:
            raise TypeError("out must have dtype torch.float32")

        # Check CUDA device
        if not a.is_cuda or not b.is_cuda:
            raise ValueError("a and b must be on a CUDA device")
        if out is not None and not out.is_cuda:
            raise ValueError("out must be on a CUDA device")
        
        tensor_device = a.device
        if not all(x.device == tensor_device for x in (a, b)):
            raise ValueError(f"All inputs must be on the same CUDA device: got {[x.device for x in (a, b)]}")
        if out is not None and out.device != tensor_device:
            raise ValueError(f"out must be on the same CUDA device as inputs: got {out.device}, expected {tensor_device}")

        # NEW: fold hyper_dict into L and validate each tensor
        L, hyper_items = self._validate_and_collect_hypers(hyper_dict, L, tensor_device)
        num_hypers = len(hyper_items)

        tensor_stats_a = tensor_stats(a)
        tensor_stats_b = tensor_stats(b)

        # Get shapes
        _, M, K_a = tensor_stats_a.shape
        _, N, K_b = tensor_stats_b.shape

        # Check shape consistency
        if K_a != K_b:
            raise ValueError(f"K dimensions must match: got {K_a} for a and {K_b} for b")
        
        K = K_a
        
        if out is not None:
            L_c = 1 if out.dim() == 2 else out.size(0)
            tensor_stats_c = tensor_stats(out)
            _, M_c, N_c = tensor_stats_c.shape
            if (M_c, N_c) != (M,N):
                raise ValueError(f"out must have shape (M={M}, N={N}), got {(M_c, N_c)}")
            if L_c != L and L != 1:
                raise ValueError(f"out must have batch dimension (L={L}), got {(L_c)}")
        else:
            out = torch.zeros((L, M, N), dtype=torch.float32, device=tensor_device)
            tensor_stats_c = tensor_stats(out)
    
        pt_stream = torch.cuda.current_stream()
        pt_device = pt_stream.device
        device = Device(pt_device.index)
        device.set_current()
        stream = Stream.from_handle(int(pt_stream.cuda_stream))

        if tensor_device != pt_device:
            raise ValueError("cuda stream must be on the same device as the tensors: got {pt_device}, expected {tensor_device}")
        
        if tensor_stats_c.majorness == Majorness.ROW_MAJOR:
            # Swap arguments if output tensor is row major
            # Kernel will dispatch to version with output as col major
            temp_M = M
            M = N
            N = temp_M

            temp_a = a
            a = b
            b = temp_a
            
            temp_tensor_stats_a = tensor_stats_a
            tensor_stats_a = tensor_stats_b
            tensor_stats_b = temp_tensor_stats_a

        align_4_A = Alignment.ALIGN_1 if not try_to_align else tensor_stats_a.alignment
        align_4_B = Alignment.ALIGN_1 if not try_to_align else tensor_stats_b.alignment

        function_name = self._render_function_name(num_hypers,tensor_stats_a.majorness, tensor_stats_b.majorness, align_4_A, align_4_B)
        dict_key = device, function_name
        kernel = None
        if (dict_key in self.cubin_kernels_dict):
            # We found the kernel already loaded for this majorness and alignment
            # (With the same injected PTX)
            kernel = self.cubin_kernels_dict[dict_key]
        else:
            def get_cuda_source_lambda():
                return self._create_hyper_semiring_template(num_hypers)
            # We did not find the kernel for this majorness and alignment
            # and number of hyper parameters requested.
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

            mma = inject['mma']
            epilogue = inject['epilogue']

            assert( mma['a'].mut_type == ptx_inject.MutType.IN)
            assert( mma['a'].data_type == DataTypeInfo.F32)

            assert( mma['b'].mut_type == ptx_inject.MutType.IN)
            assert( mma['b'].data_type == DataTypeInfo.F32)

            assert( mma['c'].mut_type == ptx_inject.MutType.MOD)
            assert( mma['c'].data_type == DataTypeInfo.F32)

            assert( epilogue['e'].mut_type == ptx_inject.MutType.MOD)
            assert( epilogue['e'].data_type == DataTypeInfo.F32)

            # assert the types for each hyper parameter found in the inject.
            hyper_names = [f"hyper{i}" for i in range(num_hypers)]
            for h in hyper_names:
                for group, gname in (
                    (mma, "mma"),
                    (epilogue, "epilogue")
                ):
                    assert group[h].mut_type == ptx_inject.MutType.IN,  f"{gname}['{h}'] must be IN"
                    assert group[h].data_type == DataTypeInfo.F32,      f"{gname}['{h}'] must be F32"

            registry = stack_ptx.RegisterRegistry()
            # Add the regular register names to the registry.
            registry.add(mma['a'].reg,              Stack.f32, name='mma_a')
            registry.add(mma['b'].reg,              Stack.f32, name='mma_b')
            registry.add(mma['c'].reg,              Stack.f32, name='mma_c')
            registry.add(epilogue['e'].reg,         Stack.f32, name='epilogue_e')

            # Add the register names from the hyper parameters.
            for h in hyper_names:
                registry.add(mma[h].reg,          Stack.f32, name=f"mma_{h}")
                registry.add(epilogue[h].reg,     Stack.f32, name=f"epilogue_{h}")

            registry.freeze()

            mma_requests =          [registry.mma_c]
            epilogue_requests =     [registry.epilogue_e]

            def _build_stage_register_dict(stage: str) -> dict[str, object]:
                """
                Map user-provided names to the corresponding stage register *invocations*.
                Example: {"my_beta": registry.mma_hyper0(), "gamma": registry.mma_hyper1(), ...}
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

            mma_register_dict        = _build_stage_register_dict("mma")
            epilogue_register_dict   = _build_stage_register_dict("epilogue")

            mma_instructions = \
                self.mma_lambda(
                    registry.mma_a,
                    registry.mma_b,
                    registry.mma_c,
                    mma_register_dict
                )

            epilogue_instructions = \
                self.epilogue_lambda(
                    registry.epilogue_e,
                    epilogue_register_dict
                )

            mma_ptx_stub = \
                stack_ptx_compiler.compile(
                    registry=registry,
                    instructions=mma_instructions, 
                    requests=mma_requests,
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
                'mma':          mma_ptx_stub,
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

        num_blocks_M = ceil_div(M, 128)
        num_blocks_N = ceil_div(N, 128)
        num_batches = L

        grid = (num_blocks_M, num_blocks_N, num_batches)
        config = LaunchConfig(grid=grid, block=256)

        ld_a = np.uint64(tensor_stats_a.leading_dimension_stride)
        batch_stride_a = np.uint64(tensor_stats_a.batch_stride)

        ld_b = np.uint64(tensor_stats_b.leading_dimension_stride)
        batch_stride_b = np.uint64(tensor_stats_b.batch_stride)

        ld_c = np.uint64(tensor_stats_c.leading_dimension_stride)
        batch_stride_c = np.uint64(tensor_stats_c.batch_stride)

        kernel_args = (
            M, N, K, L,
            a.data_ptr(),       ld_a,   batch_stride_a,
            b.data_ptr(),       ld_b,   batch_stride_b,
            out.data_ptr(),     ld_c,   batch_stride_c
        )

        if num_hypers:
            hyper_args = []
            for name, t in hyper_items:
                bs = np.uint64(0 if t.dim() == 0 or t.numel() == 1 else 1)  # scalar -> 0, [L] -> 0
                hyper_args.extend([t.data_ptr(), bs])
            kernel_args = (*kernel_args, *hyper_args)

        launch(stream, config, kernel, *kernel_args)

        return out
