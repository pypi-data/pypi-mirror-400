"""
mark2pdf CLI 测试
"""

import sys
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

# 添加父目录路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mark2pdf.cli import main


class TestInitCommand:
    """init 命令测试"""

    def test_init_missing_arg(self):
        """测试缺少参数"""
        runner = CliRunner()
        result = runner.invoke(main, ["init"])
        assert result.exit_code != 0
        assert "Missing argument 'TARGET_DIR'" in result.output

    def test_init_non_empty_dir_fails(self, tmp_path):
        """测试在非空目录运行失败"""
        # 创建一个非空目录
        target = tmp_path / "non_empty"
        target.mkdir()
        (target / "foo.txt").touch()

        runner = CliRunner()
        # 必须传入目录参数
        result = runner.invoke(main, ["init", str(target)])

        assert result.exit_code != 0
        assert "目录不为空" in result.output
        assert "禁止在非空目录初始化" in result.output

    def test_init_empty_dir_succeeds(self, tmp_path):
        """测试在空目录运行成功"""
        target = tmp_path / "empty"
        target.mkdir()

        runner = CliRunner()
        with patch("mark2pdf.commands.workspace.init_workspace") as mock_init:
            result = runner.invoke(main, ["init", str(target)])

            assert result.exit_code == 0
            mock_init.assert_called_once_with(
                target.resolve(),
                template_name=None,
                simple=False,
            )

    def test_init_template_only(self, tmp_path):
        """测试 --template 仅复制指定模板"""
        target = tmp_path / "template_only"
        target.mkdir()

        runner = CliRunner()
        with patch("mark2pdf.commands.workspace.init_workspace") as mock_init:
            result = runner.invoke(main, ["init", str(target), "--template", "nb.typ"])

            assert result.exit_code == 0
            mock_init.assert_called_once_with(
                target.resolve(),
                template_name="nb.typ",
                simple=False,
            )

    def test_init_ignores_ds_store(self, tmp_path):
        """测试忽略 .DS_Store 文件"""
        target = tmp_path / "ds_store_only"
        target.mkdir()
        (target / ".DS_Store").touch()

        runner = CliRunner()
        with patch("mark2pdf.commands.workspace.init_workspace") as mock_init:
            result = runner.invoke(main, ["init", str(target)])

            assert result.exit_code == 0
            mock_init.assert_called_once_with(
                target.resolve(),
                template_name=None,
                simple=False,
            )

    def test_init_simple_non_empty_dir_succeeds(self, tmp_path):
        """测试 --simple 允许非空目录"""
        target = tmp_path / "non_empty"
        target.mkdir()
        (target / "foo.txt").touch()

        runner = CliRunner()
        with patch("mark2pdf.commands.workspace.init_workspace") as mock_init:
            result = runner.invoke(main, ["init", str(target), "--simple"])

            assert result.exit_code == 0
            mock_init.assert_called_once_with(
                target.resolve(),
                template_name=None,
                simple=True,
            )


class TestVersionCommand:
    """version 命令测试"""

    def test_version_output(self):
        """测试版本输出"""
        runner = CliRunner()
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "mark2pdf" in result.output


