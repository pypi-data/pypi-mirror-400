
from ..decorators.singleton import Singleton
from fabric import Connection, Config
from pathlib import Path
from rich.console import Console
import logging
import questionary
import yaml

console = Console()
logging.getLogger("paramiko").setLevel(logging.CRITICAL)


def _find_config_file() -> Path:
    """向上遍历目录查找 iamt.yaml，找不到则返回当前目录下的路径"""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        # print(parent)
        candidate = parent / "iamt.yaml"
        if candidate.exists():
            return candidate
    return current / "iamt.yaml"


CONFIG_FILE = _find_config_file()


@Singleton
class ClientConfig():
    
    def __init__(self):
        self.hosts: dict[str, dict] = {}  # 所有 host 配置
        self.conn: Connection | None = None  # 当前连接
        self.hostvars: dict = {}  # 当前连接的主机信息
        self._current_host: str | None = None  # 当前连接的 host 名称
        
        if CONFIG_FILE.exists():
            self._load_all_hosts()
    
    # region 配置加载
    def _load_all_hosts(self) -> None:
        """从配置文件加载所有 host 信息"""
        config_data = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
        self.hosts = config_data.get("hosts", {})
    
    def get_host_names(self) -> list[str]:
        """获取所有可用的 host 名称"""
        return list(self.hosts.keys())
    
    def get_host_info(self, hostname: str) -> dict | None:
        """获取指定 host 的配置信息"""
        return self.hosts.get(hostname)
    # endregion
    
    # region 连接管理
    def connect(self, hostname: str | None = None) -> Connection | None:
        """
        连接到指定的 host，如果不指定则交互选择或使用第一个
        
        Args:
            hostname: host 名称，为 None 时自动选择
            
        Returns:
            Connection 对象，失败返回 None
        """
        # 如果已连接到同一 host，直接返回
        if hostname and hostname == self._current_host and self.conn:
            return self.conn
        
        # 关闭现有连接
        self.disconnect()
        
        # 确定要连接的 host
        if not self.hosts:
            info = self.collect_server_info()
            if info is None or not info.get("host"):
                console.print("[yellow]⚠[/yellow] 未提供服务器地址，退出")
                return None
            self.conn = self._create_connection_from_info(info)
        else:
            hostname = self._resolve_hostname(hostname)
            if hostname is None:
                return None
            host_info = self.hosts[hostname]
            self.conn = self._create_connection_from_info(host_info)
            self._current_host = hostname
        
        if self.conn is None:
            return None
        
        self.hostvars = self._gather_facts()
        self.conn.hostvars = self.hostvars
        return self.conn
    
    def _resolve_hostname(self, hostname: str | None) -> str | None:
        """解析 hostname，为 None 时自动选择"""
        if hostname:
            if hostname not in self.hosts:
                console.print(f"[red]✗[/red] 未找到 host: [bold]{hostname}[/bold]，可用: {', '.join(self.hosts.keys())}")
                return None
            return hostname
        
        # 只有一个 host 时直接使用
        if len(self.hosts) == 1:
            return next(iter(self.hosts))
        
        # 多个 host 时交互选择，显示详细信息
        choices = []
        for name, info in self.hosts.items():
            host = info.get("host", "")
            user = info.get("user", "")
            port = info.get("port", "22")
            label = f"{name} ({user}@{host}:{port})"
            choices.append(questionary.Choice(title=label, value=name))
        
        selected = questionary.select("请选择要连接的服务器:", choices=choices).ask()
        return selected
    
    def disconnect(self) -> None:
        """断开当前连接"""
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
            self.hostvars = {}
            self._current_host = None
    
    def _create_connection_from_info(self, host_info: dict) -> Connection | None:
        """根据 host_info 创建连接"""
        config = Config(overrides={"sudo": {"password": host_info["sudo_password"]}})
        try:
            conn = Connection(
                host=host_info["host"],
                port=int(host_info.get("port", 22)),
                user=host_info["user"],
                connect_kwargs={"password": host_info["password"]},
                config=config,
            )
            conn.open()
            return conn
        except Exception:
            console.print("[red]✗[/red] 连接服务器失败")
            return None
    # endregion 
                
        
        
    # region 用户输入收集
    def collect_server_info(self) -> dict[str, str] | None:
        """通过交互式问答收集服务器连接信息并写入 iamt.yaml，用户取消时返回 None"""
        hostname = questionary.text("请输入主机名 (用于标识此服务器):").ask()
        if hostname is None:
            return None

        ip = questionary.text("请输入服务器IP地址:").ask()
        if ip is None:
            return None

        port = questionary.text("请输入SSH端口:", default="22").ask()
        if port is None:
            return None

        username = questionary.text("请输入用户名:", default="vagrant").ask()
        if username is None:
            return None

        password = questionary.password("请输入密码:", default="vagrant").ask()
        if password is None:
            return None

        sudo_password = questionary.password("请输入SUDO密码 (留空则与登录密码相同):").ask()
        if sudo_password is None:
            return None

        host_entry = {
            "host": ip,
            "port": port,
            "user": username,
            "password": password,
            "sudo_password": sudo_password or password,
        }
        config_data = {"hosts": {hostname: host_entry}}
        
        confirm = questionary.confirm(f"是否将配置写入 {CONFIG_FILE}?", default=True).ask()
        if confirm is None or not confirm:
            console.print("[yellow]⚠[/yellow] 用户取消写入配置文件")
            return host_entry
        
        # 手动格式化为 flow style: hosts:\n  hostname: {key: value, ...}
        flow_entry = yaml.dump(host_entry, default_flow_style=True, allow_unicode=True).strip()
        yaml_content = f"hosts:\n  {hostname}: {flow_entry}\n"
        CONFIG_FILE.write_text(yaml_content, encoding="utf-8")
        return host_entry
    # endregion
    

    
    # region 主机信息收集
    def _gather_facts(self) -> dict:
        """收集主机基础信息，类似 Ansible setup 模块"""
        facts = {}
        
        # 发行版信息
        os_release = self._run_cmd("cat /etc/os-release 2>/dev/null || cat /etc/*-release 2>/dev/null | head -20")
        facts["distribution"] = self._parse_os_release(os_release)
        
        # 主机名
        facts["hostname"] = self._run_cmd("hostname").strip()
        facts["fqdn"] = self._run_cmd("hostname -f 2>/dev/null || hostname").strip()
        
        # 内核信息
        facts["kernel"] = self._run_cmd("uname -r").strip()
        facts["architecture"] = self._run_cmd("uname -m").strip()
        
        # 内存信息 (KB)
        meminfo = self._run_cmd("cat /proc/meminfo")
        facts["memory"] = self._parse_meminfo(meminfo)
        
        # CPU 信息
        facts["processor_count"] = int(self._run_cmd("nproc").strip() or "1")
        
        # 网络接口
        facts["default_ipv4"] = self._get_default_ipv4()
        
        # 用户信息
        facts["user"] = self._run_cmd("whoami").strip()
        facts["user_home"] = self._run_cmd("echo $HOME").strip()
        
        return facts
    
    def _run_cmd(self, cmd: str) -> str:
        """执行命令并返回输出，失败时返回空字符串"""
        try:
            result = self.conn.run(cmd, hide=True, warn=True)
            return result.stdout if result.ok else ""
        except Exception:
            return ""
    
    def _parse_os_release(self, content: str) -> dict:
        """解析 /etc/os-release 内容"""
        info = {"name": "", "version": "", "version_id": "", "codename": "", "id": "", "id_like": ""}
        for line in content.splitlines():
            if "=" in line:
                key, _, value = line.partition("=")
                value = value.strip('"\'')
                key_lower = key.lower()
                if key_lower == "name":
                    info["name"] = value
                elif key_lower == "version":
                    info["version"] = value
                elif key_lower == "version_id":
                    info["version_id"] = value
                elif key_lower == "version_codename":
                    info["codename"] = value
                elif key_lower == "id":
                    info["id"] = value
                elif key_lower == "id_like":
                    info["id_like"] = value
        # 如果 id_like 为空，使用 id 作为回退
        if not info["id_like"]:
            info["id_like"] = info["id"]
        return info
    
    def _parse_meminfo(self, content: str) -> dict:
        """解析 /proc/meminfo 内容，返回 MB 单位"""
        mem = {"total_mb": 0, "free_mb": 0, "available_mb": 0}
        for line in content.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                key, value = parts[0].rstrip(":"), parts[1]
                if key == "MemTotal":
                    mem["total_mb"] = int(value) // 1024
                elif key == "MemFree":
                    mem["free_mb"] = int(value) // 1024
                elif key == "MemAvailable":
                    mem["available_mb"] = int(value) // 1024
        return mem
    
    def _get_default_ipv4(self) -> dict:
        """获取默认 IPv4 地址和网关"""
        info = {"address": "", "gateway": "", "interface": ""}
        route = self._run_cmd("ip route get 1.1.1.1 2>/dev/null | head -1")
        if route:
            parts = route.split()
            for i, p in enumerate(parts):
                if p == "src" and i + 1 < len(parts):
                    info["address"] = parts[i + 1]
                elif p == "via" and i + 1 < len(parts):
                    info["gateway"] = parts[i + 1]
                elif p == "dev" and i + 1 < len(parts):
                    info["interface"] = parts[i + 1]
        return info
    # endregion