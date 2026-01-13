"""
稿纸专用预处理模块

提供稿纸格式（方格纸）的 Markdown 预处理函数：
- center_with_cnspace: 用中文空格居中文本
- md_pre_process: 清理 frontmatter、移除空格、转换段落格式
- process_for_typ: 稿纸专用排版（标题居中、作者居中、正文段首缩进）
"""

from .gaozhi_preprocess import (
    center_with_cnspace,
    md_pre_process,
    process_for_typ,
)

__all__ = [
    "center_with_cnspace",
    "md_pre_process",
    "process_for_typ",
]