class TestConvertCommand:
    """convert 命令测试"""

    def test_convert_help(self):
        """测试帮助信息"""
        runner = CliRunner()
        result = runner.invoke(main, ["convert", "--help"])
        assert result.exit_code == 0
        assert "--show-config" in result.output
        assert "--dry-run" in result.output
        assert "--postprocess" in result.output
        assert "--batchall" in result.output

    def test_convert_standalone_dry_run(self):
        """测试无配置文件时的独立模式"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("test.md").write_text("# Test")
            result = runner.invoke(main, ["convert", "test.md", "--dry-run"])
            assert result.exit_code == 0
            assert "执行计划" in result.output
            assert "paths.input: ." in result.output
            assert "paths.output: ." in result.output

    def test_convert_batchall_dry_run(self):
        """测试 --batchall 等价于批量转换当前目录"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["convert", "--batchall", "--dry-run"])
            assert result.exit_code == 0
            # jobs=4 时显示并发模式
            assert "转换目录 '.'" in result.output

    def test_batchall_batch_conflict(self):
        """--batchall 与 --batch 不能同时使用"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["convert", "--batchall", "--batch", "foo"])
            assert result.exit_code != 0
            assert "--batchall 与 --batch 不能同时使用" in result.output

    def test_dir_batch_conflict(self):
        """--dir 与 --batch 不能同时使用"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # 需要跳过工具检查，否则会检查 pandoc/typst
            result = runner.invoke(
                main, ["convert", "--dir", "foo", "--batch", "bar", "--skip-tool-check"]
            )
            assert result.exit_code != 0
            assert "--dir 和 --batch" in result.output

    def test_show_config_mode(self):
        """--show-config 仅显示配置不执行"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("test.md").write_text("# Test")
            result = runner.invoke(main, ["convert", "test.md", "--show-config"])
            assert result.exit_code == 0
            assert "合并后的完整配置" in result.output
            # 不应有执行计划
            assert "执行计划" not in result.output

    @patch("mark2pdf.commands.convert.run_conversion")
    @patch("mark2pdf.commands.convert.check_pandoc_typst")
    def test_single_file_calls_run_conversion(self, mock_check, mock_run):
        """单文件模式调用 run_conversion"""
        mock_run.return_value = True
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("test.md").write_text("# Test")
            result = runner.invoke(main, ["convert", "test.md"])
            assert result.exit_code == 0
            mock_run.assert_called_once()
            # 验证调用参数
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["filename"] == "test.md"

    @patch("mark2pdf.commands.convert.run_directory_conversion")
    @patch("mark2pdf.commands.convert.check_pandoc_typst")
    def test_dir_mode_calls_run_directory_conversion(self, mock_check, mock_run):
        """--dir 模式调用 run_directory_conversion"""
        mock_run.return_value = True
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("docs").mkdir()
            (Path("docs") / "index.md").write_text("# Docs")
            result = runner.invoke(main, ["convert", "--dir", "docs"])
            assert result.exit_code == 0
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["directory"] == "docs"

    @patch("mark2pdf.commands.convert.run_batch_conversion")
    @patch("mark2pdf.commands.convert.check_pandoc_typst")
    def test_batch_mode_calls_run_batch_conversion(self, mock_check, mock_run):
        """--batch 模式调用 run_batch_conversion"""
        mock_run.return_value = True
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("batch").mkdir()
            (Path("batch") / "file1.md").write_text("# File 1")
            result = runner.invoke(main, ["convert", "--batch", "batch"])
            assert result.exit_code == 0
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["directory"] == "batch"

class TestTemplateCommand:
    """template 命令测试"""

    def test_template_requires_workspace(self):
        """测试无工作区配置时失败"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["template", "nb.typ"])
            assert result.exit_code != 0
            assert "未检测到工作区配置" in result.output

    def test_template_copies_to_workspace(self):
        """测试复制模板到工作区"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("mark2pdf.config.toml").write_text('[project]\nname = "test"')

            result = runner.invoke(main, ["template", "card.typ"])

            assert result.exit_code == 0
            assert Path("template/card.typ").exists()

    def test_template_copies_directory(self):
        """测试复制模板目录"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("mark2pdf.config.toml").write_text('[project]\nname = "test"')

            result = runner.invoke(main, ["template", "letter"])

            assert result.exit_code == 0
            assert Path("template/letter").exists()


class TestCoverPrepareCommand:
    """coverimg 命令测试"""

    def test_list_papers(self):
        """测试列出纸型"""
        runner = CliRunner()
        result = runner.invoke(main, ["coverimg", "list"])
        assert result.exit_code == 0
        assert "a4" in result.output
        assert "letter" in result.output

    def test_check_help(self):
        """测试 check 子命令帮助"""
        runner = CliRunner()
        result = runner.invoke(main, ["coverimg", "check", "--help"])
        assert result.exit_code == 0
        assert "--paper" in result.output
