"""
移除链接后处理器

移除 Markdown 内容中的链接，保留图片。
"""

from mark2pdf.helper_markdown import pre_remove_links


def process(content: str) -> str:
    """
    移除链接（保留图片）

    Args:
        content: Markdown 内容

    Returns:
        移除链接后的内容
    """
    return pre_remove_links(content, verbose=False)
