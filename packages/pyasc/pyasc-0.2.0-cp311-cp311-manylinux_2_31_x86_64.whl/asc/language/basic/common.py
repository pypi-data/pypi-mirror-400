# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This program is free software, you can redistribute it and/or modify it under the terms and conditions of
# CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import overload

from ..._C import ir
from ..core.dtype import DataType, KnownTypes, KnownTypes as KT
from ..core.enums import MaskMode, TPosition
from ..core.ir_value import GlobalAddress, PlainValue, materialize_ir_value as _mat, RuntimeBool, RuntimeInt
from ..core.tensor import LocalTensor, GlobalTensor
from ..core.aipp_types import AippParams
from ..core.enums import AippInputFormat
from ..core.utils import require_jit, global_builder, OverloadDispatcher
from .utils import set_common_docstring


@require_jit
def ascend_is_aic() -> PlainValue:
    builder = global_builder.get_ir_builder()
    handle = builder.create_asc_AscendIsAICOp(builder.get_i1_type())
    return PlainValue(handle)


@require_jit
def ascend_is_aiv() -> PlainValue:
    builder = global_builder.get_ir_builder()
    handle = builder.create_asc_AscendIsAIVOp(builder.get_i1_type())
    return PlainValue(handle)


@require_jit
@set_common_docstring(api_name="get_hccl_context")
def get_hccl_context(index: int) -> GlobalAddress:
    builder = global_builder.get_ir_builder()
    idx_ir = _mat(index, KnownTypes.uint32).to_ir()
    ir_type = ir.get_memref_type(builder.get_ui8_type(), [ir.dynshape], ir.AddressSpace.gm)
    return GlobalAddress(builder.create_asc_GetHcclContextOp(ir_type, idx_ir), KnownTypes.uint8)


@require_jit
@set_common_docstring(api_name="get_sys_workspace")
def get_sys_workspace() -> GlobalAddress:
    builder = global_builder.get_ir_builder()
    ir_type = ir.get_memref_type(builder.get_ui8_type(), [ir.dynshape], ir.AddressSpace.gm)
    return GlobalAddress(builder.create_asc_GetSysWorkspacePtrOp(ir_type), KnownTypes.uint8)


@require_jit
def pop_stack_buffer(dtype: DataType, position: TPosition = TPosition.VECCALC) -> LocalTensor:
    builder = global_builder.get_ir_builder()
    handle = builder.create_asc_LocalTensorOp(ir.get_local_tensor_type(dtype.to_ir()))
    tensor = LocalTensor(handle, dtype, shape=None)
    builder.create_asc_PopStackBufferOp(ir.TPosition.symbolize(position), tensor.to_ir())
    return tensor


@require_jit
def reset_mask() -> None:
    builder = global_builder.get_ir_builder()
    builder.create_asc_ResetMaskOp()


@overload
def set_aipp_functions(src0: GlobalTensor, input_format: AippInputFormat, config: AippParams) -> None:
    ...


@overload
def set_aipp_functions(src0: GlobalTensor, src1: GlobalTensor, 
                        input_format: AippInputFormat, config: AippParams) -> None:
    ...


