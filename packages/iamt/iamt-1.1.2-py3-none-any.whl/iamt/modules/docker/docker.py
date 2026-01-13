"""Docker 模块 - 在远程 Linux 虚拟机上安装和配置 Docker CE

该模块遵循项目现有的 Fabric task 模式，通过 SSH 连接执行远程命令，
实现 Docker 的自动化部署。
"""

from pathlib import Path

from fabric import Connection, task


# region 模块常量配置

# 模板目录路径
TEMPLATES_DIR = Path(__file__).parent / "templates"
DAEMON_TEMPLATES_DIR = TEMPLATES_DIR / "daemon"

# Docker 版本配置
DOCKER_EDITION = "ce"  # Community Edition

# 旧版本包列表 (需要卸载以避免冲突)
DOCKER_OBSOLETE_PACKAGES = [
    "docker",
    "docker.io",
    "docker-engine",
    "podman-docker",
    "containerd",
    "runc",
]

# 环境变量 (使用英文输出避免中文乱码)
ENV_LANG_C = {"LANG": "C", "LC_ALL": "C"}

# endregion


# region Task 函数

@task 
def apt_update(conn:Connection):
    conn.sudo("apt-get update")


@task
def uninstall_old_docker(conn: Connection) -> None:
    """卸载旧版本 Docker 相关包

    检查并卸载以下旧包以避免与新版本冲突:
    docker, docker.io, docker-engine, podman-docker, containerd, runc

    如果旧包不存在，将跳过卸载并继续执行。
    """
    packages = " ".join(DOCKER_OBSOLETE_PACKAGES)
    conn.sudo(f"apt-get remove -y {packages}", warn=True, env=ENV_LANG_C)


@task
def install_dependencies(conn: Connection) -> None:
    """安装 Docker 所需依赖包"""
    conn.sudo(f"apt-get install -y apt-transport-https ca-certificates curl", env=ENV_LANG_C)


# GPG 密钥配置
DOCKER_GPG_PATH = "/etc/apt/keyrings/docker.asc"
DOCKER_GPG_TEMPLATES_DIR = TEMPLATES_DIR / "gpgkey"
DOCKER_GPG_SHA256 = {
    "debian": "1500c1f56fa9e26b9b8f42452a553675796ade0807cdce11975eb98170b3a570",
    "ubuntu": "1500c1f56fa9e26b9b8f42452a553675796ade0807cdce11975eb98170b3a570",
}


@task
def setup_gpg_key(conn: Connection, distro: str | None = None) -> bool:
    """配置 Docker GPG 密钥

    优先从本地模板上传 GPG 密钥，避免国内网络下载困难

    Args:
        conn: Fabric 连接对象
        distro: 发行版名称 (debian/ubuntu)，默认从 hostvars 获取

    Returns:
        GPG 密钥校验是否通过
    """
    # region 获取发行版
    if distro is None:
        distro = conn.hostvars["distribution"]["id"]
    # endregion

    # region 创建 keyrings 目录
    conn.sudo("install -m 0755 -d /etc/apt/keyrings", env=ENV_LANG_C)
    # endregion

    # region 上传本地 GPG 密钥
    local_gpg_file = DOCKER_GPG_TEMPLATES_DIR / f"{distro}_gpgkey"
    remote_tmp_path = f"/tmp/{distro}_gpgkey"
    conn.put(str(local_gpg_file), remote_tmp_path)
    conn.sudo(f"mv {remote_tmp_path} {DOCKER_GPG_PATH}", env=ENV_LANG_C)
    conn.sudo(f"chmod a+r {DOCKER_GPG_PATH}", env=ENV_LANG_C)
    print(f"[OK] GPG key uploaded from local template: {local_gpg_file.name}")
    # endregion

    # region SHA256 校验
    expected_sha256 = DOCKER_GPG_SHA256.get(distro, "")
    if not expected_sha256:
        print(f"[WARN] No expected SHA256 for distro '{distro}', skipping verification")
        return True

    result = conn.sudo(f"sha256sum {DOCKER_GPG_PATH}", hide=True, env=ENV_LANG_C)
    actual_sha256 = result.stdout.strip().split()[0]

    if actual_sha256 == expected_sha256:
        print(f"[OK] GPG key SHA256 verified: {actual_sha256}")
        return True
    else:
        print(f"[WARN] GPG key SHA256 mismatch!")
        print(f"  Expected: {expected_sha256}")
        print(f"  Actual:   {actual_sha256}")
        return False
    # endregion


