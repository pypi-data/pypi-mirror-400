"""架构转换工具模块"""

# 架构映射表 (uname -m -> dpkg architecture)
ARCH_MAP = {
    "x86_64": "amd64",
    "aarch64": "arm64",
    "armv7l": "armhf",
    "i686": "i386",
    "i386": "i386",
}


def normalize_arch(uname_arch: str) -> str:
    """将 uname -m 输出转换为 dpkg 架构格式

    Args:
        uname_arch: uname -m 的输出 (如 x86_64, aarch64)

    Returns:
        dpkg 架构名称 (如 amd64, arm64)
    """
    return ARCH_MAP.get(uname_arch, uname_arch)
