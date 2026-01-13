"""配置保存工具模块

提供统一的 task 配置保存功能，供 DCD 和 role 执行时复用。
"""

from pathlib import Path
from typing import TypedDict

import yaml
from rich.console import Console


class TaskCall(TypedDict):
    """Task 函数调用记录"""
    task: str             # task 函数名称 (格式: module.function)
    args: dict            # 调用参数 (不含 conn)


class TaskConfig(TypedDict):
    """Task 配置文件结构"""
    hostname: str         # iamt.yaml 中的主机名
    tasks: list[TaskCall] # 执行的 task 函数列表


def save_task_config(
    hostname: str,
    tasks: list[TaskCall],
    config_name: str,
    suffix: str = ".dcd.yaml",
    output_dir: Path | None = None,
) -> Path | None:
    """保存 task 配置到文件

    Args:
        hostname: iamt.yaml 中的主机名
        tasks: 执行的 task 函数调用列表
        config_name: 配置文件名 (不含后缀)
        suffix: 配置文件后缀，默认 ".dcd.yaml"
        output_dir: 输出目录，默认为当前工作目录

    Returns:
        保存成功返回配置文件路径，失败返回 None
    """
    console = Console()

    if not hostname:
        console.print("[red]hostname 不能为空[/red]")
        return None

    if not tasks:
        console.print("[red]tasks 列表不能为空[/red]")
        return None

    config_data: TaskConfig = {
        "hostname": hostname,
        "tasks": tasks,
    }

    output_dir = output_dir or Path.cwd()
    config_file = output_dir / f"{config_name}{suffix}"

    try:
        config_file.write_text(
            yaml.dump(config_data, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        console.print(f"[green]配置已保存到 {config_file.name}[/green]")
        return config_file
    except Exception as e:
        console.print(f"[red]保存配置失败: {e}[/red]")
        return None


def get_hostname_from_vbi_config() -> str:
    """从 iamt.yaml 中获取第一个 hostname

    Returns:
        hostname 字符串，未找到返回空字符串
    """
    from ..client_config.client_config import CONFIG_FILE

    if not CONFIG_FILE.exists():
        return ""

    try:
        config_data = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
        return next(iter(config_data.get("hosts", {})), "")
    except Exception:
        return ""
