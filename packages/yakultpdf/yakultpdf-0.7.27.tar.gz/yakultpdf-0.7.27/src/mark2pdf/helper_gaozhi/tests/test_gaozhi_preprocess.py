"""
mark2pdf.helper_gaozhi 稿纸预处理模块测试

测试核心函数：
- center_with_cnspace: 中文空格居中
- md_pre_process: 前置处理
- process_for_typ: 稿纸专用排版
"""

import sys
from pathlib import Path

import pytest

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from gaozhi_preprocess import center_with_cnspace, md_pre_process, process_for_typ


class TestCenterWithCnspace:
    """测试中文空格居中功能"""

    def test_short_text_centered(self):
        """测试短文本居中"""
        result = center_with_cnspace("标题", linelength=20)
        # 应该在前面添加中文空格
        assert result.startswith("\u3000")
        assert "标题" in result

    def test_exact_length_no_padding(self):
        """测试文本长度等于行长度时不添加空格"""
        text = "一二三四五六七八九十" * 2  # 20 个字符
        result = center_with_cnspace(text, linelength=20)
        assert result == text

    def test_longer_than_line_no_padding(self):
        """测试文本长度超过行长度时不添加空格"""
        text = "这是一个很长很长的标题超过了二十个字符"
        result = center_with_cnspace(text, linelength=20)
        assert result == text

    def test_empty_string(self):
        """测试空字符串"""
        result = center_with_cnspace("", linelength=20)
        # 空字符串也会被居中处理
        assert result.startswith("\u3000")

    def test_single_char(self):
        """测试单个字符居中"""
        result = center_with_cnspace("题", linelength=20)
        assert result.startswith("\u3000")
        assert result.endswith("题")

    def test_custom_line_length(self):
        """测试自定义行长度"""
        result = center_with_cnspace("标题", linelength=10)
        assert "\u3000" in result
        assert "标题" in result


class TestMdPreProcess:
    """测试前置处理功能"""

    def test_empty_content(self):
        """测试空内容"""
        result = md_pre_process("")
        assert result == []

    def test_whitespace_only(self):
        """测试只有空格的内容"""
        result = md_pre_process("   \n  \n  ")
        assert result == []

    def test_remove_frontmatter(self):
        """测试移除 frontmatter"""
        content = """---
title: 测试
author: 作者
---
正文内容
"""
        result = md_pre_process(content)
        assert "title" not in "".join(result)
        assert "正文内容" in "".join(result)

    def test_remove_spaces(self):
        """测试移除空格"""
        content = "这是 一段 文字"
        result = md_pre_process(content)
        joined = "".join(result)
        assert " " not in joined

    def test_remove_cnspace(self):
        """测试移除中文空格"""
        content = "这是\u3000一段\u3000文字"
        result = md_pre_process(content)
        joined = "".join(result)
        # 中文空格应该被移除
        assert "\u3000" not in joined.replace("\\", "")

    def test_paragraph_separator(self):
        """测试段落分隔符转换"""
        content = """第一段

第二段
"""
        result = md_pre_process(content)
        # 应该用反斜杠分隔
        joined = "\n".join(result)
        assert "\\" in joined

    def test_single_line(self):
        """测试单行内容"""
        content = "只有一行"
        result = md_pre_process(content)
        assert len(result) == 1
        assert "只有一行" in result[0]

    def test_multiple_paragraphs(self):
        """测试多段落内容"""
        content = """第一段

第二段

第三段
"""
        result = md_pre_process(content)
        joined = "\n".join(result)
        assert "第一段" in joined
        assert "第二段" in joined
        assert "第三段" in joined


class TestProcessForTyp:
    """测试稿纸专用排版功能"""

    def test_title_centered(self):
        """测试标题居中"""
        content = """我的作文题目

作者

正文内容
"""
        result = process_for_typ(content)
        lines = result.split("\n")
        # 第一行（标题）应该有中文空格前缀
        assert lines[0].startswith("\u3000")
        assert "我的作文题目" in lines[0]

    def test_short_author_centered(self):
        """测试短作者名居中"""
        content = """标题

张三

正文
"""
        result = process_for_typ(content)
        lines = result.split("\n")
        # 作者名（少于8字符）应该居中
        if len(lines) > 1:
            # 应该有中文空格前缀
            assert "\u3000" in lines[1]

    def test_long_author_indented(self):
        """测试长作者名缩进"""
        content = """标题

这是一个很长的作者名称超过八个字

正文
"""
        result = process_for_typ(content)
        lines = result.split("\n")
        # 长作者名应该只有两个中文空格缩进
        if len(lines) > 1:
            assert lines[1].startswith("\u3000\u3000")

    def test_body_indented(self):
        """测试正文缩进"""
        content = """标题

作者

第一段正文

第二段正文
"""
        result = process_for_typ(content)
        lines = result.split("\n")
        # 正文行（第三行及以后）应该有两个中文空格缩进
        for i, line in enumerate(lines):
            if i > 1 and line.strip():
                assert line.startswith("\u3000\u3000")

    def test_empty_content(self):
        """测试空内容"""
        result = process_for_typ("")
        assert result == ""

    def test_single_line_title_only(self):
        """测试只有标题"""
        content = "只有标题"
        result = process_for_typ(content)
        assert "\u3000" in result
        assert "只有标题" in result

    def test_title_and_author_only(self):
        """测试只有标题和作者"""
        content = """标题

作者
"""
        result = process_for_typ(content)
        lines = result.split("\n")
        assert len(lines) >= 2

    def test_with_frontmatter(self):
        """测试带 frontmatter 的内容"""
        content = """---
title: 元数据标题
---
实际标题

作者

正文内容
"""
        result = process_for_typ(content)
        # frontmatter 应该被移除
        assert "元数据标题" not in result
        assert "实际标题" in result

    def test_preserves_backslash_separators(self):
        """测试保留反斜杠分隔符"""
        content = """标题

作者

第一段

第二段
"""
        result = process_for_typ(content)
        # 反斜杠用于 Typst 段落分隔
        assert "\\" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
