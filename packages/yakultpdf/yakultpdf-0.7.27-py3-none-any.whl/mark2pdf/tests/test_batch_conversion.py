"""
run_batch_conversion 单元测试
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mark2pdf import run_batch_conversion
from mark2pdf.config import CONFIG_FILENAME


@pytest.fixture
def batch_workspace(tmp_path, monkeypatch):
    """创建批量转换测试工作区"""
    # 创建配置文件
    config_file = tmp_path / CONFIG_FILENAME
    config_file.write_text("""
[project]
name = "batch-test"

[paths]
in = "in"
out = "out"

[options]
default_template = "nb"
""")

    # 创建输入目录
    in_dir = tmp_path / "in"
    in_dir.mkdir()

    # 创建输出目录
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestRunBatchConversion:
    """run_batch_conversion 测试"""

    def test_directory_not_exists(self, batch_workspace, capsys):
        """目录不存在时返回 False"""
        result = run_batch_conversion(
            directory="nonexistent",
            workspace_dir=batch_workspace,
        )

        assert result is False
        captured = capsys.readouterr()
        assert "目录不存在" in captured.out

    def test_empty_directory(self, batch_workspace, capsys):
        """空目录（无 .md 文件）返回 True"""
        # 创建空子目录
        subdir = batch_workspace / "in" / "empty"
        subdir.mkdir()

        result = run_batch_conversion(
            directory="empty",
            workspace_dir=batch_workspace,
        )

        assert result is True
        captured = capsys.readouterr()
        assert "没有 Markdown 文件" in captured.out

    def test_only_index_md_returns_true(self, batch_workspace, capsys):
        """仅有 index.md 时也返回 True（无需转换）"""
        subdir = batch_workspace / "in" / "only_index"
        subdir.mkdir()
        (subdir / "index.md").write_text("---\ntitle: Index\n---\n# Index")

        result = run_batch_conversion(
            directory="only_index",
            workspace_dir=batch_workspace,
        )

        assert result is True
        captured = capsys.readouterr()
        assert "没有 Markdown 文件" in captured.out

    @patch("mark2pdf.conversion.convert_file")
    def test_batch_converts_each_file(self, mock_convert, batch_workspace, capsys):
        """批量模式逐一转换每个文件"""
        mock_convert.return_value = True

        subdir = batch_workspace / "in" / "batch_test"
        subdir.mkdir()
        (subdir / "file1.md").write_text("# File 1")
        (subdir / "file2.md").write_text("# File 2")
        (subdir / "file3.md").write_text("# File 3")

        result = run_batch_conversion(
            directory="batch_test",
            workspace_dir=batch_workspace,
            jobs=1,
        )

        assert result is True
        assert mock_convert.call_count == 3

        # 检查输出
        captured = capsys.readouterr()
        assert "批量转换：3 个文件" in captured.out
        assert "成功 3" in captured.out

    @patch("mark2pdf.conversion.convert_file")
    def test_batch_excludes_index_md(self, mock_convert, batch_workspace):
        """批量模式排除 index.md"""
        mock_convert.return_value = True

        subdir = batch_workspace / "in" / "with_index"
        subdir.mkdir()
        (subdir / "index.md").write_text("---\ntitle: Config\n---")
        (subdir / "doc1.md").write_text("# Doc 1")
        (subdir / "doc2.md").write_text("# Doc 2")

        run_batch_conversion(
            directory="with_index",
            workspace_dir=batch_workspace,
            jobs=1,
        )

        # index.md 不应被转换
        assert mock_convert.call_count == 2
        call_args = [call[1]["input_file"] for call in mock_convert.call_args_list]
        assert "with_index/index.md" not in call_args

    @patch("mark2pdf.conversion.convert_file")
    def test_output_subdir_for_subdirectory(self, mock_convert, batch_workspace):
        """子目录输出到 out/<子目录>/"""
        mock_convert.return_value = True

        subdir = batch_workspace / "in" / "任务发布"
        subdir.mkdir()
        (subdir / "task.md").write_text("# Task")

        run_batch_conversion(
            directory="任务发布",
            workspace_dir=batch_workspace,
            jobs=1,
        )

        # 检查 outdir 参数
        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs["outdir"] == "out/任务发布"

    @patch("mark2pdf.conversion.convert_file")
    def test_output_dir_for_current_directory(self, mock_convert, batch_workspace):
        """当前目录（.）输出到 out/"""
        mock_convert.return_value = True

        # 在 in 目录创建文件
        (batch_workspace / "in" / "root_file.md").write_text("# Root")

        run_batch_conversion(
            directory=".",
            workspace_dir=batch_workspace,
            jobs=1,
        )

        # 检查 outdir 参数
        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs["outdir"] == "out"

    @patch("mark2pdf.conversion.convert_file")
    def test_returns_false_on_any_failure(self, mock_convert, batch_workspace, capsys):
        """任一文件转换失败时返回 False"""
        # 第一个成功，第二个失败
        mock_convert.side_effect = [True, False]

        subdir = batch_workspace / "in" / "partial_fail"
        subdir.mkdir()
        (subdir / "success.md").write_text("# Success")
        (subdir / "fail.md").write_text("# Fail")

        result = run_batch_conversion(
            directory="partial_fail",
            workspace_dir=batch_workspace,
            jobs=1,
        )

        assert result is False
        captured = capsys.readouterr()
        assert "成功 1" in captured.out
        assert "失败 1" in captured.out

    @patch("mark2pdf.conversion.convert_file")
    def test_index_md_frontmatter_used_as_default(self, mock_convert, batch_workspace):
        """index.md 的 frontmatter 作为目录级默认值"""
        mock_convert.return_value = True

        subdir = batch_workspace / "in" / "fm_test"
        subdir.mkdir()
        (subdir / "index.md").write_text("""---
