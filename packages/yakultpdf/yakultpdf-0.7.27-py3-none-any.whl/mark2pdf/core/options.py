"""
转换配置选项
"""

from dataclasses import dataclass

from .defaults import DEFAULT_TEMPLATE


@dataclass
class ConversionOptions:
    """
    控制 Markdown 到 PDF 转换行为的选项集合
    """

    template: str = DEFAULT_TEMPLATE
    coverimg: str | None = None
    to_typst: bool = False
    savemd: bool = False
    removelink: bool = False
    tc: bool = False
    overwrite: bool = False
    force_filename: bool = False
    verbose: bool = False
