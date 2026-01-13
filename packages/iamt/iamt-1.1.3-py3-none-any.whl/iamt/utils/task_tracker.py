"""Task 调用追踪模块

提供 Connection 包装类，用于追踪 role 执行过程中调用的 task 函数及其参数。
"""

import functools
import importlib
import sys
from pathlib import Path
from typing import Any, Callable

from fabric import Connection, Task

from .config_saver import TaskCall


class TaskTracker:
    """Task 调用追踪器

    通过 monkey-patch 模块中的 task 函数，记录 role 执行过程中的所有 task 调用。
    """

    def __init__(self):
        self._calls: list[TaskCall] = []
        self._patched: dict[str, dict[str, Any]] = {}  # module_name -> {func_name -> original_func}

    @property
    def calls(self) -> list[TaskCall]:
        """获取记录的 task 调用列表"""
        return self._calls.copy()

    def clear(self) -> None:
        """清空调用记录"""
        self._calls.clear()

    def _get_task_name(self, func: Callable) -> str:
        """从函数获取 task 名称 (格式: module.function)"""
        module_name = func.__module__
        func_name = func.__name__

        # 从模块路径提取简短名称 (如 iamt.modules.docker.docker -> docker)
        module_parts = module_name.split(".")
        if "modules" in module_parts:
            idx = module_parts.index("modules")
            short_module = module_parts[idx + 1] if idx + 1 < len(module_parts) else module_parts[-1]
        else:
            short_module = module_parts[-1]

        return f"{short_module}.{func_name}"

    def _wrap_func(self, func: Callable, task_name: str) -> Callable:
        """包装函数以追踪调用"""
        tracker = self

        @functools.wraps(func)
        def wrapper(conn: Connection, *args: Any, **kwargs: Any) -> Any:
            tracker._calls.append({
                "task": task_name,
                "args": kwargs.copy(),
            })
            return func(conn, *args, **kwargs)

        return wrapper

    def patch_module(self, module_name: str) -> None:
        """Patch 指定模块中的所有 task 函数

        Args:
            module_name: 完整模块名 (如 iamt.modules.docker.docker)
        """
        if module_name in self._patched:
            return

        try:
            module = importlib.import_module(module_name)
        except ImportError:
            return

        self._patched[module_name] = {}

        for name in dir(module):
            obj = getattr(module, name)
            # 检查是否是在该模块定义的函数且被 @task 装饰
            if isinstance(obj, Task) and obj.body.__module__ == module_name:
                original_func = obj.body
                task_name = self._get_task_name(original_func)
                wrapped = self._wrap_func(original_func, task_name)
                # 保存原始函数
                self._patched[module_name][name] = original_func
                # 替换 Task 对象的 body
                obj.body = wrapped

    def unpatch_all(self) -> None:
        """恢复所有被 patch 的函数"""
        for module_name, funcs in self._patched.items():
            try:
                module = sys.modules.get(module_name)
                if module is None:
                    continue
                for name, original_func in funcs.items():
                    obj = getattr(module, name, None)
                    if isinstance(obj, Task):
                        obj.body = original_func
            except Exception:
                pass
        self._patched.clear()

    def patch_role_module(self, role_module_name: str) -> None:
        """根据 role 所在模块，patch 相关的 task 模块

        Args:
            role_module_name: role 函数所在的模块名 (如 docker)
        """
        # 构建 task 模块路径 (如 iamt.modules.docker.docker)
        task_module = f"iamt.modules.{role_module_name}.{role_module_name}"
        self.patch_module(task_module)

    def __enter__(self) -> "TaskTracker":
        return self

    def __exit__(self, *args: Any) -> None:
        self.unpatch_all()
