"""
init_workspace 简化模式测试
"""

import pytest

from mark2pdf.config import CONFIG_FILENAME
from mark2pdf.config.workspace import init_workspace


def test_simple_init_only_writes_config_and_frontmatter(tmp_path):
    """simple 模式仅写入配置与 frontmatter"""
    target = tmp_path / "workspace"
    target.mkdir()
    (target / "existing.txt").write_text("keep")

    init_workspace(target, simple=True)

    assert (target / CONFIG_FILENAME).exists()
    assert (target / "frontmatter.yaml").exists()

    assert not (target / "createpdf.py").exists()
    assert not (target / "in").exists()
    assert not (target / "out").exists()
    assert not (target / "tmp").exists()
    assert not (target / "template").exists()
    assert not (target / "fonts").exists()


def test_simple_init_rejects_template_copy(tmp_path):
    """simple 模式不支持模板复制"""
    target = tmp_path / "workspace"
    target.mkdir()

    with pytest.raises(ValueError, match="simple 模式不支持复制模板"):
        init_workspace(target, template_name="nb.typ", simple=True)
