# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This program is free software, you can redistribute it and/or modify it under the terms and conditions of
# CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import List, overload, Optional

from ..core.dtype import KnownTypes
from ..core.ir_value import RuntimeBool, RuntimeInt, RuntimeFloat, materialize_ir_value as _mat
from ..core.tensor import LocalTensor
from ..core.utils import require_jit, global_builder
from ..core.types import BinaryRepeatParams, UnaryRepeatParams
from .utils import op_impl, set_binary_docstring, set_common_docstring
from .vec_unary import op_impl as unary_op_impl


@overload
def add_relu_cast(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, count: int) -> None:
    ...


@overload
def add_relu_cast(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, mask: int, repeat_times: int,
                  repeat_params: BinaryRepeatParams, is_set_mask: bool = True) -> None:
    ...


@overload
def add_relu_cast(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, mask: List[int], repeat_times: int,
                  repeat_params: BinaryRepeatParams, is_set_mask: bool = True) -> None:
    ...


@require_jit
@set_binary_docstring(cpp_name="AddReluCast", append_text="按元素求和，结果和0对比取较大值，并根据源操作数和目的操作数Tensor的数据类型进行精度转换。")
def add_relu_cast(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, *args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    op_impl("add_relu_cast", dst, src0, src1, args, kwargs, builder.create_asc_AddReluCastL0Op,
            builder.create_asc_AddReluCastL1Op, builder.create_asc_AddReluCastL2Op)


@overload
def cast_deq(dst: LocalTensor, src: LocalTensor, count: int, is_vec_deq: bool = True, half_block: bool = True) -> None:
    ...


@overload
def cast_deq(dst: LocalTensor, src: LocalTensor, mask: int, repeat_times: int, repeat_params: UnaryRepeatParams,
            is_set_mask: bool = True, is_vec_deq: bool = True, half_block: bool = True) -> None:
    ...


@overload
def cast_deq(dst: LocalTensor, src: LocalTensor, mask: List[int], repeat_times: int, repeat_params: UnaryRepeatParams,
            is_set_mask: bool = True, is_vec_deq: bool = True, half_block: bool = True) -> None:
    ...


@require_jit
def cast_deq(dst: LocalTensor, src: LocalTensor, *args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    unary_op_impl("cast_deq", dst, src, args, kwargs, builder.create_asc_CastDeqL0Op, 
                  builder.create_asc_CastDeqL1Op, builder.create_asc_CastDeqL2Op)


@overload
def set_deq_scale(scale: float) -> None:
    ...


@overload
def set_deq_scale(scale: float, offset: int, sign_mode: bool) -> None:
    ...


@require_jit
@set_common_docstring(api_name="set_deq_scale")
def set_deq_scale(scale: RuntimeFloat, offset: Optional[RuntimeInt] = None, 
                    sign_mode: Optional[RuntimeBool] = None) -> None:
    if offset is None and sign_mode is None:
        global_builder.get_ir_builder().create_asc_SetDeqScaleOp(_mat(scale, KnownTypes.half).to_ir())
    else:
        global_builder.get_ir_builder().create_asc_SetDeqScaleOp(_mat(scale, KnownTypes.float32).to_ir(), \
            _mat(offset, KnownTypes.int16).to_ir(), _mat(sign_mode, KnownTypes.bit).to_ir())


@overload
def sub_relu_cast(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, count: int) -> None:
    ...


@overload
def sub_relu_cast(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, mask: int, repeat_times: int,
                  repeat_params: BinaryRepeatParams, is_set_mask: bool = True) -> None:
    ...


@overload
def sub_relu_cast(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, mask: List[int], repeat_times: int,
                  repeat_params: BinaryRepeatParams, is_set_mask: bool = True) -> None:
    ...


@require_jit
@set_binary_docstring(cpp_name="SubReluCast", append_text="按元素求差，结果和0对比取较大值，并根据源操作数和目的操作数Tensor的数据类型进行精度转换。")
def sub_relu_cast(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, *args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    op_impl("sub_relu_cast", dst, src0, src1, args, kwargs, builder.create_asc_SubReluCastL0Op,
            builder.create_asc_SubReluCastL1Op, builder.create_asc_SubReluCastL2Op)
