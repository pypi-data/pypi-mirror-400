import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 添加父目录到路径，以便导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from mark2pdf.helper_workingpath.helper_working_path import (
    create_working_dirs,
    get_project_root,
    resolve_inout_paths,
    resolve_template_path,
    safesave_path,
)


def create_mock_config(data_root: Path):
    """创建一个 mock 的 PdfworkConfig 对象"""
    mock_config = MagicMock()
    mock_config.data_root = data_root
    mock_config.code_root = data_root
    mock_paths = MagicMock()
    mock_paths.template = "template"
    mock_config.paths = mock_paths
    # 添加 input_dir 和 output_dir 属性
    mock_config.input_dir = data_root / "in"
    mock_config.output_dir = data_root / "out"
    return mock_config


def test_get_project_root():
    """测试获取项目根目录（按优先级选择标识文件）"""
    root = get_project_root()
    assert root.exists()
    # 检查至少有一个标识文件存在（按优先级顺序）
    has_identifier = (root / "pyproject.toml").exists() or (root / "package.json").exists()
    assert has_identifier, "至少应该有一个项目根目录标识文件存在"


def test_get_project_root_nodejs(monkeypatch, tmp_path):
    """测试获取项目根目录（Node.js 项目）"""
    # 创建临时目录结构模拟 Node.js 项目
    project_root = tmp_path / "nodejs_project"
    project_root.mkdir()

    # 创建 package.json
    (project_root / "package.json").write_text('{"name": "test-nodejs"}')

    # 创建子目录结构
    src_dir = project_root / "src" / "working_path"
    src_dir.mkdir(parents=True)

    # 模拟当前文件在子目录中
    with monkeypatch.context() as m:
        m.setattr(
            "mark2pdf.helper_workingpath.helper_working_path.__file__",
            str(src_dir / "helper_working_path.py"),
        )

        # 测试函数
        root = get_project_root()
        assert root == project_root


def test_get_project_root_prefer_python(monkeypatch, tmp_path):
    """测试优先选择 Python 项目（当同时存在 pyproject.toml 和 package.json 时）"""
    # 创建临时目录结构
    project_root = tmp_path / "mixed_project"
    project_root.mkdir()

    # 同时创建 pyproject.toml 和 package.json
    (project_root / "pyproject.toml").write_text('[tool.poetry]\nname = "test-python"')
    (project_root / "package.json").write_text('{"name": "test-nodejs"}')

    # 创建子目录结构
    src_dir = project_root / "src" / "working_path"
    src_dir.mkdir(parents=True)

    # 模拟当前文件在子目录中
    with monkeypatch.context() as m:
        m.setattr(
            "mark2pdf.helper_workingpath.helper_working_path.__file__",
            str(src_dir / "helper_working_path.py"),
        )

        # 测试函数 - 应该优先返回 Python 项目根目录
        root = get_project_root()
        assert root == project_root


def test_get_project_root_not_found(monkeypatch, tmp_path):
    """测试找不到项目根目录时的错误"""
    # 创建临时目录结构（没有项目文件）
    random_dir = tmp_path / "random_dir"
    random_dir.mkdir()

    # 模拟当前文件在随机目录中
    with monkeypatch.context() as m:
        m.setattr(
            "mark2pdf.helper_workingpath.helper_working_path.__file__",
            str(random_dir / "helper_working_path.py"),
        )

        # 应该抛出 FileNotFoundError
        with pytest.raises(FileNotFoundError, match="找不到项目根目录标识文件"):
            get_project_root()


def test_create_working_dirs():
    """测试创建 working 目录结构"""
    with (
        patch("mark2pdf.helper_workingpath.helper_working_path.get_project_root") as mock_root,
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("pathlib.Path.exists") as mock_exists,
        patch("mark2pdf.ConfigManager.load") as mock_load,
    ):
        mock_root.return_value = Path("/fake/project")
        mock_exists.return_value = False  # 所有目录都不存在
        mock_load.return_value = MagicMock(data_root=None)

        dirs = create_working_dirs()

        assert dirs["working"] == Path("/fake/project")
        assert dirs["in"] == Path("/fake/project/in")
        assert dirs["out"] == Path("/fake/project/out")
        assert dirs["tmp"] == Path("/fake/project/tmp")

        # 验证 mkdir 被调用了 3 次（每个目录一次）
        assert mock_mkdir.call_count == 3


