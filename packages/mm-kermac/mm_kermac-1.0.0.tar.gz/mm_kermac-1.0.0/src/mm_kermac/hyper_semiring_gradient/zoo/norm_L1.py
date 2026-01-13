# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

from mm_kermac import Stack, PtxInstruction
from mm_kermac.hyper_semiring_gradient import HyperSemiringGradientKernel

import torch

class NormL1:
    def __init__(self):
        self.hyper_semiring_gradient = \
            HyperSemiringGradientKernel(
                multiply_lambda=\
                    lambda reg_d, reg_b, reg_a, _: [
                        reg_b,
                        reg_d,
                        PtxInstruction.sub_ftz_f32,
                        Stack.f32.constant(1.0),
                        Stack.f32.swap,
                        PtxInstruction.copysign_f32,
                        reg_a,
                        PtxInstruction.mul_ftz_f32
                    ],
                accumulate_lambda=\
                    lambda reg_c, reg_diff, reg_e, _: [
                        reg_c,
                        reg_diff,
                        PtxInstruction.mul_ftz_f32,
                        reg_e,
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
        coefs : torch.Tensor,
        grad_kernel_matrix : torch.Tensor,
        out : torch.Tensor = None,
        debug = False
    ):
        return self.hyper_semiring_gradient(
            a = grad_kernel_matrix,
            b = x,
            c = coefs,
            d = z,
            hyper_dict=None,
            out = out,
            debug = debug
        )
