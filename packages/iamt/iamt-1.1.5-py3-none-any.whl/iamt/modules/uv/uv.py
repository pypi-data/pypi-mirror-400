"""UV 模块 - 在远程 Linux 主机上安装和配置 uv Python 包管理器

该模块通过 SSH 连接执行远程命令，实现 uv 的自动化部署和配置。
"""

import os
import platform
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from fabric import Connection, task


# region 模块常量配置

# 模板目录路径
TEMPLATES_DIR = Path(__file__).parent / "templates"

# UV 版本配置
UV_VERSION = "0.9.22"

# UV 下载 URL 模板
UV_DOWNLOAD_URL_TEMPLATE = "https://github.com/astral-sh/uv/releases/download/{version}/uv-{platform}.tar.gz"

# 平台映射 (本地系统 -> uv 发布平台名称)
UV_PLATFORM_MAP = {
    ("Linux", "x86_64"): "x86_64-unknown-linux-gnu",
    ("Linux", "aarch64"): "aarch64-unknown-linux-gnu",
    ("Darwin", "x86_64"): "x86_64-apple-darwin",
    ("Darwin", "arm64"): "aarch64-apple-darwin",
    ("Windows", "AMD64"): "x86_64-pc-windows-msvc",
}

# 远程主机架构映射
UV_REMOTE_PLATFORM_MAP = {
    "x86_64": "x86_64-unknown-linux-gnu",
    "aarch64": "aarch64-unknown-linux-gnu",
    "arm64": "aarch64-unknown-linux-gnu",
}

# 默认安装目录 (相对于用户家目录)
UV_INSTALL_DIR = ".local/bin"

# 环境变量 (使用英文输出避免中文乱码)
ENV_LANG_C = {"LANG": "C", "LC_ALL": "C"}

# endregion


# region 辅助函数

def _get_remote_platform(conn: Connection) -> str:
    """获取远程主机的平台标识
    
    Args:
        conn: Fabric 连接对象
        
    Returns:
        uv 发布平台名称 (如 x86_64-unknown-linux-gnu)
    """
    result = conn.run("uname -m", hide=True)
    arch = result.stdout.strip()
    return UV_REMOTE_PLATFORM_MAP.get(arch, "x86_64-unknown-linux-gnu")