def test_create_working_dirs_existing():
    """测试创建 working 目录结构 - 目录已存在的情况"""
    with (
        patch("mark2pdf.helper_workingpath.helper_working_path.get_project_root") as mock_root,
        patch("mark2pdf.ConfigManager.load") as mock_load,
    ):
        mock_root.return_value = Path("/fake/project")
        mock_load.return_value = MagicMock(data_root=None)

        # 模拟目录已存在
        with patch("pathlib.Path.exists") as mock_exists:
            # 让第一个目录 (in) 返回 True，其他返回 False
            call_count = [0]

            def exists_side_effect():
                call_count[0] += 1
                return call_count[0] == 1  # 只有第一个目录存在

            mock_exists.side_effect = exists_side_effect

            with pytest.raises(FileExistsError, match="目录已存在"):
                create_working_dirs()


def test_safesave_path_new_file():
    """测试安全保存路径 - 新文件"""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = False
        result = safesave_path("test.txt")
        assert result == "test.txt"


def test_safesave_path_existing_file():
    """测试安全保存路径 - 已存在文件"""
    with (
        patch("pathlib.Path.exists") as mock_exists,
        patch("mark2pdf.helper_workingpath.helper_working_path.time.strftime") as mock_time,
    ):
        mock_exists.return_value = True
        mock_time.return_value = "01-01-1200"

        result = safesave_path("test.txt")
        assert "test_01-01-1200.txt" in result


def test_resolve_inout_paths_basic():
    """测试基本输入输出路径解析"""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        mock_config = create_mock_config(Path("/fake/project"))

        in_path, out_path = resolve_inout_paths("test.md", config=mock_config)

        assert in_path == "/fake/project/in/test.md"
        assert "test_" in out_path and out_path.endswith(".md")


def test_resolve_inout_paths_file_not_found():
    """测试文件不存在的情况"""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = False
        mock_config = create_mock_config(Path("/fake/project"))

        with pytest.raises(FileNotFoundError, match="找不到输入文件"):
            resolve_inout_paths("nonexistent.md", config=mock_config)


def test_resolve_inout_paths_custom_outfile():
    """测试自定义输出文件名"""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        mock_config = create_mock_config(Path("/fake/project"))

        in_path, out_path = resolve_inout_paths(
            "test.md", outfile="custom_output.md", config=mock_config
        )

        assert in_path == "/fake/project/in/test.md"
        assert "custom_output_" in out_path and out_path.endswith(".md")


def test_safesave_path_with_different_extensions():
    """测试不同文件扩展名的安全保存"""
    with (
        patch("pathlib.Path.exists") as mock_exists,
        patch("mark2pdf.helper_workingpath.helper_working_path.time.strftime") as mock_time,
    ):
        mock_exists.return_value = True
        mock_time.return_value = "01-01-1200"

        # 测试不同扩展名
        result1 = safesave_path("test.txt")
        result2 = safesave_path("test.csv")
        result3 = safesave_path("test.json")

        assert "test_01-01-1200.txt" in result1
        assert "test_01-01-1200.csv" in result2
        assert "test_01-01-1200.json" in result3


def test_resolve_inout_paths_with_different_extensions():
    """测试不同文件扩展名的路径解析"""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        mock_config = create_mock_config(Path("/fake/project"))

        # 测试不同输入扩展名，默认输出为 md
        in_path1, out_path1 = resolve_inout_paths("test.txt", config=mock_config)
        in_path2, out_path2 = resolve_inout_paths("test.csv", config=mock_config)

        assert in_path1 == "/fake/project/in/test.txt"
        assert in_path2 == "/fake/project/in/test.csv"
        assert out_path1.endswith(".md")
        assert out_path2.endswith(".md")


def test_resolve_inout_paths_custom_ext():
    """测试自定义输出文件扩展名"""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        mock_config = create_mock_config(Path("/fake/project"))

        in_path, out_path = resolve_inout_paths("test.md", ext="txt", config=mock_config)

        assert in_path == "/fake/project/in/test.md"
        assert out_path.endswith(".txt")


