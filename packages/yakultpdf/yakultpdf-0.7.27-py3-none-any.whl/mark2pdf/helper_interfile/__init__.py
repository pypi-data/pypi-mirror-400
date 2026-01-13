"""
中间文件管理模块 (Intermediate File Manager)

提供临时.md 文件的创建、写入和清理功能
"""

from .interfile_manager import (
    cleanup_tmpfile,
    create_md_tmpfile,
    write_to_tmpfile,
)

__all__ = ["create_md_tmpfile", "write_to_tmpfile", "cleanup_tmpfile"]
