# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

from mm_kermac import Stack, PtxInstruction
from mm_kermac.hyper_semiring import HyperSemiringKernel

import torch

class NormLp:
    def __init__(self, epsilon):
        self.hyper_semiring = \
            HyperSemiringKernel(
                mma_lambda=\
                    lambda reg_a, reg_b, reg_c, reg_dict: [
                        reg_a,
                        reg_b,
                        PtxInstruction.sub_ftz_f32,           # diff = reg_b - reg_a [diff]
                        PtxInstruction.abs_ftz_f32,           # [abs(diff)]

                        # raise to power p_inner
                        PtxInstruction.lg2_approx_ftz_f32,
                        reg_dict['p_inner'],
                        PtxInstruction.mul_ftz_f32,
                        PtxInstruction.ex2_approx_ftz_f32,    # [ex2(p_inner * lg2(abs(diff)))]
                                                                # [pow(abs(diff), p_inner)]
                        reg_c,
                        PtxInstruction.add_ftz_f32
                    ],
                epilogue_lambda=\
                    lambda reg_e, reg_dict: [
                        reg_e,

                        # raise to power p_outer
                        PtxInstruction.lg2_approx_ftz_f32,    #   [lg2(reg_e)]
                        reg_dict['p_outer'],                    #   [p_outer, lg2(reg_e)]
                        PtxInstruction.mul_ftz_f32,           #   [p_outer * lg2(reg_e)]
                        PtxInstruction.ex2_approx_ftz_f32,    #   [ex2(p_outer * lg2(reg_e))]
                                                                #   [pow(reg_e, p_outer)]
                        # if less than epsilon, clamp to 0
                        Stack.f32.store(0),                     # Store pow(reg_e, p_outer)
                        Stack.load(0),                          # Load it here
                        Stack.f32.constant(epsilon),            # [e, pow(reg_e, p_outer)]
                        PtxInstruction.setp_gt_ftz_f32,       # [] : [e > pow(reg_e, p_outer)]
                        Stack.load(0),                          # Load it here too
                        Stack.f32.constant(0.0),                # [0.0, pow(reg_e, p_outer)] : [e > pow(reg_e, p_outer)]
                        PtxInstruction.selp_f32               # [e > pow(reg_e, p_outer) ? 0.0 : pow(reg_e, p_outer)]
                    ]
            )
        
    def __call__(
        self,
        x : torch.Tensor,
        z : torch.Tensor,
        p_inner : torch.Tensor,
        p_outer : torch.Tensor,
        out : torch.Tensor = None,
        try_to_align : bool = False,
        debug = False
    ):
        hyper_dict = {
            'p_inner': p_inner,
            'p_outer': p_outer
        }
        return self.hyper_semiring(
            a = x,
            b = z,
            out = out,
            hyper_dict=hyper_dict,
            try_to_align = try_to_align,
            debug = debug
        )