def _download_uv_tarball(version: str, target_platform: str, dest_dir: str) -> str:
    """下载 uv 压缩包到本地
    
    Args:
        version: uv 版本号
        target_platform: 目标平台标识
        dest_dir: 下载目标目录
        
    Returns:
        下载后的压缩包路径
    """
    url = UV_DOWNLOAD_URL_TEMPLATE.format(version=version, platform=target_platform)
    filename = f"uv-{target_platform}.tar.gz"
    dest_path = os.path.join(dest_dir, filename)
    
    if os.path.exists(dest_path):
        print(f"  压缩包已存在: {dest_path}")
        return dest_path
    
    print(f"  正在下载: {url}")
    
    def progress_hook(block_num: int, block_size: int, total_size: int) -> None:
        if total_size > 0:
            percent = min(100, block_num * block_size * 100 // total_size)
            print(f"\r  下载进度: {percent}%", end="", flush=True)
    
    urllib.request.urlretrieve(url, dest_path, progress_hook)
    print(f"\n  下载完成: {dest_path}")
    
    return dest_path

# endregion


# region Task 函数

@task
def create_uv_install_dir(conn: Connection, install_dir: str | None = None) -> str:
    """创建 uv 安装目录
    
    默认在当前用户家目录下创建 .local/bin 目录
    
    Args:
        conn: Fabric 连接对象
        install_dir: 安装目录路径 (可选)，默认为 ~/.local/bin
        
    Returns:
        安装目录的完整路径
    """
    if install_dir is None:
        install_dir = f"~/{UV_INSTALL_DIR}"
    
    # 展开 ~ 为实际路径
    result = conn.run(f"echo {install_dir}", hide=True)
    full_path = result.stdout.strip()
    
    conn.run(f"mkdir -p {install_dir}", env=ENV_LANG_C)
    print(f"[OK] UV 安装目录已创建: {full_path}")
    
    return full_path


@task
def extract_uv_tarball(conn: Connection, tarball_path: str, extract_dir: str) -> None:
    """解压 uv 压缩包
    
    Args:
        conn: Fabric 连接对象
        tarball_path: 压缩包路径
        extract_dir: 解压目标目录
    """
    print(f"\n[任务] 解压压缩包")
    conn.run(f"tar -xzf {tarball_path} -C {extract_dir}", env=ENV_LANG_C)
    print("  解压完成")


@task
def install_uv_binaries(conn: Connection, extracted_dir: str, install_dir: str) -> None:
    """安装 uv 二进制文件
    
    从解压目录复制 uv 和 uvx 到安装目录
    
    Args:
        conn: Fabric 连接对象
        extracted_dir: 解压后的二进制文件目录
        install_dir: 安装目录路径
    """
    print(f"\n[任务] 安装 uv 二进制文件")
    
    # 展开安装目录路径
    result = conn.run(f"echo {install_dir}", hide=True)
    full_install_dir = result.stdout.strip()
    
    # 确保安装目录存在
    conn.run(f"mkdir -p {full_install_dir}", env=ENV_LANG_C)
    
    # 安装 uv
    conn.run(f"cp {extracted_dir}/uv {full_install_dir}/uv", env=ENV_LANG_C)
    conn.run(f"chmod +x {full_install_dir}/uv", env=ENV_LANG_C)
    print(f"  uv 已安装到: {full_install_dir}/uv")
    
    # 安装 uvx
    conn.run(f"cp {extracted_dir}/uvx {full_install_dir}/uvx", env=ENV_LANG_C)
    conn.run(f"chmod +x {full_install_dir}/uvx", env=ENV_LANG_C)
    print(f"  uvx 已安装到: {full_install_dir}/uvx")


@task
def cleanup_uv_temp(conn: Connection, temp_dir: str) -> None:
    """清理 uv 安装临时文件
    
    Args:
        conn: Fabric 连接对象
        temp_dir: 临时目录路径
    """
    print(f"\n[任务] 清理临时文件")
    conn.run(f"rm -rf {temp_dir}", env=ENV_LANG_C)
    print("  清理完成")


@task
def install_uv(conn: Connection, version: str | None = None, install_dir: str | None = None) -> None:
    """下载并安装 uv (本地下载模式)
    
    1. 下载 uv 压缩包到本地
    2. 上传压缩包到远程主机
    3. 解压并安装二进制文件
    4. 清理临时文件
    
    Args:
        conn: Fabric 连接对象
        version: uv 版本号 (可选)，默认使用 UV_VERSION
        install_dir: 安装目录路径 (可选)，默认为 ~/.local/bin
    """
    if version is None:
        version = UV_VERSION
    if install_dir is None:
        install_dir = f"~/{UV_INSTALL_DIR}"
    
    target_platform = _get_remote_platform(conn)
    print(f"[INFO] 目标平台: {target_platform}")
    
    remote_tmp_dir = "/tmp/uv_install"
    remote_tarball = f"{remote_tmp_dir}/uv.tar.gz"
    extracted_dir = f"{remote_tmp_dir}/uv-{target_platform}"
    
    # region 下载并上传压缩包
    print(f"\n[任务] 下载 uv {version}")
    with tempfile.TemporaryDirectory() as temp_dir:
        tarball_path = _download_uv_tarball(version, target_platform, temp_dir)
        
        print(f"\n[任务] 上传压缩包到远程主机")
        conn.run(f"mkdir -p {remote_tmp_dir}", env=ENV_LANG_C)
        conn.put(tarball_path, remote_tarball)
        print(f"  上传完成: {remote_tarball}")
    # endregion
    
    extract_uv_tarball(conn, remote_tarball, remote_tmp_dir)
    install_uv_binaries(conn, extracted_dir, install_dir)
    cleanup_uv_temp(conn, remote_tmp_dir)
    
    print(f"\n[OK] uv {version} 安装完成 (本地下载模式)")


@task
def install_uv_remote(conn: Connection, version: str | None = None, install_dir: str | None = None) -> None:
    """下载并安装 uv (远程下载模式)
    
    直接在远程主机上下载压缩包，适用于远程主机网络条件较好的场景。
    
    1. 在远程主机上下载 uv 压缩包
    2. 解压并安装二进制文件
    3. 清理临时文件
    
    Args:
        conn: Fabric 连接对象
        version: uv 版本号 (可选)，默认使用 UV_VERSION
        install_dir: 安装目录路径 (可选)，默认为 ~/.local/bin
    """
    if version is None:
        version = UV_VERSION
    if install_dir is None:
        install_dir = f"~/{UV_INSTALL_DIR}"
    
    target_platform = _get_remote_platform(conn)
    print(f"[INFO] 目标平台: {target_platform}")
    
    download_url = UV_DOWNLOAD_URL_TEMPLATE.format(version=version, platform=target_platform)
    print(f"[INFO] 下载地址: {download_url}")
    
    remote_tmp_dir = "/tmp/uv_install"
    remote_tarball = f"{remote_tmp_dir}/uv.tar.gz"
    extracted_dir = f"{remote_tmp_dir}/uv-{target_platform}"
    
    # region 在远程主机上下载压缩包
    print(f"\n[任务] 在远程主机上下载 uv {version}")
    conn.run(f"mkdir -p {remote_tmp_dir}", env=ENV_LANG_C)
    conn.run(f"curl -fsSL -o {remote_tarball} '{download_url}'", env=ENV_LANG_C)
    print(f"  下载完成: {remote_tarball}")
    # endregion
    
    extract_uv_tarball(conn, remote_tarball, remote_tmp_dir)
    install_uv_binaries(conn, extracted_dir, install_dir)
    cleanup_uv_temp(conn, remote_tmp_dir)
    
    print(f"\n[OK] uv {version} 安装完成 (远程下载模式)")


@task
def setup_uv_path(conn: Connection, install_dir: str | None = None, shell_rc: str = ".bashrc") -> None:
    """将 UV 安装目录添加到 PATH 并更新 shell 配置文件
    
    在用户的 shell 配置文件 (如 .bashrc) 中添加 PATH 配置
    
    Args:
        conn: Fabric 连接对象
        install_dir: 安装目录路径 (可选)，默认为 ~/.local/bin
        shell_rc: shell 配置文件名 (可选)，默认为 .bashrc
    """
    if install_dir is None:
        install_dir = f"$HOME/{UV_INSTALL_DIR}"
    
    # region 检查是否已配置
    rc_file = f"~/{shell_rc}"
    result = conn.run(f"grep -q '{UV_INSTALL_DIR}' {rc_file} 2>/dev/null", warn=True, hide=True)
    
    if result.ok:
        print(f"[OK] PATH 已配置在 {shell_rc} 中，跳过")
        return
    # endregion
    
    # region 添加 PATH 配置
    path_config = f'\n# UV PATH\nexport PATH="{install_dir}:$PATH"\n'
    conn.run(f"echo '{path_config}' >> {rc_file}", env=ENV_LANG_C)
    print(f"[OK] PATH 配置已添加到 ~/{shell_rc}")
    # endregion


@task
def configure_uv(conn: Connection, template: str = "uv.toml") -> None:
    """为当前用户添加 UV 配置文件
    
    1. 确保 ~/.config/uv/ 目录存在
    2. 根据模板在 ~/.config/uv/ 目录下生成 uv.toml 配置文件
    
    Args:
        conn: Fabric 连接对象
        template: 模板文件名 (可选)，默认为 uv.toml
    """
    # region 创建配置目录
    config_dir = "~/.config/uv"
    conn.run(f"mkdir -p {config_dir}", env=ENV_LANG_C)
    print(f"[OK] 配置目录已创建: {config_dir}")
    # endregion
    
    # region 读取模板并写入配置文件
    template_path = TEMPLATES_DIR / template
    config_content = template_path.read_text(encoding="utf-8")
    
    # 展开配置目录路径
    result = conn.run(f"echo {config_dir}", hide=True)
    full_config_dir = result.stdout.strip()
    config_file = f"{full_config_dir}/uv.toml"
    
    # 使用 tee 写入配置文件
    conn.run(f"tee {config_file} > /dev/null << 'EOF'\n{config_content}EOF", env=ENV_LANG_C)
    print(f"[OK] UV 配置文件已写入: {config_file} (模板: {template})")
    # endregion

# endregion
