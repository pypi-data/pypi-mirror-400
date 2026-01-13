import sys
import tempfile
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 直接导入模块
from interfile_manager import cleanup_tmpfile, create_md_tmpfile, write_to_tmpfile


def test_create_md_tmpfile():
    """测试创建临时.md 文件"""
    # 创建一个临时目录作为测试环境
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建一个模拟的原始文件
        original_file = Path(temp_dir) / "test.md"
        original_file.write_text("# Test Content", encoding="utf-8")

        # 创建临时文件
        temp_fd, temp_path = create_md_tmpfile(str(original_file))

        # 验证临时文件路径
        assert Path(temp_path).exists()
        assert temp_path.endswith(".md")
        assert "pandoc2pdf_" in temp_path
        assert Path(temp_path).parent == Path(temp_dir)

        # 清理
        cleanup_tmpfile(temp_path)


def test_write_to_tmpfile():
    """测试写入临时文件"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_file = Path(temp_dir) / "test.md"
        original_file.write_text("# Test Content", encoding="utf-8")

        # 创建临时文件
        temp_fd, temp_path = create_md_tmpfile(str(original_file))

        # 写入内容
        test_content = "# Processed Content\n\nThis is processed markdown."
        write_to_tmpfile(temp_fd, test_content)

        # 验证文件内容
        with open(temp_path, encoding="utf-8") as f:
            content = f.read()
        assert content == test_content

        # 清理
        cleanup_tmpfile(temp_path)


def test_cleanup_tmpfile():
    """测试清理临时文件"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_file = Path(temp_dir) / "test.md"
        original_file.write_text("# Test Content", encoding="utf-8")

        # 创建临时文件
        temp_fd, temp_path = create_md_tmpfile(str(original_file))

        # 验证文件存在
        assert Path(temp_path).exists()

        # 清理文件
        cleanup_tmpfile(temp_path)

        # 验证清理成功
        assert not Path(temp_path).exists()


def test_cleanup_nonexistent_file():
    """测试清理不存在的文件"""
    with tempfile.TemporaryDirectory() as temp_dir:
        nonexistent_file = Path(temp_dir) / "nonexistent.md"

        # 清理不存在的文件应该不会抛出异常
        cleanup_tmpfile(str(nonexistent_file))

        # 验证文件确实不存在
        assert not Path(nonexistent_file).exists()


def test_custom_prefix():
    """测试自定义前缀"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_file = Path(temp_dir) / "test.md"
        original_file.write_text("# Test Content", encoding="utf-8")

        # 使用自定义前缀
        temp_fd, temp_path = create_md_tmpfile(str(original_file), prefix="custom_")

        # 验证前缀
        assert "custom_" in temp_path
        assert "pandoc2pdf_" not in temp_path

        # 清理
        cleanup_tmpfile(temp_path)


if __name__ == "__main__":
    # 运行所有测试
    test_create_md_tmpfile()
    print("✓ test_create_md_tmpfile passed")

    test_write_to_tmpfile()
    print("✓ test_write_to_tmpfile passed")

    test_cleanup_tmpfile()
    print("✓ test_cleanup_tmpfile passed")

    test_cleanup_nonexistent_file()
    print("✓ test_cleanup_nonexistent_file passed")

    test_custom_prefix()
    print("✓ test_custom_prefix passed")

    print("\n✅ 所有测试通过！")
