from unittest.mock import MagicMock, patch

import pytest

from mark2pdf.helper_typst import run_pandoc_typst


class TestRunPandocTypst:
    """测试 run_pandoc_typst 函数"""

    @pytest.fixture
    def mock_subprocess(self):
        with patch("mark2pdf.helper_typst.helper_typst.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            yield mock_run

    def test_single_file_template(self, tmp_path, mock_subprocess):
        """测试单文件模板处理：card.typ"""
        workdir = tmp_path / "work"
        workdir.mkdir()

        input_file = workdir / "test.md"
        input_file.write_text("# Test")
        output_file = workdir / "test.pdf"

        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "card.typ"
        template_file.write_text("# Template")

        # 在 pandoc 执行时检查模板文件是否已复制到工作目录
        def side_effect(*args, **kwargs):
            # 检查模板文件是否在工作目录中
            expected_template = workdir / "card.typ"
            assert expected_template.exists(), "模板文件未复制到工作目录"
            # 创建输出文件
            output_file.touch()
            return MagicMock(returncode=0)

        mock_subprocess.side_effect = side_effect

        result = run_pandoc_typst(
            str(input_file),
            str(output_file),
            str(template_file),
            str(workdir),
            verbose=True,
        )

        assert result is True

        # 验证模板文件在转换后被清理
        target_template = workdir / "card.typ"
        assert not target_template.exists(), "模板文件未被清理"

    def test_directory_template(self, tmp_path, mock_subprocess):
        """测试目录式模板处理：nb/nb.typ"""
        workdir = tmp_path / "work"
        workdir.mkdir()

        input_file = workdir / "test.md"
        input_file.write_text("# Test")
        output_file = workdir / "test.pdf"

        template_root = tmp_path / "templates"
        template_dir = template_root / "nb"
        template_dir.mkdir(parents=True)
        template_file = template_dir / "nb.typ"
        template_file.write_text("# Template")
        lib_file = template_dir / "lib.typ"  # 模拟依赖文件
        lib_file.write_text("# Lib")

        # 在 pandoc 执行时检查模板目录内容是否已平铺复制
        def side_effect(*args, **kwargs):
            # 验证 nb.typ 和 lib.typ 都在工作目录根目录下
            assert (workdir / "nb.typ").exists(), "模板文件未平铺复制"
            assert (workdir / "lib.typ").exists(), "依赖文件未平铺复制"

            # 验证没有 nb 子目录
            assert not (workdir / "nb").exists(), "不应创建子目录"

            output_file.touch()
            return MagicMock(returncode=0)

        mock_subprocess.side_effect = side_effect

        # 使用真实的 copytree/copy2，不需要 patch 它们，因为我们在验证副作用
        # 只需要 patch subprocess.run

        result = run_pandoc_typst(
            str(input_file),
            str(output_file),
            str(template_file),
            str(workdir),
            verbose=True,
        )

        assert result is True

        # 验证清理
        assert not (workdir / "nb.typ").exists(), "模板文件未被清理"
        assert not (workdir / "lib.typ").exists(), "依赖文件未被清理"

    def test_extra_arguments(self, tmp_path, mock_subprocess):
        """测试额外参数传递"""
        workdir = tmp_path / "work"
        workdir.mkdir()
        template_file = tmp_path / "card.typ"
        template_file.write_text("# Template")
        input_file = workdir / "test.md"
        output_file = workdir / "test.pdf"

        # 模拟 pandoc 生成输出文件
        # 使用 lambda 时要小心，因为它不接受语句。
        def side_effect(*args, **kwargs):
            output_file.touch()
            return MagicMock(returncode=0)

        mock_subprocess.side_effect = side_effect

        result = run_pandoc_typst(
            str(input_file),
            str(output_file),
            str(template_file),
            str(workdir),
            verbose=False,
            with_pagenumber=True,
            cover_image="cover.jpg",
        )

        assert result is True

    def test_output_typst(self, tmp_path, mock_subprocess):
        """测试输出 typst 格式"""
        workdir = tmp_path / "work"
        workdir.mkdir()
        template_file = tmp_path / "card.typ"
        template_file.write_text("# Tpl")

        input_file = workdir / "in.md"
        output_file = workdir / "out.pdf"

        def side_effect(*args, **kwargs):
            # 确保实际期望的是 .typ 文件
            real_output = output_file.with_suffix(".typ")
            real_output.touch()
            return MagicMock(returncode=0)

        mock_subprocess.side_effect = side_effect

        result = run_pandoc_typst(
            str(input_file), str(output_file), str(template_file), str(workdir), to_typst=True
        )

        assert result is True
        assert output_file.with_suffix(".typ").exists()
