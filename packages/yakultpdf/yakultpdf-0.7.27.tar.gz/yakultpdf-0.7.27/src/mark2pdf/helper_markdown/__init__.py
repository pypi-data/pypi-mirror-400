"""
Markdown 预处理模块

包含所有以 pre 开头的预处理函数：
- pre_clean_frontmatter: 清理 YAML frontmatter
- pre_image_verify: 验证图片引用
- pre_remove_links: 移除链接（保留图片）
- pre_remove_titlestar: 去掉标题中的加粗标记
- pre_trim_whitespace: 去除每行前后的空格
- pre_add_line_breaks: 添加空行分隔，跳过表格、引用块、代码块
- pre_dash_to_star: 将下划线斜体改为星号加粗
- pre_for_typst_at: 将不在链接 URL 中的 @ 转义
- pre_for_typst_dollarmark: 将普通文本中的 $ 转义
- pre_for_typst: 组合多个 Typst 预处理函数

以及辅助函数：
- extract_frontmatter: 从 markdown 文件中提取 frontmatter
"""

from .md_preprocess import (
    extract_frontmatter,
    pre_add_line_breaks,
    pre_clean_frontmatter,
    pre_dash_to_star,
    pre_for_typst,
    pre_for_typst_at,
    pre_for_typst_dollarmark,
    pre_image_verify,
    pre_remove_links,
    pre_remove_titlestar,
    pre_trim_whitespace,
)

__all__ = [
    "pre_clean_frontmatter",
    "pre_image_verify",
    "pre_remove_links",
    "pre_remove_titlestar",
    "pre_trim_whitespace",
    "pre_add_line_breaks",
    "pre_dash_to_star",
    "pre_for_typst_at",
    "pre_for_typst_dollarmark",
    "pre_for_typst",
    "extract_frontmatter",
]
