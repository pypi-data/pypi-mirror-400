"""
Configuration and workspace utilities for mark2pdf.
"""

from .defaults import CONFIG_FILENAME, DEFAULT_CONFIG_CONTENT
from .loader import ConfigManager, get_code_root, load_frontmatter_yaml, resolve_template
from .reporter import print_config_report, print_execution_plan
from .types import OptionsConfig, PathsConfig, PdfworkConfig
from .workspace import (
    detect_workspace,
    init_workspace,
    install_template,
)

__all__ = [
    "ConfigManager",
    "PdfworkConfig",
    "PathsConfig",
    "OptionsConfig",
    "get_code_root",
    "detect_workspace",
    "init_workspace",
    "install_template",
    "load_frontmatter_yaml",
    "resolve_template",
    "print_config_report",
    "print_execution_plan",
    "CONFIG_FILENAME",
    "DEFAULT_CONFIG_CONTENT",
]
