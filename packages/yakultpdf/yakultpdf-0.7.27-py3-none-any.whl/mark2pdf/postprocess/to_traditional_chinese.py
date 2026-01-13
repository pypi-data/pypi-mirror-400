"""
繁体中文转换后处理器

将简体中文内容转换为繁体中文。
"""

from mark2pdf.helper_utils import convert_to_traditional


def process(content: str) -> str:
    """
    转换为繁体中文

    Args:
        content: 原始内容

    Returns:
        繁体中文内容
    """
    return convert_to_traditional(content)
