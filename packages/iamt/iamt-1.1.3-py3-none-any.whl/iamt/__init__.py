

import inspect
import importlib
import pkgutil
from pathlib import Path

import fire 
from fabric import Connection
from fabric import Task 
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel

from .client_config.client_config import ClientConfig

from .dcd.dcd import DCD 

class ENTRY:
    
    def __init__(self):
        self.dcd=DCD()
        pass

    def _scan_roles(self) -> dict[str, dict]:
        """扫描 modules 目录下所有 roles 文件夹中定义的函数"""
        roles = {}
        modules_path = Path(__file__).parent / "modules"
        
        # region 遍历 modules 目录下的非下划线开头的文件夹
        for module_dir in modules_path.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue
            
            roles_dir = module_dir / "roles"
            if not roles_dir.exists() or not roles_dir.is_dir():
                continue
            
            # region 扫描 roles 目录下的所有 Python 文件
            for py_file in roles_dir.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                
                # 构建模块导入路径
                relative_path = py_file.relative_to(Path(__file__).parent)
                module_name = ".".join(relative_path.with_suffix("").parts)
                
                try:
                    module = importlib.import_module(f".{module_name}", package="iamt")
                    # 查找在该模块中定义的函数（排除导入的函数）
                    for name, obj in vars(module).items():
                        if inspect.isfunction(obj) and obj.__module__ == module.__name__:
                            roles[name] = {
                                "func": obj,
                                "module": module_dir.name,
                                "source": py_file.name
                            }
                except ImportError as e:
                    print(f"警告: 无法导入模块 {module_name}: {e}")
            # endregion
        # endregion
        
        return roles
    
    def _scan_modules(self) -> list[str]:
        """扫描 modules 目录下的所有模块"""
        modules_path = Path(__file__).parent / "modules"
        return [
            d.name for d in modules_path.iterdir() 
            if d.is_dir() and not d.name.startswith("_")
        ]
    
    def list_modules(self):
        """列出所有可用模块"""
        console = Console()
        columns = Columns(self._scan_modules(), equal=True, expand=True, column_first=False)
        panel = Panel(columns, title="可用模块", border_style="blue")
        console.print(panel)
    
    def list_hostvars(self, hostname: str | None = None):
        """列出主机变量，可指定 hostname"""
        config = ClientConfig()
        conn = config.connect(hostname)
        if conn is None:
            return
        console = Console()
        console.print(config.hostvars)
    
    def _scan_tasks(self) -> dict[str, dict]:
        """扫描 modules 目录下所有子目录中的 task"""
        tasks = {}
        modules_path = Path(__file__).parent / "modules"
        
        # region 遍历 modules 目录下的非下划线开头的子目录
        for module_dir in modules_path.iterdir():
            # print(module_dir)
            if not module_dir.is_dir() or module_dir.name.startswith("_"):
                continue
            
            # region 扫描子目录下不以下划线开头的 Python 文件
            for py_file in module_dir.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                
                module_name = py_file.stem
                import_path = f".modules.{module_dir.name}.{module_name}"
                
                try:
                    module = importlib.import_module(import_path, package="iamt")
                    source_file = py_file.name
                    
                    for name, obj in vars(module).items():
                        if isinstance(obj, Task):
                            tasks[name] = {
                                "task": obj,
                                "source": source_file,
                                "module": module_dir
                            }
                except ImportError as e:
                    print(f"警告: 无法导入模块 {import_path}: {e}")
            # endregion
        # endregion
        
        return tasks
    
    def list_tasks(self):
        """列出所有任务"""
        print("可用任务:")
        for name, task_info in (self._scan_tasks()).items():
            task_obj = task_info["task"]
            sig = inspect.signature(task_obj.body)
            params = [p for p in sig.parameters.keys() if p != 'ctx']
            params_str = f"({', '.join(params)})" if params else "()"
            doc = (task_obj.body.__doc__ or "").strip().split('\n')[0]
            location = f"@ {task_info['module'].name}/{task_info['source']}"
            print(f"  {name}{params_str}: {doc} {location}")
    

    
    def run_task(self):
        """交互式选择并运行任务"""
        from prompt_toolkit import prompt
        from .completers.customCompleter import CustomCompleter, CustomValidator
        
        if not self._scan_tasks():
            print("没有可用的任务")
            return
        
        # region 构建 模块名.task函数名 格式的选项列表
        task_options = {
            f"{task_info['module'].name}.{name}": f"{task_info['module'].name}.{name}" 
            for name, task_info in (self._scan_tasks()).items()
        }
        completer = CustomCompleter(task_options)
        validator = CustomValidator(completer, error_msg="无效的任务，请从补全列表中选择")
        # endregion
        
        # region 模糊搜索选择
        try:
            selected_key = prompt(
                "请选择要运行的任务 (Tab补全, 支持模糊搜索): ",
                completer=completer,
                validator=validator
            ).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n已取消选择")
            return
        
        if not selected_key or selected_key not in task_options:
            print(f"无效的选择: {selected_key}")
            return
        # endregion
        
        # region 执行选中的任务
        # selected_key 格式为 "模块名.任务名"，提取任务名
        task_name = selected_key.split(".")[-1]
        task_info = (self._scan_tasks())[task_name]
        task_obj = task_info["task"]
        config = ClientConfig()
        conn = config.connect()
        if conn is None:
            return
        doc = (task_obj.body.__doc__ or "").strip()
        if doc:
            print(f"\n{doc}\n")
        try:
            task_obj(conn)
        except Exception as e:
            print(f"任务 '{task_name}' 执行失败: {e}")
    
    
    def list_roles(self):
        """列出所有可用的 roles"""
        print("可用 roles:")
        for name, info in (self._scan_roles()).items():
            print(f"  {name} @ {info['module']}/roles/{info['source']}")

    def run_role(self):
        """交互式选择并运行 role"""
        from prompt_toolkit import prompt
        from prompt_toolkit.completion import FuzzyWordCompleter
        
        if not self._scan_roles():
            print("没有可用的 roles")
            return
        
        # region 构建模块名.函数名格式的选项列表
        role_options = {
            f"{info['module']}.{name}": name
            for name, info in (self._scan_roles()).items()
        }
        completer = FuzzyWordCompleter(list(role_options.keys()))
        # endregion
        
        # region 模糊搜索选择
        try:
            selected_key = prompt(
                "请选择要运行的 role (Tab补全, 支持模糊搜索): ",
                completer=completer
            ).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n已取消选择")
            return
        
        if not selected_key or selected_key not in role_options:
            print(f"无效的选择: {selected_key}")
            return
        # endregion
        
        # region 执行选中的 role
        selected = role_options[selected_key]
        role_info = (self._scan_roles())[selected]
        role_func = role_info["func"]
        config = ClientConfig()
        conn = config.connect()
        if conn is None:
            return

        # region 询问是否保存配置
        import questionary
        from .utils.config_saver import save_task_config, get_hostname_from_vbi_config
        from .utils.task_tracker import TaskTracker

        save_config = questionary.confirm(
            "是否在执行后保存运行配置?",
            default=False,
        ).ask()
        # endregion

        # region 使用 TaskTracker 追踪 task 调用
        tracker = TaskTracker()
        if save_config:
            tracker.patch_role_module(role_info["module"])

        try:
            role_func(conn)
        except Exception as e:
            print(f"Role '{selected}' 执行失败: {e}")
            tracker.unpatch_all()
            return
        finally:
            tracker.unpatch_all()
        # endregion

        # region 保存配置文件
        if save_config and tracker.calls:
            save_task_config(
                hostname=get_hostname_from_vbi_config(),
                tasks=tracker.calls,
                config_name=selected,
                suffix=".role.yaml",
            )
        # endregion
        # endregion

    def test(self, hostname: str | None = None):
        """测试连接"""
        config = ClientConfig()
        conn = config.connect(hostname)
        if conn:
            print(f"连接成功: {config.hostvars.get('hostname', 'unknown')}")

    def run_file(self) -> None:
        """从当前目录的配置文件执行 task 函数"""
        import questionary
        import yaml
        from .client_config.client_config import ClientConfig, CONFIG_FILE
        
        console = Console()
        
        # region 扫描配置文件
        config_suffixes = [".dcd.yaml", ".role.yaml"]
        config_files: list[Path] = []
        for suffix in config_suffixes:
            config_files.extend(Path.cwd().glob(f"*{suffix}"))
        
        if not config_files:
            console.print(f"[yellow]当前目录未找到配置文件 ({', '.join(config_suffixes)})[/yellow]")
            return
        # endregion
        
        # region 选择配置文件
        if len(config_files) == 1:
            selected_file = config_files[0]
        else:
            file_choices = [f.name for f in config_files]
            selected_name = questionary.select("请选择配置文件:", choices=file_choices).ask()
            if selected_name is None:
                console.print("[yellow]已取消[/yellow]")
                return
            selected_file = Path.cwd() / selected_name
        # endregion
        
        # region 读取并验证配置
        try:
            config_data = yaml.safe_load(selected_file.read_text(encoding="utf-8"))
        except Exception as e:
            console.print(f"[red]读取配置文件失败: {e}[/red]")
            return
        
        hostname = config_data.get("hostname", "")
        tasks = config_data.get("tasks", [])
        
        if not hostname:
            console.print("[red]配置文件缺少 hostname[/red]")
            return
        if not tasks:
            console.print("[red]配置文件缺少 tasks[/red]")
            return
        # endregion
        
        # region 验证 hostname 并创建连接
        if not CONFIG_FILE.exists():
            console.print("[red]未找到 iamt.yaml 配置文件[/red]")
            return
        
        vbi_config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
        if hostname not in vbi_config.get("hosts", {}):
            console.print(f"[red]iamt.yaml 中未找到主机: {hostname}[/red]")
            return
        
        config = ClientConfig()
        conn = config.connect(hostname)
        if conn is None:
            console.print("[red]无法连接到服务器[/red]")
            return
        # endregion
        
        # region 显示配置信息并确认
        console.print(f"[cyan]配置文件: {selected_file.name}[/cyan]")
        console.print(f"[cyan]目标主机: {hostname}[/cyan]")
        console.print("[cyan]待执行任务:[/cyan]")
        for t in tasks:
            console.print(f"  - {t['task']}: {t['args']}")
        
        if not questionary.confirm("确认执行?", default=True).ask():
            console.print("[yellow]已取消[/yellow]")
            return
        # endregion
        
        # region 执行 tasks
        scanned_tasks = self._scan_tasks()
        
        for task_call in tasks:
            task_name = task_call["task"]
            task_args = task_call.get("args", {}).copy()
            
            # 解析 task 名称 (格式: module.function)
            parts = task_name.split(".")
            if len(parts) != 2:
                console.print(f"[red]无效的 task 名称: {task_name}[/red]")
                continue
            
            func_name = parts[1]
            
            # 从扫描结果中获取 task
            if func_name not in scanned_tasks:
                console.print(f"[red]未找到 task 函数: {task_name}[/red]")
                continue
            
            task_obj = scanned_tasks[func_name]["task"]
            
            # 执行 task
            console.print(f"[cyan]执行: {task_name}[/cyan]")
            try:
                task_obj(conn, **task_args)
            except Exception as e:
                console.print(f"[red]执行失败: {e}[/red]")
                return
        
        console.print("[green]所有任务执行完成[/green]")
        # endregion


def main() -> None:
    try:
        fire.Fire(ENTRY)
    except KeyboardInterrupt:
        print("\n操作已取消")
        exit(0)
    # except Exception as e:
    #     print(f"\n程序执行出错: {str(e)}")
    #     print("请检查您的输入参数或网络连接")
    #     exit(1)