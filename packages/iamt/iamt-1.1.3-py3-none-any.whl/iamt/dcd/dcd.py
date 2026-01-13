"""DCD 模块 - Docker Compose 部署管理

提供以下命令:
- vbi dcd ls: 列出所有可用的 docker compose 模块
- vbi dcd x: 交互式部署 docker compose 模块到远程服务器
- vbi dcd file: 从配置文件执行部署任务
"""

from pathlib import Path
from typing import TypedDict

import questionary
import yaml
from prompt_toolkit import prompt
from rich.console import Console
from rich.table import Table

from ..completers.customCompleter import CustomCompleter, CustomValidator


# region 常量配置

COMPOSES_DIR = Path(__file__).parent.parent / "composes"
DCD_CONFIG_SUFFIX = ".dcd.yaml"

# endregion


# region 类型定义

from ..utils.config_saver import TaskCall, save_task_config, get_hostname_from_vbi_config


class ComposeModule(TypedDict):
    """Docker Compose 模块信息"""
    name: str             # 模块名称
    category: str         # 所属分类
    path: Path            # 模块路径

# endregion


class DCD:
    """Docker Compose 部署管理类"""

    def __init__(self):
        self.console = Console()

    # region vbi dcd ls - 列出所有 compose 模块

    def ls(self) -> None:
        """列出所有可用的 docker compose 模块"""
        modules = self._scan_compose_modules()
        if not modules:
            self.console.print("[yellow]未找到任何 docker compose 模块[/yellow]")
            return

        table = Table(title="Docker Compose 模块列表", show_lines=False)
        table.add_column("分类", style="cyan")
        table.add_column("模块名", style="green")
        table.add_column("路径", style="dim")

        for module in modules:
            table.add_row(module["category"], module["name"], str(module["path"].relative_to(COMPOSES_DIR)))

        self.console.print(table)
        self.console.print(f"\n[dim]共 {len(modules)} 个模块[/dim]")

    def _scan_compose_modules(self) -> list[ComposeModule]:
        """扫描 composes 目录下所有包含 docker-compose.yml 的模块"""
        modules: list[ComposeModule] = []
        if not COMPOSES_DIR.exists():
            return modules

        for category_dir in sorted(COMPOSES_DIR.iterdir()):
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue

            for module_dir in sorted(category_dir.iterdir()):
                if not module_dir.is_dir():
                    continue

                compose_file = module_dir / "docker-compose.yml"
                if compose_file.exists():
                    modules.append({
                        "name": module_dir.name,
                        "category": category_dir.name,
                        "path": module_dir,
                    })

        return modules

    # endregion

    # region vbi dcd x - 交互式部署

    def x(self, force: bool = False, start: bool = False) -> None:
        """交互式部署 docker compose 模块到远程服务器

        Args:
            force: 强制执行，若远程目录已存在且有 compose 项目运行，会先停止并删除
            start: 部署完成后是否立即启动项目
        """
        from ..client_config.client_config import ClientConfig

        # region 选择 compose 模块
        modules = self._scan_compose_modules()
        if not modules:
            self.console.print("[red]未找到任何 docker compose 模块[/red]")
            return

        module_choices = {f"{m['category']}/{m['name']}": f"{m['category']}/{m['name']}" for m in modules}
        completer = CustomCompleter(module_choices)
        validator = CustomValidator(completer, "无效的模块，请从补全列表中选择。")

        try:
            selected = prompt(
                "请选择要部署的 docker compose 模块: ",
                completer=completer,
                validator=validator,
            )
        except (KeyboardInterrupt, EOFError):
            self.console.print("[yellow]已取消[/yellow]")
            return

        if not selected:
            self.console.print("[yellow]已取消[/yellow]")
            return

        selected_module = modules[list(module_choices.keys()).index(selected)]
        # endregion

        # region 获取远程部署目录
        default_remote_dir = f"/opt/docker/{selected_module['name']}"
        remote_dir = questionary.text(
            "请输入远程部署目录:",
            default=default_remote_dir,
        ).ask()

        if remote_dir is None:
            self.console.print("[yellow]已取消[/yellow]")
            return
        # endregion

        # region 确认并执行部署
        config = ClientConfig()
        conn = config.connect()
        if conn is None:
            self.console.print("[red]无法连接到服务器[/red]")
            return

        host_info = f"{conn.user}@{conn.host}:{conn.port}"
        mode_hints = []
        if force:
            mode_hints.append("强制模式")
        if start:
            mode_hints.append("部署后启动")
        mode_hint = f" [{', '.join(mode_hints)}]" if mode_hints else ""
        confirm = questionary.confirm(
            f"确认部署 {selected} 到 {host_info}:{remote_dir}?{mode_hint}",
            default=True,
        ).ask()

        if not confirm:
            self.console.print("[yellow]已取消[/yellow]")
            return
        # endregion

        # region 执行部署任务
        from ..modules.dcdtask.dcdtask import compose_up, deploy_compose_module

        # 记录执行的 task 调用
        executed_tasks: list[TaskCall] = []

        deploy_args = {
            "local_path": str(selected_module["path"]),
            "remote_dir": remote_dir,
            "force": force,
        }
        success, msg = deploy_compose_module(conn, **deploy_args)
        executed_tasks.append({"task": "dcdtask.deploy_compose_module", "args": deploy_args})

        if not success:
            self.console.print(f"[red]部署失败: {msg}[/red]")
            return

        if start:
            up_args = {"remote_dir": remote_dir}
            compose_up(conn, **up_args)
            executed_tasks.append({"task": "dcdtask.compose_up", "args": up_args})
        # endregion

        # region 保存配置文件
        save_config = questionary.confirm(
            "是否保存部署配置到当前目录?",
            default=True,
        ).ask()

        if save_config:
            config_name = Path(remote_dir).name
            save_task_config(
                hostname=get_hostname_from_vbi_config(),
                tasks=executed_tasks,
                config_name=config_name,
                suffix=DCD_CONFIG_SUFFIX,
            )
        # endregion

    # endregion

    # region vbi dcd file - 从配置文件部署

    def file(self) -> None:
        """从当前目录的配置文件执行部署任务"""
        from ..client_config.client_config import ClientConfig, CONFIG_FILE

        # region 扫描配置文件
        config_files = list(Path.cwd().glob(f"*{DCD_CONFIG_SUFFIX}"))
        if not config_files:
            self.console.print(f"[yellow]当前目录未找到 {DCD_CONFIG_SUFFIX} 配置文件[/yellow]")
            return
        # endregion

        # region 选择配置文件
        if len(config_files) == 1:
            selected_file = config_files[0]
        else:
            file_choices = [f.name for f in config_files]
            selected_name = questionary.select(
                "请选择配置文件:",
                choices=file_choices,
            ).ask()

            if selected_name is None:
                self.console.print("[yellow]已取消[/yellow]")
                return

            selected_file = Path.cwd() / selected_name
        # endregion

        # region 读取配置
        try:
            config_data: DCDConfig = yaml.safe_load(selected_file.read_text(encoding="utf-8"))
        except Exception as e:
            self.console.print(f"[red]读取配置文件失败: {e}[/red]")
            return

        hostname = config_data.get("hostname", "")
        tasks = config_data.get("tasks", [])

        if not hostname:
            self.console.print("[red]配置文件缺少 hostname[/red]")
            return
        if not tasks:
            self.console.print("[red]配置文件缺少 tasks[/red]")
            return
        # endregion

        # region 验证 hostname 并创建连接
        if not CONFIG_FILE.exists():
            self.console.print(f"[red]未找到 iamt.yaml 配置文件[/red]")
            return

        vbi_config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
        hosts = vbi_config.get("hosts", {})
        if hostname not in hosts:
            self.console.print(f"[red]iamt.yaml 中未找到主机: {hostname}[/red]")
            return

        config = ClientConfig()
        conn = config.connect(hostname)
        if conn is None:
            self.console.print("[red]无法连接到服务器[/red]")
            return
        # endregion

        # region 显示配置信息并确认
        self.console.print(f"[cyan]配置文件: {selected_file.name}[/cyan]")
        self.console.print(f"[cyan]目标主机: {hostname}[/cyan]")
        self.console.print(f"[cyan]待执行任务:[/cyan]")
        for t in tasks:
            self.console.print(f"  - {t['task']}: {t['args']}")

        confirm = questionary.confirm("确认执行部署?", default=True).ask()
        if not confirm:
            self.console.print("[yellow]已取消[/yellow]")
            return
        # endregion

        # region 执行 tasks
        from ..modules.dcdtask import dcdtask as dcdtask_module

        for task_call in tasks:
            task_name = task_call["task"]
            task_args = task_call["args"].copy()

            # 解析 task 名称 (格式: module.function)
            parts = task_name.split(".")
            if len(parts) != 2:
                self.console.print(f"[red]无效的 task 名称: {task_name}[/red]")
                continue

            module_name, func_name = parts

            # 获取 task 函数
            try:
                task_func = getattr(dcdtask_module, func_name, None)
                if task_func is None:
                    self.console.print(f"[red]未找到 task 函数: {task_name}[/red]")
                    continue
            except Exception as e:
                self.console.print(f"[red]加载 task 失败: {task_name}, {e}[/red]")
                continue

            # 执行 task
            self.console.print(f"[cyan]执行: {task_name}[/cyan]")
            try:
                task_func(conn, **task_args)
            except Exception as e:
                self.console.print(f"[red]执行失败: {e}[/red]")
                return
        # endregion

    # endregion
