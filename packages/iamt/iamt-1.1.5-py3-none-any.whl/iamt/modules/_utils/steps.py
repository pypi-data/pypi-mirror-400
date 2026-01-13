from typing import Callable

from rich.console import Console

console = Console()

# region Step 定义与执行
type Step = tuple[str, Callable] | tuple[str, Callable, tuple] | tuple[str, Callable, tuple, dict]
"""
Step 类型定义，支持以下格式:
- (desc, func)                    # 仅描述和函数
- (desc, func, args)              # 带位置参数
- (desc, func, args, kwargs)      # 带位置参数和关键字参数
"""


def run_steps(c, steps: list[Step]):
    """执行步骤列表"""
    total = len(steps)
    for i, step in enumerate(steps, 1):
        desc, func = step[0], step[1]
        args = step[2] if len(step) > 2 else ()
        kwargs = step[3] if len(step) > 3 else {}
        console.print(f"[cyan][{i}/{total}][/cyan] [yellow]{desc}[/yellow]...")
        func(c, *args, **kwargs)
# endregion
