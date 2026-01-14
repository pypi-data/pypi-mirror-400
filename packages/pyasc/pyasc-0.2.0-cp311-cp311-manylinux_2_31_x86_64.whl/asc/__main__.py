# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This program is free software, you can redistribute it and/or modify it under the terms and conditions of
# CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

import argparse
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin

from asc.common.compat import get_annotations
from asc.language.core.dtype import DataType
from asc.language.core.constexpr import ConstExpr
from asc.runtime import config as runtime_config
from asc.runtime.compiler import Compiler
from asc.runtime.jit import JITFunction, MockTensor, MockValue


def parse_args() -> argparse.Namespace:
    version = "version undefined"
    try:
        version = importlib.metadata.version("pyasc")
    except importlib.metadata.PackageNotFoundError:
        pass
    parser = argparse.ArgumentParser("pyasc", description="PyAsc compilation tool")
    parser.add_argument("-e", "--emit", default="ascendc", choices=["codegen", "ir", "ascendc"],
                        help="Emission flow (default: %(default)s)")
    parser.add_argument("--kernel", default=None, help="JIT kernel function name")
    parser.add_argument("-p", "--platform", type=runtime_config.Platform, default="Ascend910B1",
                        help="Runtime platform name (default: %(default)s)")
    parser.add_argument("--args", nargs="+", help="Runtime argument type: name=dtype (or *dtype for tensors)")
    parser.add_argument("--constexprs", nargs="+", help="ConstExpr argument value: name=value")
    parser.add_argument("-v", "--version", action="version", version=version)
    parser.add_argument("-o", "--output", default="-", help="Output file (default: %(default)s)")
    parser.add_argument("--no-binary", action="store_true", help="Disable binary compilation")
    parser.add_argument("input", help="Input file")
    return parser.parse_args()


def warning(*args) -> None:
    print("[WARNING]", *args, file=sys.stderr)


def fatal_error(*args, exit_code=1) -> None:
    print("[ERROR]", *args, file=sys.stderr)
    sys.exit(exit_code)


def load_kernel(filename: str, kernel_name: Optional[str] = None) -> Optional[JITFunction]:
    spec = importlib.util.spec_from_file_location("_pyasc_module", filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if kernel_name is not None:
        return getattr(module, kernel_name, None)
    for var in vars(module).values():
        if isinstance(var, JITFunction):
            return var
    return None


def populate_runtime_args(arg_defs: List[str], args: Dict[str, Any]) -> None:
    arg_defs = arg_defs or []
    for arg_def in arg_defs:
        name, dtype = (s.strip() for s in arg_def.split("=", maxsplit=1))
        if dtype[0] == "*":
            args[name] = MockTensor(DataType(dtype[1:]))
        else:
            args[name] = MockValue(DataType(dtype))


def populate_constexprs(constexpr_defs: List[str], annotations: Dict[str, Any], args: Dict[str, Any]) -> None:
    constexpr_types: Dict[str, Union[Type[int], Type[float]]] = {}
    for name, ann_type in annotations.items():
        if not issubclass(get_origin(ann_type) or ann_type, ConstExpr):
            continue
        ann_args = get_args(ann_type)
        if len(ann_args) != 1:
            raise RuntimeError(f"ConstExpr annotation of argument '{name}' must have explicit type")
        supported_types = (int, float, bool, str, None, dict, list, tuple)
        constraint = ann_args[0]
        if constraint not in supported_types:
            raise RuntimeError(f"ConstExpr annotation of argument '{name}' must be one of {supported_types}")
        constexpr_types[name] = constraint
    constexpr_defs = constexpr_defs or []
    for ce_def in constexpr_defs:
        name, value = (s.strip() for s in ce_def.split("=", maxsplit=1))
        args[name] = ConstExpr(constexpr_types[name](json.loads(value)))


def mock() -> None:

    def mock_set_platform(*args, **kwargs) -> None:
        warning("Runtime configuration is disabled")
        pass

    def mock_run_launcher(*args, **kwargs) -> None:
        pass

    def mock_run_compilation(*args, **kwargs) -> None:
        pass

    def mock_run_translation(*args, **kwargs) -> str:
        return ""

    runtime_config.set_platform = mock_set_platform
    JITFunction._run_launcher = mock_run_launcher
    Compiler.run_compilation = mock_run_compilation
    Compiler.run_translation = mock_run_translation


def set_platform(platform: Union[runtime_config.Platform, str]) -> None:
    runtime_config.active_platform = runtime_config.Platform(platform)


def main() -> int:
    args = parse_args()
    mock()
    set_platform(args.platform)
    kernel_fn = load_kernel(args.input, args.kernel)
    if kernel_fn is None:
        fatal_error("JIT kernel function is not found")
    kernel_args: Dict[str, Any] = {}
    if args.args:
        populate_runtime_args(args.args, kernel_args)
    if args.constexprs:
        populate_constexprs(args.constexprs, get_annotations(kernel_fn.fn), kernel_args)
    kernel_args["always_compile"] = True
    if "codegen" in args.emit:
        kernel_args["run_passes"] = False
    with tempfile.TemporaryDirectory(prefix="pyasc_cli_") as tmpdir:
        os.environ["PYASC_DUMP_PATH"] = tmpdir
        kernel_fn[1](**kernel_args)
        tmpdir = Path(tmpdir)
        filename = {
            "codegen": "codegen.mlir",
            "ir": "ascir.mlir",
            "ascendc": "ascendc.cpp",
        }[args.emit]
        output = (tmpdir / filename).read_text()
        if args.output == "-":
            print(output)
        else:
            Path(args.output).write_text(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
