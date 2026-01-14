# Copyright (c) 2025 AISS Group, Harbin Institute of Technology.
# This program is free software, you can redistribute it and/or modify it under the terms and conditions of
# CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import List, overload
from ..core.ir_value import RuntimeBool, RuntimeInt, materialize_ir_value as _mat
from ..core.tensor import LocalTensor, MrgSortSrcList
from ..core.types import KnownTypes, MrgSort4Info
from ..core.utils import DefaultValued, require_jit, global_builder, OverloadDispatcher
from .utils import set_common_docstring


@overload
def mrg_sort(dst: LocalTensor, sort_list: MrgSortSrcList, element_count_list: List[int],
             sorted_num: List[int], valid_bit: int, repeat_time: int,
             is_exhausted_suspension: bool = False) -> None:
    ...


@overload
def mrg_sort(dst: LocalTensor, sort_list: MrgSortSrcList, params: MrgSort4Info) -> None:
    ...


@require_jit
@set_common_docstring(api_name="mrg_sort")
def mrg_sort(dst: LocalTensor, sort_list: MrgSortSrcList, *args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    dispatcher = OverloadDispatcher("mrg_sort")

    @dispatcher.register(element_count_list=List[int], sorted_num=List[int], valid_bit=RuntimeInt,
          repeat_time=RuntimeInt, is_exhausted_suspension=DefaultValued(RuntimeBool, False))
    def _(element_count_list: List[int], sorted_num: List[int], valid_bit: RuntimeInt,
          repeat_time: RuntimeInt, is_exhausted_suspension: bool = False):
        
        if is_exhausted_suspension not in (True, False):
            raise TypeError(
                f"The 'is_exhausted_suspension' argument must be a boolean literal (True or False), "
                f"but got {is_exhausted_suspension} of type {type(is_exhausted_suspension).__name__}. "
                f"This parameter must be a compile-time constant."
            )

        element_count_list_ir = [_mat(count, KnownTypes.uint16).to_ir() for count in element_count_list]
        sorted_num_ir = [_mat(num, KnownTypes.uint32).to_ir() for num in sorted_num]
        
        builder.create_asc_MrgSortOp(
            dst.to_ir(), sort_list.to_ir(),
            element_count_list_ir,
            sorted_num_ir,
            _mat(valid_bit, KnownTypes.uint16).to_ir(),
            _mat(repeat_time, KnownTypes.uint16).to_ir(),
            is_exhausted_suspension
        )

    @dispatcher.register(params=MrgSort4Info)
    def _(params: MrgSort4Info):
        builder.create_asc_MrgSortWithInfoOp(dst.to_ir(), sort_list.to_ir(), params.to_ir())

    dispatcher(*args, **kwargs)


@require_jit
@set_common_docstring(api_name="mrg_sort4")
def mrg_sort4(dst: LocalTensor, src: MrgSortSrcList, params: MrgSort4Info) -> None:
    builder = global_builder.get_ir_builder()
    builder.create_asc_MrgSort4Op(dst.to_ir(), src.to_ir(), params.to_ir())


@overload
def proposal_concat(dst: LocalTensor, src: LocalTensor, repeat_time: int, mode_number: int) -> None:
    ...


@require_jit
@set_common_docstring(api_name="proposal_concat")
def proposal_concat(dst: LocalTensor, src: LocalTensor, repeat_time: RuntimeInt, mode_number: RuntimeInt) -> None:
    global_builder.get_ir_builder().create_asc_ProposalConcatOp(dst.to_ir(), src.to_ir(),
                                                                _mat(repeat_time).to_ir(), _mat(mode_number).to_ir())


@overload
def proposal_extract(dst: LocalTensor, src: LocalTensor, repeat_time: int, mode_number: int) -> None:
    ...


@require_jit
@set_common_docstring(api_name="proposal_extract")
def proposal_extract(dst: LocalTensor, src: LocalTensor, repeat_time: RuntimeInt, mode_number: RuntimeInt) -> None:
    global_builder.get_ir_builder().create_asc_ProposalExtractOp(dst.to_ir(), src.to_ir(),
                                                                 _mat(repeat_time).to_ir(), _mat(mode_number).to_ir())


@overload
def rp_sort16(dst: LocalTensor, src: LocalTensor, repeat_time: int) -> None:
    ...


@require_jit
@set_common_docstring(api_name="rp_sort16")
def rp_sort16(dst: LocalTensor, src: LocalTensor, repeat_time: RuntimeInt) -> None:
    builder = global_builder.get_ir_builder()
    builder.create_asc_RpSort16Op(
        dst.to_ir(),
        src.to_ir(),
        _mat(repeat_time, KnownTypes.int32).to_ir()
    )


@overload
def sort(dst: LocalTensor, concat: LocalTensor, index: LocalTensor, tmp: LocalTensor, repeat_time: int) -> None:
    ...


@require_jit
@set_common_docstring(api_name="sort")
def sort(dst: LocalTensor, concat: LocalTensor, index: LocalTensor, tmp: LocalTensor, repeat_time: RuntimeInt,
          is_full_sort: bool = False) -> None:
    
    if is_full_sort not in (True, False):
        raise TypeError(
            f"The 'is_full_sort' argument must be a boolean literal (True or False), "
            f"but got {is_full_sort} of type {type(is_full_sort).__name__}. "
            f"This parameter must be a compile-time constant."
        )
    
    builder = global_builder.get_ir_builder()
    builder.create_asc_SortOp(
            dst.to_ir(),
            concat.to_ir(),
            index.to_ir(),
            tmp.to_ir(),
            _mat(repeat_time, KnownTypes.int32).to_ir(),
            is_full_sort
        )


@overload
def sort32(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, repeat_time: int) -> None:
    ...


@require_jit
@set_common_docstring(api_name="sort32")
def sort32(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, repeat_time: RuntimeInt) -> None:
    builder = global_builder.get_ir_builder()
    builder.create_asc_Sort32Op(
        dst.to_ir(),
        src0.to_ir(),
        src1.to_ir(),
        _mat(repeat_time, KnownTypes.int32).to_ir()
    )