def test_resolve_inout_paths_custom_directories():
    """测试自定义输入输出目录"""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        mock_config = create_mock_config(Path("/fake/project"))

        # 测试自定义输入输出目录
        in_path, out_path = resolve_inout_paths(
            "test.md", indir="custom_in", outdir="custom_out", ext="txt", config=mock_config
        )

        assert in_path == "/fake/project/custom_in/test.md"
        assert out_path.endswith(".txt")
        assert "custom_out" in out_path


def test_resolve_inout_paths_rejects_directory_paths():
    """测试拒绝包含目录路径的输入文件名"""
    with patch("mark2pdf.helper_workingpath.helper_working_path.get_project_root") as mock_root:
        mock_root.return_value = Path("/fake/project")

        # 测试包含目录路径的情况
        with pytest.raises(ValueError, match="包含目录路径"):
            resolve_inout_paths("subdir/test.md")
        with pytest.raises(ValueError, match="包含目录路径"):
            resolve_inout_paths("../test.md")
        with pytest.raises(ValueError, match="包含目录路径"):
            resolve_inout_paths("./test.md")

        # 测试不带扩展名的目录路径也应该被拒绝
        with pytest.raises(ValueError, match="包含目录路径"):
            resolve_inout_paths("subdir/test")
        with pytest.raises(ValueError, match="包含目录路径"):
            resolve_inout_paths("../test")
        with pytest.raises(ValueError, match="包含目录路径"):
            resolve_inout_paths("./test")


def test_resolve_inout_paths_error_messages():
    """测试错误消息内容"""
    mock_config = create_mock_config(Path("/fake/project"))

    # 测试目录路径错误消息
    with pytest.raises(ValueError, match="输入文件名 'subdir/test.md' 包含目录路径"):
        resolve_inout_paths("subdir/test.md", config=mock_config)

    # 测试文件不存在错误消息
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = False
        with pytest.raises(
            FileNotFoundError,
            match="找不到输入文件 '/fake/project/in/nonexistent.md'",
        ):
            resolve_inout_paths("nonexistent.md", config=mock_config)


def test_resolve_inout_paths_no_extension():
    """测试没有文件扩展名的路径解析"""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        mock_config = create_mock_config(Path("/fake/project"))

        # 测试没有扩展名的文件，应该自动添加.md
        in_path, out_path = resolve_inout_paths("test", config=mock_config)

        assert in_path == "/fake/project/in/test.md"
        assert "test_" in out_path
        assert out_path.endswith(".md")


def test_create_working_dirs_integration(tmp_path):
    """集成测试：实际创建目录和验证安全机制"""
    # 临时修改 get_project_root 返回临时目录
    original_get_project_root = None

    try:
        import mark2pdf.helper_workingpath.helper_working_path as helper_working_path

        original_get_project_root = helper_working_path.get_project_root
        helper_working_path.get_project_root = lambda: tmp_path
        with patch("mark2pdf.ConfigManager.load") as mock_load:
            mock_load.return_value = MagicMock(data_root=None)

            # 第一次创建应该成功
            dirs = create_working_dirs()

            # 验证目录结构
            assert dirs["working"] == tmp_path
            assert dirs["in"] == tmp_path / "in"
            assert dirs["out"] == tmp_path / "out"
            assert dirs["tmp"] == tmp_path / "tmp"

            # 验证目录实际存在
            assert dirs["working"].exists()
            assert dirs["in"].exists()
            assert dirs["out"].exists()
            assert dirs["tmp"].exists()

            # 第二次创建应该失败
            with pytest.raises(FileExistsError, match="目录已存在"):
                create_working_dirs()

    finally:
        # 恢复原始函数
        if original_get_project_root:
            helper_working_path.get_project_root = original_get_project_root


