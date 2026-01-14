import click
import os
import subprocess
import sys
import re
import shutil
from pathlib import Path
from typing import Tuple, List, Optional
from rich.console import Console
from rich.panel import Panel

console = Console()


def validateSifFile(sif_path: Path) -> Tuple[bool, str]:
    """验证 SIF 文件是否有效

    Args:
        sif_path: SIF 文件路径

    Returns:
        Tuple[bool, str]: (是否有效, 错误消息)
    """
    if not sif_path.exists():
        return False, f"SIF 文件不存在: {sif_path}"

    if not sif_path.is_file():
        return False, f"路径不是文件: {sif_path}"

    if not os.access(sif_path, os.R_OK):
        return False, f"SIF 文件不可读: {sif_path}"

    file_size = sif_path.stat().st_size
    if file_size == 0:
        return False, f"SIF 文件为空: {sif_path}"

    return True, ""


def validateImageUrl(image_url: str) -> Tuple[bool, str]:
    """验证 Docker 镜像 URL 格式

    Args:
        image_url: Docker 镜像 URL

    Returns:
        Tuple[bool, str]: (是否有效, 错误消息)
    """
    # 基本格式验证：registry/namespace/image:tag
    # 支持域名和 IP 地址（带端口号）
    pattern = r'^[a-zA-Z0-9\-\.]+(:[0-9]+)?(/[a-zA-Z0-9\-_]+)+:[a-zA-Z0-9\.\-_]+$'

    if not re.match(pattern, image_url):
        return False, "镜像 URL 格式不正确，应为 registry/namespace/image:tag"

    return True, ""


