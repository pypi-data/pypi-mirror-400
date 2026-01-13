import os
import shutil
import tempfile
import uuid
from pathlib import Path


def create_md_tmpfile(
    original_file: str, prefix: str = "pandoc2pdf_", verbose: bool = False
) -> tuple[int, str]:
    """创建临时.md 文件，与原始文件在同一目录"""
    input_path = Path(original_file)

    # 使用 tempfile.mkstemp 创建临时文件
    temp_fd, temp_path = tempfile.mkstemp(suffix=".md", prefix=prefix, dir=input_path.parent)

    if verbose:
        print(f"  ✓ 创建临时文件：{temp_path}")

    return temp_fd, temp_path


def write_to_tmpfile(
    temp_fd: int, content: str, encoding: str = "utf-8", verbose: bool = False
) -> None:
    """将内容写入临时文件"""
    try:
        with os.fdopen(temp_fd, "w", encoding=encoding) as f:
            f.write(content)

        if verbose:
            print("  ✓ 成功写入临时文件")
    except OSError as e:
        raise OSError(f"写入临时文件失败：{e}") from e


def cleanup_tmpfile(temp_file: str, verbose: bool = False) -> None:
    """清理临时文件"""
    try:
        if Path(temp_file).exists():
            Path(temp_file).unlink()

        if verbose:
            print(f"  ✓ 已删除临时文件：{temp_file}")
    except OSError as e:
        raise OSError(f"清理临时文件失败：{e}") from e


# ============================================================
# 沙箱管理函数
# ============================================================


def create_sandbox(tmp_dir: Path, prefix: str = "md2pdf_", verbose: bool = False) -> Path:
    """
    在临时目录中创建隔离沙箱

    Args:
        tmp_dir: 临时目录根路径（如 workspace/tmp）
        prefix: 沙箱目录前缀
        verbose: 是否显示详细信息

    Returns:
        沙箱目录路径
    """
    sandbox_name = f"{prefix}{uuid.uuid4().hex[:8]}"
    sandbox_path = tmp_dir / sandbox_name
    sandbox_path.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"  ✓ 创建沙箱目录：{sandbox_path}")

    return sandbox_path


def link_input_dir(sandbox: Path, input_dir: Path, verbose: bool = False) -> Path:
    """
    在沙箱中创建指向输入目录的符号链接

    注意：当前 core.py 中直接遍历子目录创建 symlink，此函数保留作为备用。
    可用于未来整体链接输入目录的场景（如 Docker 容器挂载）。

    Args:
        sandbox: 沙箱目录路径
        input_dir: 输入目录路径（如 workspace/in）
        verbose: 是否显示详细信息

    Returns:
        符号链接路径
    """
    link_path = sandbox / input_dir.name  # e.g., sandbox/in

    # 如果已存在则删除
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()

    # 创建符号链接
    link_path.symlink_to(input_dir.resolve())

    if verbose:
        print(f"  ✓ 创建符号链接：{link_path} -> {input_dir}")

    return link_path


def cleanup_sandbox(sandbox: Path, verbose: bool = False) -> None:
    """
    清理整个沙箱目录

    Args:
        sandbox: 沙箱目录路径
        verbose: 是否显示详细信息
    """
    try:
        if sandbox.exists():
            shutil.rmtree(sandbox)

            if verbose:
                print(f"  ✓ 已清理沙箱：{sandbox}")
    except Exception as e:
        if verbose:
            print(f"  ✗ 清理沙箱失败：{e}")


def link_images_dir(sandbox: Path, input_dir: Path, verbose: bool = False) -> Path | None:
    """
    在沙箱中创建指向输入目录下 images/ 的符号链接

    约定：图片必须放置在 in/images/ 目录中。

    Args:
        sandbox: 沙箱目录路径
        input_dir: 输入目录路径（如 workspace/in）
        verbose: 是否显示详细信息

    Returns:
        符号链接路径，如果 images 目录不存在则返回 None
    """
    images_dir = input_dir / "images"

    if not images_dir.exists():
        return None

    link_path = sandbox / "images"
    link_path.symlink_to(images_dir.resolve())

    if verbose:
        print(f"  ✓ 创建符号链接：images -> {images_dir}")

    return link_path
