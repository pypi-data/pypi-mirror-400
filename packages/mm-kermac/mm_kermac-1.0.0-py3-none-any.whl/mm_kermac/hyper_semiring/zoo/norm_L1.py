# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

from mm_kermac import PtxInstruction
from mm_kermac.hyper_semiring import HyperSemiringKernel

import torch

class NormL1:
    def __init__(self):
        self.hyper_semiring = \
            HyperSemiringKernel(
                mma_lambda=\
                    lambda reg_a, reg_b, reg_c, _: [
                        reg_a,
                        reg_b,
                        PtxInstruction.sub_ftz_f32,
                        PtxInstruction.abs_ftz_f32,
                        reg_c,
                        PtxInstruction.add_ftz_f32
                    ],
                epilogue_lambda=\
                    lambda reg_e, _: [
                        reg_e
                    ]
            )
        
    def __call__(
        self,
        x : torch.Tensor,
        z : torch.Tensor,
        out : torch.Tensor = None,
        try_to_align : bool = False,
        debug = False
    ):
        return self.hyper_semiring(
            a = x,
            b = z,
            out = out,
            hyper_dict=None,
            try_to_align = try_to_align,
            debug = debug
        )
