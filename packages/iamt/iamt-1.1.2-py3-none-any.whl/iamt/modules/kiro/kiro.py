import os
import urllib.request
from fabric import Connection, task

# Kiro IDE 下载配置
KIRO_VERSION = "0.8.0"
KIRO_DOWNLOAD_URL = f"https://prod.download.desktop.kiro.dev/releases/stable/linux-x64/signed/{KIRO_VERSION}/deb/kiro-ide-{KIRO_VERSION}-stable-linux-x64.deb"
KIRO_DEB_FILENAME = f"kiro-ide-{KIRO_VERSION}-stable-linux-x64.deb"


# region Kiro IDE 安装任务


def download_kiro_deb(dest_dir: str = ".") -> str:
    """下载 Kiro IDE deb 安装包到本地主机
    
    Args:
        dest_dir: 下载目标目录，默认为当前目录
        
    Returns:
        下载后的 deb 文件路径
    """
    print(f"\n[任务] 下载 Kiro IDE {KIRO_VERSION}")
    
    deb_path = os.path.join(dest_dir, KIRO_DEB_FILENAME)
    
    # 检查文件是否已存在
    if os.path.exists(deb_path):
        print(f"  deb 文件已存在: {deb_path}")
        return deb_path
    
    # 下载 deb 并显示进度
    print(f"  正在下载: {KIRO_DOWNLOAD_URL}")
    
    def progress_hook(block_num: int, block_size: int, total_size: int) -> None:
        if total_size > 0:
            percent = min(100, block_num * block_size * 100 // total_size)
            print(f"\r  下载进度: {percent}%", end="", flush=True)
    
    urllib.request.urlretrieve(KIRO_DOWNLOAD_URL, deb_path, progress_hook)
    print(f"\n  下载完成: {deb_path}")
    
    return deb_path


@task
def install_kiro(conn: Connection) -> None:
    """下载、上传并安装 Kiro IDE deb 包"""
    # region 下载 deb 包到本地
    deb_path = download_kiro_deb()
    # endregion
    
    # region 上传 deb 包到服务器
    print(f"\n[任务] 上传 deb 包到服务器")
    remote_deb_path = f"/tmp/{KIRO_DEB_FILENAME}"
    conn.put(deb_path, remote_deb_path)
    print(f"  上传完成: {remote_deb_path}")
    # endregion
    
    # region 安装 deb 包
    print(f"\n[任务] 安装 Kiro IDE")
    # 使用 dpkg 安装，如果有依赖问题则用 apt-get -f install 修复
    conn.sudo(f"dpkg -i {remote_deb_path}", warn=True)
    conn.sudo("apt-get install -f -y", warn=True)
    print("  安装完成")
    # endregion


# endregion
