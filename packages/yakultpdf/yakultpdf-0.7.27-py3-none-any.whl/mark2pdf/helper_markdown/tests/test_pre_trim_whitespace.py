import sys
from pathlib import Path

import pytest

# 添加父目录到路径，以便导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_preprocess import pre_trim_whitespace


class TestPreTrimWhitespace:
    """测试 pre_trim_whitespace 函数"""

    def test_trim_leading_whitespace(self):
        """测试去除行首空格"""
        content = "  这是第一行\n  这是第二行"
        expected = "这是第一行\n这是第二行"
        result = pre_trim_whitespace(content)
        assert result == expected

    def test_trim_trailing_whitespace(self):
        """测试去除行尾空格"""
        content = "这是第一行  \n这是第二行  "
        expected = "这是第一行\n这是第二行"
        result = pre_trim_whitespace(content)
        assert result == expected

    def test_trim_both_leading_and_trailing(self):
        """测试同时去除行首和行尾空格"""
        content = "  这是第一行  \n  这是第二行  "
        expected = "这是第一行\n这是第二行"
        result = pre_trim_whitespace(content)
        assert result == expected

    def test_empty_lines(self):
        """测试空行处理"""
        content = "   \n  这是内容  \n   "
        expected = "\n这是内容\n"
        result = pre_trim_whitespace(content)
        assert result == expected

    def test_no_whitespace(self):
        """测试没有空格的情况"""
        content = "这是第一行\n这是第二行"
        expected = "这是第一行\n这是第二行"
        result = pre_trim_whitespace(content)
        assert result == expected

    def test_single_line(self):
        """测试单行内容"""
        content = "  单行内容  "
        expected = "单行内容"
        result = pre_trim_whitespace(content)
        assert result == expected

    def test_empty_content(self):
        """测试空内容"""
        content = ""
        expected = ""
        result = pre_trim_whitespace(content)
        assert result == expected

    def test_tabs_and_spaces(self):
        """测试制表符和空格混合"""
        content = "\t  这是制表符和空格  \t"
        expected = "这是制表符和空格"
        result = pre_trim_whitespace(content)
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
