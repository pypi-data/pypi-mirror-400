"""
后处理器加载器

提供 load_postprocessor 函数，先从工作区 postprocess 目录加载，再回退到预设处理器。
"""

from collections.abc import Callable
from importlib import util
from pathlib import Path


def _load_from_workspace(name: str) -> Callable[[str], str] | None:
    """从工作区 postprocess 目录加载处理器"""
    workspace_postprocess = Path.cwd() / "postprocess"
    if not workspace_postprocess.is_dir():
        return None

    # 尝试从 __init__.py 导入
    init_file = workspace_postprocess / "__init__.py"
    if init_file.exists():
        spec = util.spec_from_file_location("_workspace_postprocess", init_file)
        if spec and spec.loader:
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
            processor = getattr(module, name, None)
            if callable(processor):
                return processor

    # 尝试从单独的模块文件导入
    module_file = workspace_postprocess / f"{name}.py"
    if module_file.exists():
        spec = util.spec_from_file_location(f"_workspace_{name}", module_file)
        if spec and spec.loader:
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
            processor = getattr(module, "process", None)
            if callable(processor):
                return processor

    return None


def load_postprocessor(name: str) -> Callable[[str], str] | None:
    """
    加载后处理器

    优先从工作区 postprocess 目录加载，再回退到预设处理器包。

    Args:
        name: 处理器名称（如 "remove_links", "to_traditional_chinese", "convert_divs"）

    Returns:
        处理器函数，或 None（未找到）
    """
    # 1. 先从工作区加载
    processor = _load_from_workspace(name)
    if processor:
        return processor

    # 2. 回退到预设 postprocess 包
    try:
        from mark2pdf import postprocess as builtin_postprocess

        processor = getattr(builtin_postprocess, name, None)
        if callable(processor):
            return processor
    except ImportError:
        pass

    return None


def ensure_tc_postprocess(
    postprocess: Callable[[str], str] | None,
) -> Callable[[str], str]:
    """
    确保后处理链包含繁体转换。

    如果已有处理器链包含繁体转换，则直接返回原处理器。
    """
    from mark2pdf.postprocess.to_traditional_chinese import process as tc_process

    if postprocess is None:
        return tc_process
    if postprocess is tc_process:
        return postprocess
    if getattr(postprocess, "_mark2pdf_handles_tc", False):
        return postprocess

    def combined(content: str) -> str:
        content = postprocess(content)
        return tc_process(content)

    combined._mark2pdf_handles_tc = True  # type: ignore[attr-defined]
    return combined