def test_resolve_template_path_system_fallback():
    """测试系统模板回退机制"""
    with patch("mark2pdf.helper_workingpath.helper_working_path.get_project_root") as mock_root:
        mock_root.return_value = Path("/fake/project")

        # 修复: Patch ConfigManager.load 以避免在测试环境中寻找真实 root 失败
        with (
            patch("mark2pdf.ConfigManager.load", return_value=None),
            patch(
                "mark2pdf.helper_workingpath.helper_working_path._get_global_template_dir",
                return_value=Path("/global/templates"),
            ),
            patch(
                "mark2pdf.helper_workingpath.helper_working_path._get_bundled_template_path",
                return_value=None,
            ),
        ):
            # 模拟系统模板存在
            # 使用 autospec=True 确保 mock 接收 self (Path实例) 参数
            with patch("pathlib.Path.exists", autospec=True) as mock_exists:

                def exists_side_effect(self):
                    # 在 pytest 中，self 是一个 PosixPath 对象
                    return str(self) == "/fake/project/src/mark2pdf/templates/nb.typ"

                mock_exists.side_effect = exists_side_effect

                # 不带 config 调用
                # 此时内部 ConfigManager.load 返回 None (模拟不可用或未配置)，触发 Legacy 逻辑
                path = resolve_template_path("nb.typ")
                assert path == "/fake/project/src/mark2pdf/templates/nb.typ"


def test_resolve_template_path_local_priority():
    """测试本地模板优先机制"""
    with patch("mark2pdf.helper_workingpath.helper_working_path.get_project_root") as mock_root:
        mock_root.return_value = Path("/fake/project")

        mock_config = create_mock_config(Path("/local/project"))
        mock_config.paths.template = "templates"

        # 模拟本地模板存在
        with patch("pathlib.Path.exists", autospec=True) as mock_exists:

            def exists_side_effect(self):
                # 本地模板存在
                if str(self) == "/local/project/templates/custom.typ":
                    return True
                return False

            mock_exists.side_effect = exists_side_effect

            # 带 config 调用
            path = resolve_template_path("custom.typ", config=mock_config)
            assert path == "/local/project/templates/custom.typ"


def test_resolve_template_path_global_fallback():
    """测试全局模板回退机制"""
    with (
        patch("mark2pdf.ConfigManager.load", return_value=None),
        patch(
            "mark2pdf.helper_workingpath.helper_working_path._get_global_template_dir",
            return_value=Path("/global/templates"),
        ),
        patch(
            "mark2pdf.helper_workingpath.helper_working_path._get_bundled_template_path",
            return_value=None,
        ),
    ):
        with patch("pathlib.Path.exists", autospec=True) as mock_exists:

            def exists_side_effect(self):
                return str(self) == "/global/templates/global.typ"

            mock_exists.side_effect = exists_side_effect

            path = resolve_template_path("global.typ")
            assert path == "/global/templates/global.typ"


def test_resolve_template_path_bundled_fallback():
    """测试包内置模板回退机制"""
    with (
        patch("mark2pdf.ConfigManager.load", return_value=None),
        patch(
            "mark2pdf.helper_workingpath.helper_working_path._get_global_template_dir",
            return_value=Path("/global/templates"),
        ),
        patch(
            "mark2pdf.helper_workingpath.helper_working_path._get_bundled_template_path",
            return_value=Path("/pkg/templates/nb.typ"),
        ),
    ):
        with patch("pathlib.Path.exists", autospec=True) as mock_exists:
            mock_exists.return_value = False
            path = resolve_template_path("nb.typ")
            assert path == "/pkg/templates/nb.typ"


def test_resolve_template_path_security():
    """测试模板路径安全性检查 - 仅拒绝父目录遍历"""
    # 父目录遍历应该抛出 FileNotFoundError（因为不会匹配任何有效路径）
    with pytest.raises(FileNotFoundError, match="找不到模板文件"):
        resolve_template_path("../hack.typ")

    # 子目录路径应该被允许（如 nb/nb.typ）
    # 这里不测试 subdir/hack.typ，因为子目录现在是合法的


