"""
Tests for clean command
"""

import sys
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

# 添加父目录路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mark2pdf import PdfworkConfig
from mark2pdf.cli import main


class TestCleanCommand:
    """clean 命令测试"""

    def test_clean_dry_run(self, tmp_path):
        """测试 --dry-run (仅 PDF)"""
        # 准备环境
        output_dir = tmp_path / "out"
        output_dir.mkdir()

        # PDF 文件
        (output_dir / "file1.pdf").touch()
        (output_dir / "subdir").mkdir()
        (output_dir / "subdir" / "file2.pdf").touch()

        # 非 PDF 文件 (应保留)
        (output_dir / "readme.md").touch()
        (output_dir / "subdir" / "config.json").touch()

        runner = CliRunner()

        # 模拟 ConfigManager
        mock_config = PdfworkConfig()
        mock_config.data_root = tmp_path
        mock_config.paths.output = output_dir.name
        mock_config.standalone = False

        with patch("mark2pdf.commands.clean.ConfigManager.load", return_value=mock_config):
            result = runner.invoke(main, ["clean", "--dry-run"])

            assert result.exit_code == 0
            assert "file1.pdf" in result.output
            assert "file2.pdf" in result.output
            # 确认非 PDF 文件不在删除列表中
            assert "readme.md" not in result.output

            assert "[Dry Run] 将要删除以下文件" in result.output
            assert "Dry Run 完成，未执行删除操作" in result.output

            # 验证所有文件仍然存在
            assert (output_dir / "file1.pdf").exists()
            assert (output_dir / "readme.md").exists()

    def test_clean_abort(self, tmp_path):
        """测试用户取消"""
        output_dir = tmp_path / "out"
        output_dir.mkdir()
        (output_dir / "file1.pdf").touch()

        runner = CliRunner()
        mock_config = PdfworkConfig()
        mock_config.data_root = tmp_path
        mock_config.paths.output = output_dir.name
        mock_config.standalone = False

        with patch("mark2pdf.commands.clean.ConfigManager.load", return_value=mock_config):
            # 输入 n
            result = runner.invoke(main, ["clean"], input="n\n")

            assert result.exit_code != 0
            assert "Aborted" in result.output or "Aborted!" in result.output

            # 验证文件仍然存在
            assert (output_dir / "file1.pdf").exists()

    def test_clean_confirm(self, tmp_path):
        """测试用户确认 (保留非 PDF)"""
        output_dir = tmp_path / "out"
        output_dir.mkdir()
        (output_dir / "file1.pdf").touch()
        (output_dir / "keep.txt").touch()

        runner = CliRunner()
        mock_config = PdfworkConfig()
        mock_config.data_root = tmp_path
        mock_config.paths.output = output_dir.name
        mock_config.standalone = False

        with patch("mark2pdf.commands.clean.ConfigManager.load", return_value=mock_config):
            # 输入 y
            result = runner.invoke(main, ["clean"], input="y\n")

            assert result.exit_code == 0
            assert "正在清理 PDF 文件" in result.output
            assert "已删除: file1.pdf" in result.output

            # 验证 PDF 已被删除
            assert not (output_dir / "file1.pdf").exists()
            # 验证非 PDF 保留
            assert (output_dir / "keep.txt").exists()

    def test_clean_force(self, tmp_path):
        """测试强制删除"""
        output_dir = tmp_path / "out"
        output_dir.mkdir()
        (output_dir / "file1.pdf").touch()

        runner = CliRunner()
        mock_config = PdfworkConfig()
        mock_config.data_root = tmp_path
        mock_config.paths.output = output_dir.name
        mock_config.standalone = False

        with patch("mark2pdf.commands.clean.ConfigManager.load", return_value=mock_config):
            result = runner.invoke(main, ["clean", "--force"])

            assert result.exit_code == 0
            assert "正在清理" in result.output
            assert not (output_dir / "file1.pdf").exists()

    def test_clean_non_existent_dir(self, tmp_path):
        """测试目录不存在"""
        output_dir = tmp_path / "non_existent"

        runner = CliRunner()
        mock_config = PdfworkConfig()
        mock_config.data_root = tmp_path
        mock_config.paths.output = output_dir.name
        mock_config.standalone = False

        with patch("mark2pdf.commands.clean.ConfigManager.load", return_value=mock_config):
            result = runner.invoke(main, ["clean"])

            assert result.exit_code == 0
            assert "输出目录不存在" in result.output

    def test_clean_no_pdf(self, tmp_path):
        """测试无 PDF 文件"""
        output_dir = tmp_path / "no_pdf"
        output_dir.mkdir()
        (output_dir / "readme.md").touch()

        runner = CliRunner()
        mock_config = PdfworkConfig()
        mock_config.data_root = tmp_path
        mock_config.paths.output = output_dir.name
        mock_config.standalone = False

        with patch("mark2pdf.commands.clean.ConfigManager.load", return_value=mock_config):
            result = runner.invoke(main, ["clean"])

            assert result.exit_code == 0
            assert "没有 PDF 文件" in result.output
            assert (output_dir / "readme.md").exists()
