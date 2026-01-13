r"""
测试 pre_for_typst_at 功能
将不在链接 URL 中的 @ 改为 \@
"""

import sys
from pathlib import Path

# 添加父目录到 sys.path，使得可以导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_preprocess import pre_for_typst_at


def test_at_in_url_not_escaped():
    """测试链接 URL 中的 @ 不应该被转义"""
    content = "[Click here](https://x.com/@ethena_labs)"
    expected = "[Click here](https://x.com/@ethena_labs)"
    result = pre_for_typst_at(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_at_in_link_text_escaped():
    """测试链接文本中的 @ 应该被转义"""
    content = "[@ethena](https://x.com/ethena)"
    expected = "[\\@ethena](https://x.com/ethena)"
    result = pre_for_typst_at(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_at_in_image_alt_text():
    """测试图片 alt 文本中的 @ 应该被转义"""
    content = "![Photo of @user](image.png)"
    expected = "![Photo of \\@user](image.png)"
    result = pre_for_typst_at(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_at_in_inline_code_not_escaped():
    """测试行内代码中的 @ 不应该被转义"""
    content = "Use `@decorator` for registration."
    expected = "Use `@decorator` for registration."
    result = pre_for_typst_at(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_at_in_code_block_not_escaped():
    """测试代码块中的 @ 不应该被转义"""
    content = "```\n@decorator\n```"
    expected = "```\n@decorator\n```"
    result = pre_for_typst_at(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_already_escaped():
    """测试已经转义的 @ 不会被重复转义"""
    content = "\\@username"
    expected = "\\@username"
    result = pre_for_typst_at(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"