# 镜像源配置
DOCKER_MIRRORS = {
    "official": "https://download.docker.com",
    "cernet": "https://mirrors.cernet.edu.cn/docker-ce",
    "tuna": "https://mirrors.tuna.tsinghua.edu.cn/docker-ce",
    "aliyun": "https://mirrors.aliyun.com/docker-ce",
    "ustc": "https://mirrors.ustc.edu.cn/docker-ce",
}
DEFAULT_MIRROR = "cernet"

# APT 源格式模板
DOCKER_SOURCES_TEMPLATE = "deb [arch={arch} signed-by={gpg_path}] {mirror}/linux/{distro} {codename} stable\n"

@task
def setup_docker_repo(conn: Connection, mirror: str = DEFAULT_MIRROR) -> None:
    """配置 Docker APT 源

    1. 从 hostvars 获取发行版信息
    2. 调用 _generate_docker_sources 生成配置
    3. 写入 /etc/apt/sources.list.d/docker.list
    4. 执行 apt-get update 更新包索引

    Args:
        conn: Fabric 连接对象
        mirror: 镜像源名称 (official/cernet/tuna/aliyun/ustc) 或完整 URL
    """
    # region 从 hostvars 获取发行版信息
    distro = conn.hostvars["distribution"]["id"]
    codename = conn.hostvars["distribution"]["codename"]
    arch = normalize_arch(conn.hostvars["architecture"])
    # endregion      

    # region 生成并写入 APT 源配置
    sources_content = _generate_docker_sources(
        mirror=mirror,
        distro=distro,
        codename=codename,
        arch=arch,
    )
    docker_list_path = "/etc/apt/sources.list.d/docker.list"
    conn.sudo(f"tee {docker_list_path} > /dev/null << 'EOF'\n{sources_content}EOF", env=ENV_LANG_C)
    print(f"[OK] Docker APT source written to {docker_list_path}")
    # endregion

    # region 更新包索引
    conn.sudo("apt-get update", env=ENV_LANG_C)
    print("[OK] APT package index updated")
    # endregion


# Docker 包列表 (不含版本)
DOCKER_PACKAGES = [
    "docker-ce",
    "docker-ce-cli",
    "docker-ce-rootless-extras",
    "containerd.io",
    "docker-buildx-plugin",
]

@task
def install_docker(conn: Connection, version: str | None = None) -> None:
    """安装 Docker CE 及相关组件

    安装以下包: docker-ce, docker-ce-cli, docker-ce-rootless-extras,
    containerd.io, docker-buildx-plugin

    Args:
        conn: Fabric 连接对象
        version: Docker 版本号 (可选)，为空时安装最新版
    """
    packages = _build_docker_packages(version)
    packages_str = " ".join(packages)
    conn.sudo(f"apt-get install -y {packages_str}", env=ENV_LANG_C)
    print(f"[OK] Docker packages installed: {packages_str}")


@task
def install_docker_compose(conn: Connection) -> None:
    """安装 Docker Compose 插件

    安装 docker-compose-plugin 包以支持 docker compose 命令

    Args:
        conn: Fabric 连接对象
    """
    conn.sudo("apt-get install -y docker-compose-plugin", env=ENV_LANG_C)
    print("[OK] Docker Compose plugin installed")



@task
def configure_daemon(conn: Connection, template: str = "daemon_multi_mirrors.json") -> None:
    """配置 Docker daemon

    1. 确保 /etc/docker 目录存在且权限为 0755
    2. 从模板文件读取配置并写入 daemon.json

    Args:
        conn: Fabric 连接对象
        template: 模板文件名
    """
    # region 创建 /etc/docker 目录
    conn.sudo("install -m 0755 -d /etc/docker", env=ENV_LANG_C)
    # endregion

    # region 读取模板并写入 daemon.json
    template_path = DAEMON_TEMPLATES_DIR / template
    daemon_json = template_path.read_text(encoding="utf-8")
    daemon_path = "/etc/docker/daemon.json"
    conn.sudo(f"tee {daemon_path} > /dev/null << 'EOF'\n{daemon_json}EOF", env=ENV_LANG_C)
    print(f"[OK] Docker daemon config written to {daemon_path} (template: {template})")
    # endregion


