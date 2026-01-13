"""
Working Path Helper - 工作目录管理工具

提供安全的目录创建、文件路径解析和安全保存功能。
"""

from .helper_working_path import (
    create_working_dirs,
    get_project_root,
    resolve_inout_paths,
    resolve_template_path,
    safesave_path,
)

__version__ = "1.0.0"
__all__ = [
    "get_project_root",
    "create_working_dirs",
    "safesave_path",
    "resolve_inout_paths",
    "resolve_template_path",
]
