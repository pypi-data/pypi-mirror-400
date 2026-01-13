"""
mark2pdf.core CLI 测试

使用 Click 的 CliRunner 测试 CLI 参数解析和分支逻辑。
通过 mock 避免实际调用 Pandoc/Typst。
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mark2pdf.core.cli import cli


class TestCliHelp:
    """测试 CLI 帮助信息"""

    def test_help_option(self):
        """测试 --help 选项"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "将 Markdown 文件转换为 PDF" in result.output
        assert "--template" in result.output

        assert "--verbose" in result.output

    def test_no_arguments(self):
        """测试无参数时显示提示"""
        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert "请提供 Markdown 文件名或使用 --dir 指定目录" in result.output
        assert "--help" in result.output


class TestCliFileMode:
    """测试文件模式 CLI"""

    def test_file_mode_calls_convert_file(self):
        """测试文件模式调用 convert_file"""
        runner = CliRunner()
        with (
            patch("mark2pdf.core.cli.convert_file") as mock_convert,
            patch("mark2pdf.core.cli.get_default_dirs", return_value=("in", "out")),
        ):
            mock_convert.return_value = True
            runner.invoke(cli, ["test.md"])

            mock_convert.assert_called_once()
            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["input_file"] == "test.md"
            assert call_kwargs["options"].template == "nb"
            assert call_kwargs["indir"] == "in"
            assert call_kwargs["outdir"] == "out"

    def test_file_mode_with_options(self):
        """测试带选项的文件模式"""
        runner = CliRunner()
        with (
            patch("mark2pdf.core.cli.convert_file") as mock_convert,
            patch("mark2pdf.core.cli.get_build_defaults") as mock_defaults,
        ):
            mock_convert.return_value = True
            mock_defaults.return_value = {}
            runner.invoke(
                cli,
                [
                    "test.md",
                    "--template",
                    "custom.typ",
                    "--verbose",
                    "--indir",
                    "custom_in",
                    "--outdir",
                    "custom_out",
                    "--overwrite",
                ],
            )

            mock_convert.assert_called_once()
            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["input_file"] == "test.md"
            options = call_kwargs["options"]
            assert options.template == "custom.typ"
            assert options.verbose is True
            assert options.overwrite is True

            assert call_kwargs["indir"] == "custom_in"
            assert call_kwargs["outdir"] == "custom_out"

    def test_file_mode_with_output_option(self):
        """测试自定义输出文件名"""
        runner = CliRunner()
        with patch("mark2pdf.core.cli.convert_file") as mock_convert:
            mock_convert.return_value = True
            runner.invoke(cli, ["test.md", "--output", "custom_output"])

            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["output_file"] == "custom_output"

    def test_file_mode_with_tc_option(self):
        """测试繁体转换选项"""
        runner = CliRunner()
        with patch("mark2pdf.core.cli.convert_file") as mock_convert:
            mock_convert.return_value = True
            runner.invoke(cli, ["test.md", "--tc"])

            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["options"].tc is True

    def test_file_mode_with_removelink(self):
        """测试移除链接选项"""
        runner = CliRunner()
        with patch("mark2pdf.core.cli.convert_file") as mock_convert:
            mock_convert.return_value = True
            runner.invoke(cli, ["test.md", "--removelink"])

            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["options"].removelink is True

    def test_file_mode_with_savemd(self):
        """测试保存中间 MD 文件选项"""
        runner = CliRunner()
        with patch("mark2pdf.core.cli.convert_file") as mock_convert:
            mock_convert.return_value = True
            runner.invoke(cli, ["test.md", "--savemd"])

            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["options"].savemd is True

    def test_file_mode_to_typst(self):
        """测试输出 typst 文件选项"""
        runner = CliRunner()
        with patch("mark2pdf.core.cli.convert_file") as mock_convert:
            mock_convert.return_value = True
            runner.invoke(cli, ["test.md", "--to-typst"])

            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["options"].to_typst is True


class TestCliDirectoryMode:
    """测试目录模式 CLI"""

    def test_directory_mode_calls_convert_directory(self):
        """测试目录模式调用 convert_directory"""
        runner = CliRunner()
        with patch("mark2pdf.core.cli.convert_directory") as mock_convert:
            mock_convert.return_value = True
            runner.invoke(cli, ["--dir", "docs"])

            mock_convert.assert_called_once()
            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["directory"] == "docs"
            assert call_kwargs["options"].template == "nb"

    def test_directory_mode_with_options(self):
        """测试带选项的目录模式"""
        runner = CliRunner()
        with (
            patch("mark2pdf.core.cli.convert_directory") as mock_convert,
            patch("mark2pdf.core.cli.get_build_defaults") as mock_defaults,
        ):
            mock_convert.return_value = True
            mock_defaults.return_value = {}
            runner.invoke(
                cli,
                [
                    "--dir",
                    "docs",
                    "--template",
                    "book.typ",
                    "--coverimg",
                    "cover.png",
                    "--to-typst",
                    "--savemd",
                    "--removelink",
                    "--tc",
                    "--verbose",
                ],
            )

            mock_convert.assert_called_once()
            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["directory"] == "docs"
            options = call_kwargs["options"]
            assert options.template == "book.typ"
            assert options.coverimg == "cover.png"
            assert options.to_typst is True
            assert options.savemd is True
            assert options.removelink is True
            assert options.tc is True
            assert options.verbose is True

    def test_directory_mode_with_output(self):
        """测试目录模式自定义输出"""
        runner = CliRunner()
        with patch("mark2pdf.core.cli.convert_directory") as mock_convert:
            mock_convert.return_value = True
            runner.invoke(cli, ["--dir", "docs", "--output", "merged_book"])

            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["output_file"] == "merged_book"

    def test_directory_mode_priority_over_file(self):
        """测试目录模式优先于文件模式"""
        runner = CliRunner()
        with patch("mark2pdf.core.cli.convert_directory") as mock_dir:
            with patch("mark2pdf.core.cli.convert_file") as mock_file:
                mock_dir.return_value = True
                # 同时提供文件名和 --dir，应该使用目录模式
                runner.invoke(cli, ["test.md", "--dir", "docs"])

                mock_dir.assert_called_once()
                mock_file.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