@task
def start_docker(conn: Connection) -> None:
    """启动 Docker 服务
    """
    conn.sudo("systemctl start docker", env=ENV_LANG_C)
    print("[OK] Docker service started")


@task
def enable_docker(conn: Connection) -> None:
    """设置 Docker 服务开机自启"""
    conn.sudo("systemctl enable docker", env=ENV_LANG_C)
    print("[OK] Docker service enabled for auto-start")


@task
def restart_docker(conn: Connection) -> None:
    """重启 Docker 服务
    """
    conn.sudo("systemctl restart docker", env=ENV_LANG_C)
    print("[OK] Docker service restarted")


@task
def configure_docker_user(conn: Connection, username: str | None = None) -> None:
    """将用户添加到 docker 组

    1. 通过 getent 获取 docker 组信息
    2. 检查指定用户是否已在 docker 组中
    3. 如果用户不在 docker 组中，将用户添加到 docker 组
    4. 如果用户已在 docker 组中，跳过添加操作

    Args:
        conn: Fabric 连接对象
        username: 用户名，默认从 hostvars 获取当前用户
    """
    # region 确定目标用户名
    if username is None:
        username = conn.hostvars["user"]
    # endregion

    # region 获取 docker 组信息
    result = conn.sudo("getent group docker", hide=True, warn=True, env=ENV_LANG_C)
    if result.failed:
        print("[WARN] Docker group does not exist, skipping user configuration")
        return
    # endregion

    # region 检查用户是否已在 docker 组中
    members = _parse_group_members(result.stdout)
    if username in members:
        print(f"[OK] User '{username}' is already in docker group, skipping")
        return
    # endregion

    # region 添加用户到 docker 组
    conn.sudo(f"usermod -aG docker {username}", env=ENV_LANG_C)
    print(f"[OK] User '{username}' added to docker group")
    # endregion

    # region 重建 SSH 连接以刷新组成员身份
    conn.close()
    conn.open()
    print(f"[OK] SSH connection refreshed, group membership now active")
    # endregion




# endregion

# region 辅助函数


from iamt.modules._utils.arch import normalize_arch


def _generate_docker_sources(
    mirror: str,
    distro: str,
    codename: str,
    arch: str = "amd64",
    gpg_path: str = DOCKER_GPG_PATH,
) -> str:
    """生成 Docker APT 源配置字符串

    Args:
        mirror: 镜像源名称 (official/cernet/tuna/aliyun/ustc) 或完整 URL
        distro: 发行版名称 (debian/ubuntu)
        codename: 发行版代号 (如 bookworm, jammy)
        arch: 架构 (默认 amd64)
        gpg_path: GPG 密钥路径 (默认 /etc/apt/keyrings/docker.asc)

    Returns:
        符合 DEB822 格式的 APT 源配置字符串
    """
    mirror_url = DOCKER_MIRRORS.get(mirror, mirror)
    return DOCKER_SOURCES_TEMPLATE.format(
        arch=arch,
        gpg_path=gpg_path,
        mirror=mirror_url,
        distro=distro,
        codename=codename,
    )


def _build_docker_packages(version: str | None = None) -> list[str]:
    """构建 Docker 包名列表

    Args:
        version: Docker 版本号 (可选)，为空时安装最新版

    Returns:
        包含版本后缀 (如有) 的 Docker 包名列表
    """
    if version:
        return [f"{pkg}={version}" for pkg in DOCKER_PACKAGES]
    return DOCKER_PACKAGES.copy()


def _parse_group_members(getent_output: str) -> list[str]:
    """解析 getent group 输出，返回用户列表

    Args:
        getent_output: getent group 命令的输出 (格式: groupname:x:gid:user1,user2,...)

    Returns:
        组成员用户名列表，无成员时返回空列表
    """
    parts = getent_output.strip().split(":")
    if len(parts) < 4 or not parts[3]:
        return []
    return [u.strip() for u in parts[3].split(",") if u.strip()]


# endregion
