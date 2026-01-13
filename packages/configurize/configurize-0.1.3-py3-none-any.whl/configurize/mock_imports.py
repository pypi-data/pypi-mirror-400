"""
mock_imports —— Python 模块导入自动 mock 工具
========================================

【工具简介】
    mock_imports 是一个用于 Python 单元测试、CI、依赖隔离等场景的自动模块 mock 工具。

【主要功能】
    - mock_imports(patterns, auto_mock_missing=True, auto_mock_ignore_patterns=None)
        - patterns: List[str]，需要 mock 的模块名或通配符列表（如 ["torch*", "myproject.utils*"]）。
        - auto_mock_missing: bool，是否自动 mock 所有不存在的库（即使未在 patterns 中匹配），默认 True。
        - auto_mock_ignore_patterns: List[str]，自动 mock 时忽略的模块名/通配符列表。
    - 被 mock 的模块会变为 MagicMock 实例，行为与真实模块不同，仅用于测试隔离。
    - patterns 支持 fnmatch 通配符语法，支持子模块递归。
    - 自动 mock 不存在的库时，**若 import 语句在捕获 ImportError 的 try except 块中**，则不会 mock，正常抛出 ImportError。

【典型用法】
    from mock_imports import mock_imports
    with mock_imports(["torch*"]):
        import torch
        import torch.nn as nn
        import not_exist_lib  # 若 auto_mock_missing=True，将被自动 mock
        print(torch, nn, not_exist_lib)
"""

# mock_manager.py

import fnmatch
import importlib.util
import sys
from contextlib import contextmanager
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from unittest.mock import MagicMock


class MockLoader(Loader):
    """一个自定义加载器，它不加载模块，而是返回一个 MagicMock。"""

    def create_module(self, spec):
        """创建并返回 MagicMock 对象作为模块。"""
        mock_module = MagicMock(name=spec.name)
        mock_module.__name__ = spec.name
        mock_module.__path__ = []  # 支持子模块导入
        sys.modules[spec.name] = mock_module
        return mock_module

    def exec_module(self, module):
        """不需要执行任何模块代码。"""
        pass


class PatternMockFinder(MetaPathFinder):
    """只拦截 patterns 匹配的模块。"""

    def __init__(self, patterns):
        self.patterns = patterns
        self._loader = MockLoader()
        self.matches = {}

    def find_spec(self, fullname, path, target=None):
        for pattern in self.patterns:
            if fnmatch.fnmatch(fullname, pattern):
                self.matches[fullname] = sys.modules.get(fullname)
                return ModuleSpec(fullname, self._loader)
        return None


