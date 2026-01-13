"""
mark2pdf.core - Markdown 到 PDF 转换器

使用 Pandoc 和 Typst 将 Markdown 文件转换为 PDF。

核心 API:
    - convert_file: 转换单个 Markdown 文件
    - convert_from_string: 转换内存 Markdown 字符串
    - convert_directory: 转换整个目录（合并后转换）

CLI:
    - cli: Click CLI 入口点
"""

from .core import convert_file, convert_from_string
from .directory import convert_directory, merge_directory_markdown
from .options import ConversionOptions

try:
    from importlib.metadata import version

    __version__ = version("mark2pdf")
except Exception:
    __version__ = "0.0.0"
__all__ = [
    "convert_file",
    "convert_from_string",
    "convert_directory",
    "merge_directory_markdown",
    "ConversionOptions",
]
