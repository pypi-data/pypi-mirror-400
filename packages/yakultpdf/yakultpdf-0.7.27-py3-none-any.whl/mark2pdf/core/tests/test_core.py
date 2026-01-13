"""
mark2pdf.core 核心功能测试

测试核心函数：
- get_output_filename: 输出文件名处理
- merge_directory_markdown: 目录合并
"""

import tempfile
from pathlib import Path

import pytest

from mark2pdf.core.core import get_output_filename
from mark2pdf.core.directory import merge_directory_markdown


class TestGetOutputFilename:
    """测试输出文件名处理功能"""

    def test_title_fallback_when_no_export_filename(self):
        """测试无 exportFilename 时使用 title"""
        content = """---
title: 测试文档
---

正文
"""
        default_path = Path("/output/test.pdf")
        result = get_output_filename(content, default_path, tc=False, verbose=False)
        assert result == Path("/output/测试文档.pdf")

    def test_no_export_filename_or_title(self):
        """测试无 exportFilename/title 时使用默认路径"""
        content = "正文"
        default_path = Path("/output/test.pdf")
        result = get_output_filename(content, default_path, tc=False, verbose=False)
        assert result == default_path

    def test_with_export_filename(self):
        """测试使用 exportFilename 覆盖默认路径"""
        content = """---
title: 测试文档
exportFilename: 自定义名称.pdf
---

正文
"""
        default_path = Path("/output/test.pdf")
        result = get_output_filename(content, default_path, tc=False, verbose=False)
        assert result == Path("/output/自定义名称.pdf")

    def test_export_filename_without_extension(self):
        """测试 exportFilename 缺省追加扩展名"""
        content = """---
title: 测试文档
exportFilename: 自定义名称
---

正文
"""
        default_path = Path("/output/test.pdf")
        result = get_output_filename(content, default_path, tc=False, verbose=False)
        assert result == Path("/output/自定义名称.pdf")

    def test_export_filename_with_tc(self):
        """测试繁体中文转换"""
        content = """---
exportFilename: 简体文件名.pdf
---
"""
        default_path = Path("/output/test.pdf")
        result = get_output_filename(content, default_path, tc=True, verbose=False)
        # 繁体转换后的文件名
        assert "簡體" in str(result) or "简体" not in str(result)


class TestMergeDirectoryMarkdown:
    """测试目录合并功能"""

    def test_merge_basic_directory(self):
        """测试基本目录合并"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # 创建测试文件
            (tmppath / "01_chapter1.md").write_text("# 第一章\n\n内容1", encoding="utf-8")
            (tmppath / "02_chapter2.md").write_text("# 第二章\n\n内容2", encoding="utf-8")

            content = merge_directory_markdown(tmppath)

            assert "第一章" in content
            assert "第二章" in content

    def test_merge_with_index(self):
        """测试包含 index.md 的目录合并"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # 创建 index.md 和其他文件
            (tmppath / "index.md").write_text(
                """---
title: 书籍标题
---

# 前言
""",
                encoding="utf-8",
            )
            (tmppath / "01_chapter1.md").write_text("# 第一章\n\n内容", encoding="utf-8")

            content = merge_directory_markdown(tmppath)

            # index.md 应该在最前面
            assert content.startswith("---")
            assert "书籍标题" in content
            assert "第一章" in content

    def test_merge_excludes_special_files(self):
        """测试合并时排除特殊文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            (tmppath / "01_chapter.md").write_text("# 正文", encoding="utf-8")
            (tmppath / "merged.md").write_text("# 旧合并文件", encoding="utf-8")
            (tmppath / "md2pdf_temp.md").write_text("# 临时文件", encoding="utf-8")

            content = merge_directory_markdown(tmppath)

            assert "正文" in content
            assert "旧合并文件" not in content
            assert "临时文件" not in content

    def test_merge_empty_directory(self):
        """测试空目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            content = merge_directory_markdown(tmppath)

            assert content == ""

    def test_merge_nonexistent_directory(self):
        """测试不存在的目录"""
        with pytest.raises(ValueError, match="目录不存在"):
            merge_directory_markdown(Path("/nonexistent/path"))

    def test_merge_removes_frontmatter_from_subsequent_files(self):
        """测试后续文件的 frontmatter 被移除"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            (tmppath / "index.md").write_text(
                """---
title: 主标题
---

# 前言
""",
                encoding="utf-8",
            )
            (tmppath / "01_chapter.md").write_text(
                """---
title: 章节标题
---

# 第一章
""",
                encoding="utf-8",
            )

            content = merge_directory_markdown(tmppath)

            # 只应该有一个 frontmatter
            assert content.count("---\ntitle:") == 1
