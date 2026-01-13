from pathlib import Path

import questionary
from fabric import task
from jinja2 import Template


# 模板目录路径
TEMPLATES_DIR = Path(__file__).parent / "templates"


@task
def gen_vagrantfile_interactive(_) -> None:
    """通过交互式问答生成 Vagrantfile"""
    # region 交互式获取参数
    hostname = questionary.text("虚拟机主机名:", default="u13").ask()
    hostip = questionary.text("私有网络 IP:", default="10.10.10.13").ask()
    hostcpu = questionary.text("CPU 核心数:", default="8").ask()
    hostmem = questionary.text("内存大小 (MB):", default="8192").ask()
    hostimg = questionary.text("Vagrant box 镜像:", default="vb/ubuntu_desktop2404").ask()
    hostport = questionary.text("SSH 端口转发:", default="10013").ask()
    output = questionary.text("输出文件名:", default="Vagrantfile").ask()
    create_dir = questionary.confirm("是否创建 hostname 文件夹:", default=False).ask()
    # endregion

    # region 调用 gen_vagrantfile 生成文件
    gen_vagrantfile(
        _,
        hostname=hostname,
        hostip=hostip,
        hostcpu=hostcpu,
        hostmem=hostmem,
        hostimg=hostimg,
        hostport=hostport,
        output=output,
        create_dir=create_dir,
    )
    # endregion


@task
def gen_vagrantfile(
    _,
    hostname: str = "vagrant-vm",
    hostip: str = "10.10.10.100",
    hostcpu: str = "2",
    hostmem: str = "2048",
    hostimg: str = "ubuntu/jammy64",
    hostport: str = "2222",
    output: str = "Vagrantfile",
    create_dir: bool = False,
) -> None:
    """根据模板在当前目录下生成 Vagrantfile

    Args:
        _: Fabric Context 对象 (本地任务不使用)
        hostname: 虚拟机主机名
        hostip: 虚拟机私有网络 IP
        hostcpu: CPU 核心数
        hostmem: 内存大小 (MB)
        hostimg: Vagrant box 镜像名称
        hostport: SSH 端口转发的主机端口
        output: 输出文件名
        create_dir: 是否在当前目录下创建以 hostname 命名的文件夹
    """
    # region 读取并渲染模板
    template_path = TEMPLATES_DIR / "Vagrantfile"
    template_content = template_path.read_text(encoding="utf-8")
    template = Template(template_content)

    rendered = template.render(
        hostname=hostname,
        hostip=hostip,
        hostcpu=hostcpu,
        hostmem=hostmem,
        hostimg=hostimg,
        hostport=hostport,
    )
    # endregion

    # region 确定输出路径并写入文件
    if create_dir:
        host_dir = Path(hostname)
        host_dir.mkdir(exist_ok=True)
        output_path = host_dir / output
    else:
        output_path = Path(output)

    output_path.write_text(rendered, encoding="utf-8", newline="\r\n")
    print(f"[OK] Vagrantfile 已生成: {output_path.absolute()}")
    # endregion
