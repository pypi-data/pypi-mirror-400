# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

from mm_ptx.stack_ptx import (
    StackTypeEnum, 
    ArgTypeEnum, 
    create_instruction_enum,
    create_special_register_enum,
    StackPtx
)

from enum import auto, unique

@unique
class Stack(StackTypeEnum):
    f32 =   (auto(), "f32")
    s32 =   (auto(), "s32")
    u32 =   (auto(), "u32")
    pred =  (auto(), "pred")

@unique
class ArgType(ArgTypeEnum):
    f32 =   (auto(), Stack.f32,)
    u32 =   (auto(), Stack.u32,)
    pred =  (auto(), Stack.pred,)

@unique
class PtxInstruction(create_instruction_enum(ArgType)):
    copysign_f32 =          (auto(),    "copysign.f32",         [ArgType.f32, ArgType.f32],                 [ArgType.f32])
    add_ftz_f32 =           (auto(),    "add.ftz.f32",          [ArgType.f32, ArgType.f32],                 [ArgType.f32])
    sub_ftz_f32 =           (auto(),    "sub.ftz.f32",          [ArgType.f32, ArgType.f32],                 [ArgType.f32])
    mul_ftz_f32 =           (auto(),    "mul.ftz.f32",          [ArgType.f32, ArgType.f32],                 [ArgType.f32])
    fma_rn_ftz_f32 =        (auto(),    "fma.rn.ftz.f32",       [ArgType.f32, ArgType.f32, ArgType.f32],    [ArgType.f32])
    div_approx_ftz_f32 =    (auto(),    "div.approx.ftz.f32",   [ArgType.f32, ArgType.f32],                 [ArgType.f32])
    abs_ftz_f32 =           (auto(),    "abs.ftz.f32",          [ArgType.f32],                              [ArgType.f32])
    neg_ftz_f32 =           (auto(),    "neg.ftz.f32",          [ArgType.f32],                              [ArgType.f32])
    min_ftz_f32 =           (auto(),    "min.ftz.f32",          [ArgType.f32],                              [ArgType.f32])
    max_ftz_f32 =           (auto(),    "max.ftz.f32",          [ArgType.f32],                              [ArgType.f32])
    
    rcp_approx_ftz_f32 =    (auto(),    "rcp.approx.ftz.f32",   [ArgType.f32],                              [ArgType.f32])
    sqrt_approx_ftz_f32 =   (auto(),    "sqrt.approx.ftz.f32",  [ArgType.f32],                              [ArgType.f32])
    rsqrt_approx_ftz_f32 =  (auto(),    "rsqrt.approx.ftz.f32", [ArgType.f32],                              [ArgType.f32])
    sin_approx_ftz_f32 =    (auto(),    "sin.approx.ftz.f32",   [ArgType.f32],                              [ArgType.f32])
    cos_approx_ftz_f32 =    (auto(),    "cos.approx.ftz.f32",   [ArgType.f32],                              [ArgType.f32])
    lg2_approx_ftz_f32 =    (auto(),    "lg2.approx.ftz.f32",   [ArgType.f32],                              [ArgType.f32])
    ex2_approx_ftz_f32 =    (auto(),    "ex2.approx.ftz.f32",   [ArgType.f32],                              [ArgType.f32])
    tanh_approx_f32 =       (auto(),    "tanh.approx.f32",      [ArgType.f32],                              [ArgType.f32])

    setp_lt_ftz_f32 =       (auto(),    "setp.lt.ftz.f32",      [ArgType.f32, ArgType.f32],                 [ArgType.pred])
    setp_gt_ftz_f32 =       (auto(),    "setp.gt.ftz.f32",      [ArgType.f32, ArgType.f32],                 [ArgType.pred])
    selp_f32 =              (auto(),    "selp.f32",             [ArgType.f32, ArgType.f32,  ArgType.pred],  [ArgType.f32])

@unique
class SpecialRegister(create_special_register_enum(ArgType)):
    clock =     (auto(),    "clock",      ArgType.u32)
    tid_x =     (auto(),    "tid.x",      ArgType.u32)

compiler = \
    StackPtx(
        stack_enum=Stack,
        arg_enum=ArgType,
        ptx_instruction_enum=PtxInstruction, 
        special_register_enum=SpecialRegister
    )