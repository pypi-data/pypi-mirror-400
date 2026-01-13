"""
mark2pdf - 配置管理模块

提供配置加载、解析和工作区初始化功能。
"""

from mark2pdf.core import convert_directory, convert_file, convert_from_string

from .config import (
    CONFIG_FILENAME,
    DEFAULT_CONFIG_CONTENT,
    ConfigManager,
    OptionsConfig,
    PathsConfig,
    PdfworkConfig,
    detect_workspace,
    get_code_root,
    init_workspace,
    load_frontmatter_yaml,
    resolve_template,
)
from .conversion import run_batch_conversion, run_conversion, run_directory_conversion

try:
    from importlib.metadata import version

    __version__ = version("mark2pdf")
except Exception:
    __version__ = "0.0.0"  # 开发模式下未安装时的回退值
__all__ = [
    "ConfigManager",
    "PdfworkConfig",
    "PathsConfig",
    "OptionsConfig",
    "get_code_root",
    "detect_workspace",
    "init_workspace",
    "load_frontmatter_yaml",
    "resolve_template",
    "run_batch_conversion",
    "run_conversion",
    "run_directory_conversion",
    "convert_file",
    "convert_from_string",
    "convert_directory",
    "CONFIG_FILENAME",
    "DEFAULT_CONFIG_CONTENT",
]