def checkCommandAvailable(command: str) -> Tuple[bool, str, str]:
    """检查命令是否可用

    Args:
        command: 命令名称

    Returns:
        Tuple[bool, str, str]: (是否可用, 安装提示, URL)
    """
    # 使用 which 命令检测命令是否存在（更可靠）
    try:
        result = subprocess.run(
            ['which', command],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return True, "", ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 如果 which 不可用，尝试直接运行命令
    try:
        # 对于 split，尝试运行一个简单的命令
        if command == 'split':
            # 使用 --help 而不是 --version（macOS 的 split 不支持 --version）
            result = subprocess.run(
                ['split', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "", ""
        else:
            # 其他命令尝试 --version
            result = subprocess.run(
                [command, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "", ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 命令不可用，返回安装提示
    install_hints = {
        'split': (
            "split 命令未找到",
            "split 是 macOS/Linux 系统自带命令\n\n"
            "macOS: 已预装（如果提示缺少，请安装 Xcode Command Line Tools）\n"
            "  xcode-select --install\n\n"
            "Linux: sudo apt-get install coreutils / sudo yum install coreutils"
        ),
        'docker': (
            "Docker 未安装或未运行",
            "Docker 是容器化平台\n\n"
            "macOS: 下载并安装 Docker Desktop\n"
            "  https://www.docker.com/products/docker-desktop/\n\n"
            "Linux: 安装 Docker Engine\n"
            "  https://docs.docker.com/engine/install/\n\n"
            "安装后请确保 Docker daemon 正在运行"
        )
    }

    if command in install_hints:
        hint, url = install_hints[command]
        return False, hint, url

    return False, f"{command} 命令未找到", ""


def checkDockerEnvironment() -> Tuple[bool, List[str]]:
    """检查 Docker 是否可用

    Returns:
        Tuple[bool, List[str]]: (是否可用, 错误消息列表)
    """
    errors = []

    # 检查 Docker 命令
    docker_available, docker_hint, docker_url = checkCommandAvailable('docker')
    if not docker_available:
        errors.append(f"❌ {docker_hint}")
        if docker_url:
            errors.append(f"\n{docker_url}")
    else:
        # 检查 Docker daemon 是否运行
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                errors.append("\n⚠️  Docker daemon 未运行，请启动 Docker")
        except Exception:
            pass

    return len(errors) == 0, errors


def checkRequiredCommands() -> Tuple[bool, List[str]]:
    """检查所有必需的命令

    Returns:
        Tuple[bool, List[str]]: (是否全部可用, 错误消息列表)
    """
    all_errors = []

    # 检查 split 命令
    split_available, split_hint, split_url = checkCommandAvailable('split')
    if not split_available:
        error_msg = f"❌ {split_hint}"
        if split_url:
            error_msg += f"\n\n{split_url}"
        all_errors.append(error_msg)

    # 检查 Docker
    docker_available, docker_errors = checkDockerEnvironment()
    if not docker_available:
        all_errors.extend(docker_errors)

    return len(all_errors) == 0, all_errors


def createWorkDir(sif_path: Path) -> Path:
    """创建临时工作目录

    Args:
        sif_path: SIF 文件路径

    Returns:
        Path: 工作目录路径
    """
    parent_dir = sif_path.parent
    work_dir = parent_dir / ".sif_build_temp"
    work_dir.mkdir(parents=True, exist_ok=True)
    return work_dir


def calculateOptimalChunkSize(file_size_bytes: int) -> Optional[str]:
    """根据文件大小自适应计算切片大小

    Args:
        file_size_bytes: 文件大小（字节）

    Returns:
        Optional[str]: 切片大小（如 '100M', '500M'），None 表示不切片
    """
    size_mb = file_size_bytes / (1024 * 1024)

    if size_mb < 500:
        return None  # 不切片
    elif size_mb < 2 * 1024:
        return "100M"
    elif size_mb < 10 * 1024:
        return "500M"
    else:
        return "1G"


def splitSifFile(sif_path: Path, chunk_size: Optional[str], work_dir: Path) -> List[Path]:
    """切片 SIF 文件

    Args:
        sif_path: SIF 文件路径
        chunk_size: 切片大小（如 '100M'），None 表示不切片
        work_dir: 工作目录

    Returns:
        List[Path]: 切片文件列表

    Raises:
        subprocess.CalledProcessError: split 命令执行失败
    """
    if chunk_size is None:
        # 不切片，直接复制到工作目录
        dest_file = work_dir / sif_path.name
        shutil.copy2(sif_path, dest_file)
        return [dest_file]

    # 使用 split 命令切片
    output_prefix = sif_path.name  # 不包含路径
    cmd = ['split', '-b', chunk_size, '-d', str(sif_path), output_prefix + '.']

    result = subprocess.run(
        cmd,
        cwd=work_dir,
        capture_output=True,
        text=True,
        check=True
    )

    # 查找所有切片文件
    chunks = sorted(work_dir.glob(f"{output_prefix}.*"))
    return chunks


def generateDockerfile(work_dir: Path) -> Path:
    """生成 Dockerfile

    Args:
        work_dir: 工作目录

    Returns:
        Path: Dockerfile 文件路径
    """
    dockerfile_path = work_dir / "Dockerfile"

    dockerfile_content = """FROM alpine
COPY . /sif
"""

    with open(dockerfile_path, 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)

    return dockerfile_path


def executeCommand(cmd: List[str], description: str, console: Console) -> bool:
    """执行命令并实时显示输出

    Args:
        cmd: 命令列表
        description: 命令描述
        console: Console 实例

    Returns:
        bool: 是否执行成功
    """
    console.print(f"\n[dim]执行命令: {' '.join(cmd)}[/dim]")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # 实时显示输出
        for line in process.stdout:
            console.print(line.rstrip())

        process.wait()
        return process.returncode == 0

    except Exception as e:
        console.print(f"[red]命令执行异常: {str(e)}[/red]")
        return False


def buildDockerImage(work_dir: Path, image_url: str, console: Console) -> bool:
    """构建 Docker 镜像

    Args:
        work_dir: 工作目录
        image_url: 镜像 URL
        console: Console 实例

    Returns:
        bool: 是否构建成功
    """
    # 指定架构为 x86_64，确保在不同平台上的兼容性
    cmd = ['docker', 'build', '--platform', 'linux/amd64', '-t', image_url, str(work_dir)]
    return executeCommand(cmd, "构建 Docker 镜像", console)


def pushDockerImage(image_url: str, username: Optional[str], password: Optional[str], console: Console) -> bool:
    """推送 Docker 镜像

    Args:
        image_url: 镜像 URL
        username: 用户名
        password: 密码
        console: Console 实例

    Returns:
        bool: 是否推送成功
    """
    # 如果提供了认证信息，先执行 docker login
    if username and password:
        console.print("\n[bold blue]🔐 登录 Docker 仓库[/bold blue]")

        # 从镜像 URL 提取 registry
        registry = image_url.split('/')[0]

        # 使用 stdin 传递密码
        cmd = ['docker', 'login', '-u', username, '--password-stdin', registry]

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            stdout, stderr = process.communicate(input=password)

            if process.returncode != 0:
                console.print(f"[red]登录失败: {stderr}[/red]")
                return False

            console.print("[green]✓ 登录成功[/green]")
        except Exception as e:
            console.print(f"[red]登录异常: {str(e)}[/red]")
            return False

    # 推送镜像
    cmd = ['docker', 'push', image_url]
    return executeCommand(cmd, "推送 Docker 镜像", console)


def cleanupTempFiles(work_dir: Path, keep_temp: bool, console: Console):
    """清理临时文件

    Args:
        work_dir: 工作目录
        keep_temp: 是否保留临时文件
        console: Console 实例
    """
    if keep_temp:
        console.print(f"\n[dim]临时文件保留在: {work_dir}[/dim]")
        return

    console.print(f"\n[bold blue]🧹 清理临时文件[/bold blue]")

    try:
        shutil.rmtree(work_dir)
        console.print(f"[green]✓ 已清理: {work_dir}[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠️  清理失败: {str(e)}[/yellow]")


@click.group()
def sif():
    """SIF 文件管理命令"""
    pass


@sif.command(name='upload')
@click.argument('sif_file', type=click.Path(exists=True))
@click.argument('image_url')
@click.option('--username', help='Docker 仓库用户名')
@click.option('--password', help='Docker 仓库密码')
@click.option('--chunk-size', help='覆盖自适应计算的切片大小（如 100M, 500M）')
@click.option('--keep-temp', is_flag=True, help='保留临时文件')
def upload(sif_file, image_url, username, password, chunk_size, keep_temp):
    """将 SIF 文件切片并构建 Docker 镜像推送到仓库

    切片策略：
    - 文件 < 500MB：不切片，直接使用原文件
    - 文件 500MB-2GB：切片大小 100MB
    - 文件 2GB-10GB：切片大小 500MB
    - 文件 > 10GB：切片大小 1GB

    可通过 --chunk-size 参数覆盖自适应策略

    示例:
        adam-cli sif upload ./xxx.sif xxx.cn-hangzhou.cr.aliyuncs.com/openscore/openscore-core:1.0.0
        adam-cli sif upload ./xxx.sif registry.example.com/myimage:latest --username user --password pass
    """
    sif_path = Path(sif_file).resolve()
    file_size = sif_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)

    # 显示开始面板
    console.print(Panel.fit(
        f"[bold blue]🚀 开始构建 SIF Docker 镜像[/bold blue]\n"
        f"SIF 文件: {sif_path.name}\n"
        f"文件大小: {file_size_mb:.2f} MB\n"
        f"目标镜像: {image_url}",
        border_style="blue"
    ))

    work_dir = None

    try:
        # ===== 步骤 1: 验证环境 =====
        console.print("\n[bold blue]📦 步骤 1/5: 验证环境[/bold blue]")

        # 验证 SIF 文件
        valid, error_msg = validateSifFile(sif_path)
        if not valid:
            console.print(Panel.fit(
                f"[bold red]❌ SIF 文件验证失败[/bold red]\n{error_msg}",
                border_style="red"
            ))
            sys.exit(1)
        console.print("   ✓ SIF 文件可读")

        # 验证镜像 URL
        valid, error_msg = validateImageUrl(image_url)
        if not valid:
            console.print(Panel.fit(
                f"[bold red]❌ 镜像 URL 验证失败[/bold red]\n{error_msg}",
                border_style="red"
            ))
            sys.exit(1)
        console.print("   ✓ 镜像 URL 格式正确")

        # 检查所有必需的命令
        all_available, errors = checkRequiredCommands()
        if not all_available:
            console.print(Panel.fit(
                "[bold red]❌ 环境检查失败[/bold red]\n"
                + "\n".join(errors),
                border_style="red"
            ))
            sys.exit(1)
        console.print("   ✓ split 命令可用")
        console.print("   ✓ Docker 已安装并运行")

        # ===== 步骤 2: 创建工作目录 =====
        console.print("\n[bold blue]📦 步骤 2/5: 创建工作目录[/bold blue]")
        work_dir = createWorkDir(sif_path)
        console.print(f"   ✓ 工作目录: {work_dir}")

        # ===== 步骤 3: 切片 SIF 文件 =====
        console.print("\n[bold blue]📦 步骤 3/5: 切片 SIF 文件[/bold blue]")

        # 计算切片大小
        if chunk_size:
            actual_chunk_size = chunk_size
            console.print(f"   切片策略: 自定义 ({chunk_size})")
        else:
            actual_chunk_size = calculateOptimalChunkSize(file_size)
            if actual_chunk_size:
                console.print(f"   切片策略: 自适应 ({actual_chunk_size})")
            else:
                console.print(f"   切片策略: 不切片 (文件 < 500MB)")

        console.print(f"   文件大小: {file_size_mb:.2f} MB")

        # 执行切片
        try:
            chunks = splitSifFile(sif_path, actual_chunk_size, work_dir)
            console.print(f"   ✓ 切片完成: {len(chunks)} 个文件")

            # 显示切片详情
            console.print(f"\n   📄 切片详情:")
            for chunk in chunks:
                chunk_size_mb = chunk.stat().st_size / (1024 * 1024)
                console.print(f"      - {chunk.name} ({chunk_size_mb:.2f} MB)")
        except subprocess.CalledProcessError as e:
            console.print(Panel.fit(
                f"[bold red]❌ SIF 文件切片失败[/bold red]\n"
                f"错误: {e.stderr}",
                border_style="red"
            ))
            cleanupTempFiles(work_dir, keep_temp, console)
            sys.exit(1)

        # ===== 步骤 4: 生成 Dockerfile =====
        console.print("\n[bold blue]📦 步骤 4/5: 生成 Dockerfile[/bold blue]")
        dockerfile_path = generateDockerfile(work_dir)
        console.print(f"   ✓ Dockerfile 已生成")

        # ===== 步骤 5: 构建 Docker 镜像 =====
        console.print("\n[bold blue]📦 步骤 5/5: 构建 Docker 镜像[/bold blue]")

        if not buildDockerImage(work_dir, image_url, console):
            console.print(Panel.fit(
                f"[bold red]❌ Docker 镜像构建失败[/bold red]",
                border_style="red"
            ))
            cleanupTempFiles(work_dir, keep_temp, console)
            sys.exit(1)

        console.print("[green]   ✓ 镜像构建成功[/green]")

        # ===== 步骤 6: 推送 Docker 镜像 =====
        console.print("\n[bold blue]📦 步骤 6/6: 推送 Docker 镜像[/bold blue]")

        if not pushDockerImage(image_url, username, password, console):
            console.print(Panel.fit(
                f"[bold red]❌ Docker 镜像推送失败[/bold red]\n"
                f"请检查网络连接和仓库认证信息",
                border_style="red"
            ))
            cleanupTempFiles(work_dir, keep_temp, console)
            sys.exit(1)

        console.print("[green]   ✓ 镜像推送成功[/green]")

        # ===== 成功 =====
        console.print(Panel.fit(
            f"[bold green]✅ 构建成功！[/bold green]\n"
            f"镜像: {image_url}\n"
            f"大小: {file_size_mb:.2f} MB\n"
            f"切片数: {len(chunks)}",
            border_style="green"
        ))

        # 清理临时文件
        cleanupTempFiles(work_dir, keep_temp, console)

    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]❌ 执行过程中出现异常[/bold red]\n"
            f"错误: {str(e)}",
            border_style="red"
        ))
        if work_dir:
            cleanupTempFiles(work_dir, keep_temp, console)
        sys.exit(1)


if __name__ == '__main__':
    sifBuild()