author: Default Author
pubinfo:
  edition: Test Edition
---
# Index
""")
        (subdir / "doc.md").write_text("# Doc")

        run_batch_conversion(
            directory="fm_test",
            workspace_dir=batch_workspace,
            jobs=1,
        )

        # 检查 default_frontmatter 包含 index.md 的内容
        call_kwargs = mock_convert.call_args[1]
        default_fm = call_kwargs.get("default_frontmatter", {})
        assert default_fm.get("author") == "Default Author"
        assert default_fm.get("pubinfo", {}).get("edition") == "Test Edition"

    @patch("mark2pdf.conversion.convert_file")
    def test_template_from_index_md(self, mock_convert, batch_workspace):
        """从 index.md 读取 template 配置"""
        mock_convert.return_value = True

        subdir = batch_workspace / "in" / "template_test"
        subdir.mkdir()
        (subdir / "index.md").write_text("""---
theme:
  template: card.typ
---
""")
        (subdir / "doc.md").write_text("# Doc")

        run_batch_conversion(
            directory="template_test",
            workspace_dir=batch_workspace,
            jobs=1,
        )

        # 检查 options.template
        call_kwargs = mock_convert.call_args[1]
        options = call_kwargs["options"]
        assert options.template == "card.typ"

    @patch("mark2pdf.conversion.convert_file")
    def test_cli_template_overrides_index(self, mock_convert, batch_workspace):
        """CLI 指定的 template 优先级最高"""
        mock_convert.return_value = True

        subdir = batch_workspace / "in" / "cli_override"
        subdir.mkdir()
        (subdir / "index.md").write_text("""---
template: index_template.typ
---
""")
        (subdir / "doc.md").write_text("# Doc")

        run_batch_conversion(
            directory="cli_override",
            workspace_dir=batch_workspace,
            template="cli_template.typ",
            jobs=1,
        )

        call_kwargs = mock_convert.call_args[1]
        options = call_kwargs["options"]
        assert options.template == "cli_template.typ"

    @patch("mark2pdf.conversion.convert_file")
    def test_index_title_not_inherited(self, mock_convert, batch_workspace):
        """index.md 的 title 不应注入到其他文件（避免文件名冲突）"""
        mock_convert.return_value = True

        subdir = batch_workspace / "in" / "title_test"
        subdir.mkdir()
        (subdir / "index.md").write_text("""---
title: 我的文档
author: Test Author
---
""")
        (subdir / "doc1.md").write_text("# Doc 1")
        (subdir / "doc2.md").write_text("# Doc 2")

        run_batch_conversion(
            directory="title_test",
            workspace_dir=batch_workspace,
            jobs=1,
        )

        # title 不应被继承，但 author 应该被继承
        call_kwargs = mock_convert.call_args[1]
        default_fm = call_kwargs.get("default_frontmatter", {})
        assert "title" not in default_fm
        assert default_fm.get("author") == "Test Author"

    @patch("mark2pdf.conversion.convert_file")
    def test_index_exportFilename_not_inherited(self, mock_convert, batch_workspace):
        """index.md 的 exportFilename 不应注入到其他文件"""
        mock_convert.return_value = True

        subdir = batch_workspace / "in" / "export_test"
        subdir.mkdir()
        (subdir / "index.md").write_text("""---
exportFilename: unified_output
pubinfo:
  edition: Test Edition
---
""")
        (subdir / "doc.md").write_text("# Doc")

        run_batch_conversion(
            directory="export_test",
            workspace_dir=batch_workspace,
            jobs=1,
        )

        call_kwargs = mock_convert.call_args[1]
        default_fm = call_kwargs.get("default_frontmatter", {})
        assert "exportFilename" not in default_fm
        assert default_fm.get("pubinfo", {}).get("edition") == "Test Edition"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