def test_resolve_template_path_not_found():
    """测试模板找不到的情况"""
    with patch("mark2pdf.helper_workingpath.helper_working_path.get_project_root") as mock_root:
        mock_root.return_value = Path("/fake/project")

        # 同样 patch ConfigManager.load 避免环境问题
        with (
            patch("mark2pdf.ConfigManager.load", return_value=None),
            patch(
                "mark2pdf.helper_workingpath.helper_working_path._get_global_template_dir",
                return_value=Path("/global/templates"),
            ),
            patch(
                "mark2pdf.helper_workingpath.helper_working_path._get_bundled_template_path",
                return_value=None,
            ),
        ):
            with patch("pathlib.Path.exists", autospec=True) as mock_exists:
                mock_exists.return_value = False

                with pytest.raises(FileNotFoundError, match="找不到模板文件"):
                    resolve_template_path("missing.typ")


def test_resolve_template_path_variants():
    """测试模板变体查找：nb -> nb.typ / nb/nb.typ / nb/index.typ"""
    with (
        patch("mark2pdf.ConfigManager.load", return_value=None),
        patch(
            "mark2pdf.helper_workingpath.helper_working_path._get_global_template_dir",
            return_value=Path("/global/templates"),
        ),
        patch(
            "mark2pdf.helper_workingpath.helper_working_path._get_bundled_template_path",
            return_value=None,
        ),
        patch(
            "mark2pdf.helper_workingpath.helper_working_path.get_project_root",
            return_value=Path("/fake/project"),
        ),
    ):
        # 测试1: 直接文件 nb.typ
        with patch("pathlib.Path.is_file", autospec=True) as mock_is_file:
            with patch("pathlib.Path.exists", autospec=True) as mock_exists:
                mock_exists.return_value = False

                def is_file_side_effect(self):
                    return str(self) == "/fake/project/src/mark2pdf/templates/nb.typ"

                mock_is_file.side_effect = is_file_side_effect

                path = resolve_template_path("nb")
                assert path == "/fake/project/src/mark2pdf/templates/nb.typ"

        # 测试2: 目录同名文件 nb/nb.typ
        with patch("pathlib.Path.is_file", autospec=True) as mock_is_file:
            with patch("pathlib.Path.exists", autospec=True) as mock_exists:
                mock_exists.return_value = False

                def is_file_side_effect(self):
                    return str(self) == "/fake/project/src/mark2pdf/templates/nb/nb.typ"

                mock_is_file.side_effect = is_file_side_effect

                path = resolve_template_path("nb")
                assert path == "/fake/project/src/mark2pdf/templates/nb/nb.typ"

        # 测试3: 目录 index 文件 nb/index.typ
        with patch("pathlib.Path.is_file", autospec=True) as mock_is_file:
            with patch("pathlib.Path.exists", autospec=True) as mock_exists:
                mock_exists.return_value = False

                def is_file_side_effect(self):
                    return str(self) == "/fake/project/src/mark2pdf/templates/nb/index.typ"

                mock_is_file.side_effect = is_file_side_effect

                path = resolve_template_path("nb")
                assert path == "/fake/project/src/mark2pdf/templates/nb/index.typ"


def test_resolve_template_path_subdir_compat():
    """测试子目录路径兼容性：nb/nb.typ 仍然有效"""
    with (
        patch("mark2pdf.ConfigManager.load", return_value=None),
        patch(
            "mark2pdf.helper_workingpath.helper_working_path._get_global_template_dir",
            return_value=Path("/global/templates"),
        ),
        patch(
            "mark2pdf.helper_workingpath.helper_working_path._get_bundled_template_path",
            return_value=None,
        ),
        patch(
            "mark2pdf.helper_workingpath.helper_working_path.get_project_root",
            return_value=Path("/fake/project"),
        ),
    ):
        with patch("pathlib.Path.is_file", autospec=True) as mock_is_file:
            with patch("pathlib.Path.exists", autospec=True) as mock_exists:

                def is_file_side_effect(self):
                    # 变体不存在
                    return False

                def exists_side_effect(self):
                    # 完整路径存在
                    return str(self) == "/fake/project/src/mark2pdf/templates/nb/nb.typ"

                mock_is_file.side_effect = is_file_side_effect
                mock_exists.side_effect = exists_side_effect

                path = resolve_template_path("nb/nb.typ")
                assert path == "/fake/project/src/mark2pdf/templates/nb/nb.typ"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
