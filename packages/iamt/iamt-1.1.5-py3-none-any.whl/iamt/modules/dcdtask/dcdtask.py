"""DCD Task 模块 - Docker Compose 部署任务函数

提供将本地 docker compose 模块部署到远程服务器的 task 函数
"""

import tarfile
import tempfile
from pathlib import Path

from fabric import Connection, task


# region 常量配置

ENV_LANG_C = {"LANG": "C", "LC_ALL": "C"}

# endregion


# region Task 函数

@task
def deploy_compose_module(conn: Connection, local_path: str, remote_dir: str, force: bool = False) -> tuple[bool, str]:
    """部署 docker compose 模块到远程服务器

    Args:
        conn: Fabric 连接对象
        local_path: 本地 compose 模块路径
        remote_dir: 远程部署目录
        force: 强制执行，若远程目录已存在且有 compose 项目运行，会先停止并删除

    Returns:
        tuple[bool, str]: (是否成功, 结果消息)
    """
    local_dir = Path(local_path)
    if not local_dir.exists():
        msg = f"本地路径不存在: {local_path}"
        print(f"[ERROR] {msg}")
        return False, msg

    # region 检查远程目录
    check_result = conn.run(f"test -d {remote_dir} && ls -A {remote_dir} | head -1", warn=True, hide=True, env=ENV_LANG_C)
    dir_exists_and_has_content = check_result.ok and check_result.stdout.strip()

    if dir_exists_and_has_content:
        if not force:
            msg = f"远程目录已存在且不为空: {remote_dir}"
            print(f"[ERROR] {msg}")
            print("[HINT] 使用 force=True 参数可强制覆盖部署")
            return False, msg

        # 强制模式：检查是否有 docker-compose 文件并停止项目
        compose_check = conn.run(f"test -f {remote_dir}/docker-compose.yml -o -f {remote_dir}/docker-compose.yaml -o -f {remote_dir}/compose.yml -o -f {remote_dir}/compose.yaml", warn=True, hide=True)
        if compose_check.ok:
            print(f"[INFO] 检测到 compose 文件，正在停止 docker compose 项目...")
            conn.sudo(f"bash -c 'cd {remote_dir} && docker compose down'", warn=True, env=ENV_LANG_C, timeout=300)
            print(f"[OK] docker compose 项目已停止")

        print(f"[INFO] 正在删除远程目录: {remote_dir}")
        conn.sudo(f"rm -rf {remote_dir}", env=ENV_LANG_C)
        print(f"[OK] 远程目录已删除")
    # endregion

    # region 创建远程目录
    conn.sudo(f"mkdir -p {remote_dir}", env=ENV_LANG_C)
    print(f"[OK] 远程目录已创建: {remote_dir}")
    # endregion

    # region 打包上传解压
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_file:
        tar_path = tmp_file.name

    # 本地打包
    files_count = 0
    with tarfile.open(tar_path, "w:gz") as tar:
        for local_file in local_dir.rglob("*"):
            if local_file.is_file():
                arcname = local_file.relative_to(local_dir)
                tar.add(local_file, arcname=arcname)
                files_count += 1
                print(f"  [+] {arcname}")

    # 上传并解压
    remote_tar = f"/tmp/{local_dir.name}.tar.gz"
    conn.put(tar_path, remote_tar)
    conn.sudo(f"tar -xzf {remote_tar} -C {remote_dir}", env=ENV_LANG_C)
    conn.run(f"rm -f {remote_tar}")

    # 清理本地临时文件
    Path(tar_path).unlink()
    # endregion

    msg = f"成功部署 {files_count} 个文件到 {remote_dir}"
    print(f"[OK] {msg}")
    return True, msg




@task
def remove_compose_module(conn: Connection, remote_dir: str) -> None:
    """删除远程服务器上的 compose 模块目录

    Args:
        conn: Fabric 连接对象
        remote_dir: 远程目录路径
    """
    conn.sudo(f"rm -rf {remote_dir}", env=ENV_LANG_C)
    print(f"[OK] 已删除远程目录: {remote_dir}")


@task
def compose_up(conn: Connection, remote_dir: str, detach: bool = True) -> None:
    """在远程服务器上启动 docker compose

    Args:
        conn: Fabric 连接对象
        remote_dir: compose 模块所在的远程目录
        detach: 是否后台运行，默认 True
    """
    detach_flag = "-d" if detach else ""
    conn.sudo(f"bash -c 'cd {remote_dir} && docker compose up {detach_flag}'", env=ENV_LANG_C)
    print(f"[OK] docker compose up 执行完成")


@task
def compose_down(conn: Connection, remote_dir: str, volumes: bool = False) -> None:
    """在远程服务器上停止 docker compose

    Args:
        conn: Fabric 连接对象
        remote_dir: compose 模块所在的远程目录
        volumes: 是否同时删除 volumes，默认 False
    """
    volumes_flag = "-v" if volumes else ""
    conn.sudo(f"bash -c 'cd {remote_dir} && docker compose down {volumes_flag}'", env=ENV_LANG_C)
    print(f"[OK] docker compose down 执行完成")


@task
def compose_ps(conn: Connection, remote_dir: str) -> None:
    """查看远程服务器上 compose 容器状态

    Args:
        conn: Fabric 连接对象
        remote_dir: compose 模块所在的远程目录
    """
    conn.sudo(f"bash -c 'cd {remote_dir} && docker compose ps'", env=ENV_LANG_C)


@task
def compose_logs(conn: Connection, remote_dir: str, follow: bool = False, tail: int = 100) -> None:
    """查看远程服务器上 compose 容器日志

    Args:
        conn: Fabric 连接对象
        remote_dir: compose 模块所在的远程目录
        follow: 是否持续跟踪日志，默认 False
        tail: 显示最后多少行，默认 100
    """
    follow_flag = "-f" if follow else ""
    conn.sudo(f"bash -c 'cd {remote_dir} && docker compose logs {follow_flag} --tail {tail}'", env=ENV_LANG_C)

# endregion
