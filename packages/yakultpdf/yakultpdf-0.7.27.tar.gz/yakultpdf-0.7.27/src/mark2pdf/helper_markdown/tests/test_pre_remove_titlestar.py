"""
测试 pre_remove_titlestar 功能
去掉标题中的加粗标记
"""

import sys
from pathlib import Path

# 添加父目录到 sys.path，使得可以导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_preprocess import pre_remove_titlestar


def test_h2_with_bold():
    """测试 H2 标题中的加粗应该被去掉"""
    content = "## **Premise**"
    expected = "## Premise"
    result = pre_remove_titlestar(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_h6_with_bold_and_colon():
    """测试 H6 标题中的加粗应该被去掉（包含冒号）"""
    content = "###### **Revenue Mechanics:**"
    expected = "###### Revenue Mechanics:"
    result = pre_remove_titlestar(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_h1_with_bold():
    """测试 H1 标题中的加粗应该被去掉"""
    content = "# **Introduction**"
    expected = "# Introduction"
    result = pre_remove_titlestar(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_multiple_headings():
    """测试多个标题"""
    content = """# **Title**

Some content here.

## **Subtitle**

More content.

### **Section**"""
    expected = """# Title

Some content here.

## Subtitle

More content.

### Section"""
    result = pre_remove_titlestar(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_heading_without_bold():
    """测试没有加粗的标题不应该被改变"""
    content = "## Regular Heading"
    expected = "## Regular Heading"
    result = pre_remove_titlestar(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_partial_bold_in_heading():
    """测试部分加粗的标题只去掉加粗标记"""
    content = "## This is **bold** text"
    expected = "## This is bold text"
    result = pre_remove_titlestar(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_bold_in_regular_text():
    """测试普通文本中的加粗不应该被改变"""
    content = """## **Heading**

This is **bold** text in a paragraph."""
    expected = """## Heading

This is **bold** text in a paragraph."""
    result = pre_remove_titlestar(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_heading_at_start_of_file():
    """测试文件开头的标题"""
    content = "# **First Heading**\n\nContent"
    expected = "# First Heading\n\nContent"
    result = pre_remove_titlestar(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_multiple_bold_in_heading():
    """测试标题中有多个加粗部分"""
    content = "## **Part 1** and **Part 2**"
    expected = "## Part 1 and Part 2"
    result = pre_remove_titlestar(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"
