"""
ConfigManager 单元测试
"""

import sys
from pathlib import Path

import pytest

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mark2pdf import ConfigManager, PdfworkConfig
from mark2pdf.config import CONFIG_FILENAME


class TestConfigManager:
    """ConfigManager 测试"""

    def test_load_returns_pdfwork_config(self):
        """load() 返回 PdfworkConfig 对象"""
        config = ConfigManager.load()
        assert isinstance(config, PdfworkConfig)
        assert config.data_root is not None
        assert config.code_root is not None

    def test_standalone_fallback(self, tmp_path, monkeypatch):
        """无配置时使用独立模式"""
        monkeypatch.chdir(tmp_path)
        config = ConfigManager.load()
        assert config.standalone is True
        assert config.data_root == tmp_path
        assert config.paths.input == "."
        assert config.paths.output == "."
        assert config.paths.tmp == ".mark2pdf_tmp"
        assert config.paths.fonts == "fonts"

    def test_load_from_cwd_with_config(self, tmp_path, monkeypatch):
        """CWD 有配置文件时使用 CWD"""
        # 创建配置文件
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text('[project]\nname = "test-project"')

        # 切换到临时目录
        monkeypatch.chdir(tmp_path)

        config = ConfigManager.load()

        assert config.data_root == tmp_path
        assert config.project_name == "test-project"

    def test_missing_fields_use_defaults(self, tmp_path, monkeypatch):
        """配置文件缺少字段时使用默认值"""
        # 创建只有 project 的配置
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text('[project]\nname = "partial"')

        monkeypatch.chdir(tmp_path)

        config = ConfigManager.load()

        # paths 应该使用默认值
        assert config.paths.input == "in"
        assert config.paths.output == "out"
        assert config.paths.tmp == "tmp"
        assert config.paths.template == "template"
        assert config.paths.fonts == "fonts"

        # options 应该使用默认值
        assert config.options.default_template == "nb"
        assert config.options.overwrite is False

    def test_full_config_parsing(self, tmp_path, monkeypatch):
        """完整配置文件解析"""
        config_content = """
[project]
name = "full-test"

[paths]
in = "input"
out = "output"
tmp = "temp"
template = "templates"
fonts = "fonts_dir"

[options]
default_template = "custom.typ"
overwrite = true


[frontmatter.pubinfo]
edition = "Test Edition"
watermark = "DRAFT"
"""
        config_file = tmp_path / CONFIG_FILENAME
        config_file.write_text(config_content)

        monkeypatch.chdir(tmp_path)

        config = ConfigManager.load()

        assert config.project_name == "full-test"
        assert config.paths.input == "input"
        assert config.paths.output == "output"
        assert config.paths.tmp == "temp"
        assert config.paths.template == "templates"
        assert config.paths.fonts == "fonts_dir"
        assert config.fonts_dir == tmp_path / "fonts_dir"
        assert config.options.default_template == "custom.typ"
        assert config.options.overwrite is True

        assert config.frontmatter["pubinfo"]["edition"] == "Test Edition"
        assert config.frontmatter["pubinfo"]["watermark"] == "DRAFT"


class TestPdfworkConfig:
    """PdfworkConfig 数据类测试"""

    def test_directory_properties(self, tmp_path):
        """测试目录属性"""
        config = PdfworkConfig()
        config.data_root = tmp_path

        assert config.input_dir == tmp_path / "in"
        assert config.output_dir == tmp_path / "out"
        assert config.tmp_dir == tmp_path / "tmp"
        assert config.template_dir == tmp_path / "template"
        assert config.fonts_dir == tmp_path / "fonts"

    def test_directory_properties_without_data_root(self):
        """data_root 未设置时属性抛出异常"""
        config = PdfworkConfig()

        with pytest.raises(ValueError, match="data_root 未设置"):
            _ = config.input_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