@require_jit
@set_common_docstring(api_name="set_aipp_functions")
def set_aipp_functions(*args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    dispatcher = OverloadDispatcher(set_aipp_functions)

    @dispatcher.register_auto
    def _(src0: GlobalTensor, src1: GlobalTensor, input_format: AippInputFormat, config: AippParams):
        builder.create_asc_SetAippFunctionsOp(
            src0.to_ir(), src1.to_ir(), ir.AippInputFormat.symbolize(input_format), config.to_ir())

    @dispatcher.register_auto
    def _(src0: GlobalTensor, input_format: AippInputFormat, config: AippParams):
        builder.create_asc_SetAippFunctionsOp(
            src0.to_ir(), None, ir.AippInputFormat.symbolize(input_format), config.to_ir())

    dispatcher(*args, **kwargs)


@overload
def set_fix_pipe_pre_quant_flag(config: int) -> None:
    ...


@require_jit
@set_common_docstring("set_fix_pipe_pre_quant_flag")
def set_fix_pipe_pre_quant_flag(config: RuntimeInt) -> None:
    builder = global_builder.get_ir_builder()
    builder.create_asc_SetFixpipePreQuantFlagOp(_mat(config, KT.uint64).to_ir())


@overload
@require_jit
def set_hccl_context(index: int, context: GlobalAddress) -> None:
    ...


@require_jit
@set_common_docstring(api_name="set_hccl_context")
def set_hccl_context(index: RuntimeInt, context: GlobalAddress) -> None:
    builder = global_builder.get_ir_builder()
    idx_ir = _mat(index, KnownTypes.uint32).to_ir()
    builder.create_asc_SetHcclContextOp(idx_ir, context.to_ir())


@overload
def set_hf32_mode(hf32_mode: bool) -> None:
    ...


@require_jit
@set_common_docstring(api_name="set_hf32_mode")
def set_hf32_mode(hf32_mode: RuntimeBool) -> None:
    builder = global_builder.get_ir_builder()
    hf32_mode = _mat(hf32_mode)
    builder.create_asc_SetHF32ModeOp(hf32_mode.to_ir())


@overload
def set_hf32_trans_mode(trans_mode: bool) -> None:
    ...


@require_jit
@set_common_docstring(api_name="set_hf32_trans_mode")
def set_hf32_trans_mode(trans_mode: RuntimeBool) -> None:
    builder = global_builder.get_ir_builder()
    trans_mode = _mat(trans_mode)
    builder.create_asc_SetHF32TransModeOp(trans_mode.to_ir())


@overload
def set_mm_layout_transform(mm_layout_mode: bool) -> None:
    ...


@require_jit
@set_common_docstring(api_name="set_mm_layout_transform")
def set_mm_layout_transform(mm_layout_mode: RuntimeBool) -> None:
    builder = global_builder.get_ir_builder()
    mm_layout_mode = _mat(mm_layout_mode)
    builder.create_asc_SetMMLayoutTransformOp(mm_layout_mode.to_ir())


@overload
def set_mask_count() -> None:
    ...


@require_jit
@set_common_docstring(api_name="set_mask_count")
def set_mask_count() -> None:
    builder = global_builder.get_ir_builder()
    builder.create_asc_SetMaskCountOp()


@overload
def set_mask_norm() -> None:
    ...


@require_jit
@set_common_docstring(api_name="set_mask_norm")
def set_mask_norm() -> None:
    builder = global_builder.get_ir_builder()
    builder.create_asc_SetMaskNormOp()


@require_jit
def set_sys_workspace(workspace: GlobalAddress) -> None:
    global_builder.get_ir_builder().create_asc_SetSysWorkspaceOp(workspace.to_ir())


@overload
def set_vector_mask(length: int, dtype: DataType, mode: MaskMode) -> None: 
    ...


@overload
def set_vector_mask(mask_high: int, mask_low: int, dtype: DataType, 
                    mode: MaskMode) -> None: 
    ...


@require_jit
@set_common_docstring("set_vector_mask")
def set_vector_mask(*args, dtype: DataType, mode: MaskMode) -> None:
    builder = global_builder.get_ir_builder()
    dispatcher = OverloadDispatcher("set_vector_mask")

    @dispatcher.register_auto
    def _(length: RuntimeInt, dtype: DataType, mode: MaskMode):
        builder.create_asc_SetVectorMaskL0Op(
            _mat(length, KT.int32).to_ir(),
            dtype.to_ir(),
            ir.MaskMode.symbolize(mode)
        )

    @dispatcher.register_auto
    def _(mask_high: RuntimeInt, mask_low: RuntimeInt, dtype: DataType, mode: MaskMode):
        builder.create_asc_SetVectorMaskL1Op(
            _mat(mask_high, KT.uint64).to_ir(),
            _mat(mask_low, KT.uint64).to_ir(),
            dtype.to_ir(),
            ir.MaskMode.symbolize(mode)
        )

    dispatcher(*args, dtype=dtype, mode=mode)
