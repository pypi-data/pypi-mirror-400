# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

from mm_kermac import Stack, PtxInstruction
from mm_kermac.hyper_semiring_gradient import HyperSemiringGradientKernel

from enum import IntEnum
import torch

class NormLp:
    def __init__(self, epsilon):
        class Var(IntEnum):
            diff = 0,
            abs_diff = 1,
        
        self.hyper_semiring_gradient = \
            HyperSemiringGradientKernel(
                multiply_lambda=\
                    lambda reg_d, reg_b, reg_a, reg_dict: [
                        reg_b,
                        reg_d,
                        PtxInstruction.sub_ftz_f32,           # diff = [reg_d - reg_b]
                        Stack.f32.store(Var.diff),
                        Stack.load(Var.diff),                   # [diff, diff]
                        PtxInstruction.abs_ftz_f32,           # [abs(diff), diff]
                        Stack.f32.store(Var.abs_diff),

                        # if less than epsilon, clamp to epsilon
                       
                        Stack.load(Var.abs_diff),
                        Stack.f32.constant(epsilon),            # [e, abs(diff)]
                        PtxInstruction.setp_gt_ftz_f32,       # [] : [e > abs(diff)]
                        Stack.load(Var.abs_diff),
                        Stack.f32.constant(epsilon),            # [e, abs(diff)] : [e > abs(diff)]
                        PtxInstruction.selp_f32,              # [clamped_value]

                        # raise to power p_power_grad
                        PtxInstruction.lg2_approx_ftz_f32,
                        reg_dict['p_power_grad'],
                        PtxInstruction.mul_ftz_f32,
                        PtxInstruction.ex2_approx_ftz_f32,    # [pow(clamped_value, p_power_grad)]
                    
                        Stack.load(Var.diff),                   # [diff, pow(clamped_value, p_power_grad]
                        PtxInstruction.copysign_f32,          # [sign(diff) * pow(clamped_value, p_power_grad]
                        reg_a,
                        PtxInstruction.mul_ftz_f32            # [reg_a * sign(diff) * pow(clamped_value, p_power_grad]
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
        p_power_grad : torch.Tensor,
        out : torch.Tensor = None,
        debug = False
    ):
        hyper_dict = {'p_power_grad': p_power_grad}
        return self.hyper_semiring_gradient(
            a = grad_kernel_matrix,
            b = x,
            c = coefs,
            d = z,
            hyper_dict=hyper_dict,
            out = out,
            debug = debug
        )
