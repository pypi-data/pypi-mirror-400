from rich.console import Console

from ..uv import (
    Connection,
    create_uv_install_dir,
    install_uv,
    setup_uv_path,
    configure_uv,
)
from ..._utils.steps import Step, run_steps

console = Console()


def setup_uv(c: Connection) -> None:
    """在远程服务器上安装配置 uv
    
    执行以下步骤:
    1. 创建 uv 安装目录 (~/.local/bin)
    2. 下载并安装 uv 二进制文件
    3. 配置 PATH 环境变量
    4. 生成 uv 配置文件 (使用国内镜像源)
    
    Args:
        c: Fabric 连接对象
    """
    steps: list[Step] = [
        ("创建 UV 安装目录", create_uv_install_dir),
        ("安装 UV", install_uv),
        ("配置 PATH 环境变量", setup_uv_path),
        ("生成 UV 配置文件", configure_uv),
    ]
    run_steps(c, steps)
    console.print("[bold green]✓ UV 安装配置完成[/bold green]")
