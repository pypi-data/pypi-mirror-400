from rich.console import Console

from ..docker import (
    Connection,
    uninstall_old_docker,
    install_dependencies,
    setup_gpg_key,
    setup_docker_repo,
    install_docker,
    install_docker_compose,
    configure_daemon,
    configure_docker_user,
    enable_docker,
    restart_docker,
)
from ..._utils.steps import Step, run_steps

console = Console()


def china_server_setup_docker(c: Connection):
    """完整安装配置 Docker CE 环境"""
    steps: list[Step] = [
        ("卸载旧版 Docker", uninstall_old_docker),
        ("安装依赖包", install_dependencies),
        ("配置 GPG 密钥", setup_gpg_key),
        ("配置 Docker 仓库", lambda c: setup_docker_repo(c, mirror="aliyun")),
        ("安装 Docker CE", install_docker),
        ("安装 Docker Compose", install_docker_compose),
        ("配置 Docker daemon", configure_daemon),
        ("配置 Docker 用户权限", configure_docker_user),
        ("设置 Docker 服务开机自启动", enable_docker),
        ("重启 Docker 服务", restart_docker),
    ]
    run_steps(c, steps)
    console.print("[bold green]✓ Docker 安装配置完成[/bold green]")



def other_server_setup_docker(c: Connection):
    """完整安装配置 Docker CE 环境"""
    steps: list[Step] = [
        ("卸载旧版 Docker", uninstall_old_docker),
        ("安装依赖包", install_dependencies),
        ("配置 GPG 密钥", setup_gpg_key),
        ("配置 Docker 仓库", setup_docker_repo),
        ("安装 Docker CE", install_docker),
        ("安装 Docker Compose", install_docker_compose),
        ("配置 Docker 用户权限", configure_docker_user),
        ("设置 Docker 服务开机自启动", enable_docker),
        ("重启 Docker 服务", restart_docker),
    ]
    run_steps(c, steps)
    console.print("[bold green]✓ Docker 安装配置完成[/bold green]")