class AutoMockMissingFinder(MetaPathFinder):
    """只兜底 mock 不存在的库。"""

    def __init__(self, ignore_patterns=None):
        self.ignore_patterns = ignore_patterns
        self._loader = MockLoader()
        self.matches = {}

    def find_spec(self, fullname, path, target=None):
        import traceback

        meta_path = sys.meta_path
        try:
            if self.ignore_patterns:
                for pattern in self.ignore_patterns:
                    if fnmatch.fnmatch(fullname, pattern):
                        return None
            sys.meta_path = [finder for finder in meta_path if finder is not self]
            if importlib.util.find_spec(fullname) is None:
                # 检查 import 语句是否在捕获 ImportError 的 try except 块中
                if self._is_in_try():
                    # 如果在捕获 ImportError 的 try except 块中，不进行 auto mock，让 ImportError 正常抛出
                    return None

                # stack = "".join(traceback.format_stack(limit=10))
                # 查找最近一个 import
                target_stack = ""
                for line in traceback.format_stack()[:-1]:
                    if not "frozen" in line:
                        target_stack += "\n" + line
                print(
                    f"模块 '{fullname}' 不存在，已自动 mock\n"
                    # f"导入调用堆栈：{target_stack}",
                    # ImportWarning,
                    # stacklevel=10
                )
                self.matches[fullname] = None
                return ModuleSpec(fullname, self._loader)
        finally:
            sys.meta_path = meta_path
        return None

    def _is_in_try(self):
        import inspect
        import os

        cur_frame = inspect.currentframe()
        using_import_lib = False
        while cur_frame.f_back:
            file = cur_frame.f_code.co_filename
            f_line = cur_frame.f_lineno
            if os.path.exists(file):
                if self._is_in_try_block(file, f_line):
                    return True
                elif os.path.dirname(importlib.__file__) in file:
                    # using customized import
                    using_import_lib = True
                elif using_import_lib:
                    if cur_frame.f_code.co_name == "get_object_from_file":
                        using_import_lib = False
                    else:
                        return True
            cur_frame = cur_frame.f_back
        return using_import_lib

    def _is_in_try_block(self, filename, lineno):
        """检查指定行号的代码是否在捕获 ImportError 的 try 块中"""
        import ast

        try:
            # 读取整个文件内容
            with open(filename, "r", encoding="utf-8") as f:
                source = f.read()

            # 解析 AST
            tree = ast.parse(source)

            # 遍历 AST 节点，查找 try 语句
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    # 检查目标行号是否在 try 块的范围内
                    try_start = node.lineno
                    try_end = node.end_lineno if hasattr(node, "end_lineno") else None

                    # 如果没有 end_lineno，尝试通过 body 的最后一个语句估算
                    if try_end is None and node.body:
                        last_stmt = node.body[-1]
                        try_end = (
                            last_stmt.end_lineno
                            if hasattr(last_stmt, "end_lineno")
                            else last_stmt.lineno
                        )

                    if try_start <= lineno <= (try_end or try_start):
                        # 检查对应的 except 块是否捕获了 ImportError
                        if self._check_except_handlers_for_import_error(node.handlers):
                            return True
            return False
        except Exception:
            # 如果检测失败，默认不跳过 auto mock
            return False

    def _check_except_handlers_for_import_error(self, handlers):
        """检查 except 处理器是否捕获了 ImportError"""
        import ast

        for handler in handlers:
            if handler.type is None:  # bare except
                return True
            elif isinstance(handler.type, ast.Name):
                if handler.type.id in [
                    "ImportError",
                    "ModuleNotFoundError",
                    "Exception",
                ]:
                    return True
            elif isinstance(handler.type, ast.Tuple):
                # 处理 except (ImportError, ModuleNotFoundError) 这种情况
                for elt in handler.type.elts:
                    if isinstance(elt, ast.Name) and elt.id in [
                        "ImportError",
                        "ModuleNotFoundError",
                        "Exception",
                    ]:
                        return True
        return False


@contextmanager
def mock_imports(
    patterns: list | None = None,
    auto_mock_missing: bool = True,
    auto_mock_ignore_patterns: list | None = ["backports_abc"],
):
    """只在 import 真的失败时才 mock，支持多次捕获 ImportError 并重试，每次循环都重置注入"""
    injected_finders = []
    if patterns:
        pattern_finder = PatternMockFinder(patterns)
        sys.meta_path.insert(0, pattern_finder)
        injected_finders.append(pattern_finder)
    if auto_mock_missing:
        auto_mock_finder = AutoMockMissingFinder(auto_mock_ignore_patterns)
        sys.meta_path.insert(0, auto_mock_finder)
        injected_finders.append(auto_mock_finder)

    try:
        yield
    finally:
        # 最后一次注入后要恢复 sys.meta_path
        for finder in injected_finders:
            if finder in sys.meta_path:
                sys.meta_path.remove(finder)
        # 恢复 sys.modules
        for finder in injected_finders:
            for name, original_module in finder.matches.items():
                if original_module:
                    sys.modules[name] = original_module
                else:
                    sys.modules.pop(name, None)


if __name__ == "__main__":
    with mock_imports(["torch*"]):
        import math  # 测试对正常库无影响

        import java
        import numpy
        import torch
        import torch.distributed
        import torch.nn as nn
        import torch.nn.functional as F

        print(torch)
        print(nn)
        print(F)
        print(math)
        print(numpy)
        print(java)
