import sys
import tempfile
from pathlib import Path

import pytest

# 添加父目录到路径，以便导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_preprocess import pre_image_verify


class TestPreImageVerify:
    """测试 pre_image_verify 函数"""

    def test_no_images(self):
        """测试没有图片的内容"""
        content = "这是普通文本，没有图片。"
        file_path = "/tmp/test.md"
        result = pre_image_verify(content, file_path)
        assert result == content

    def test_valid_local_image(self):
        """测试有效的本地图片"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试图片文件
            image_path = Path(temp_dir) / "test.jpg"
            image_path.touch()

            content = "这是图片![alt text](test.jpg) 测试。"
            file_path = str(Path(temp_dir) / "test.md")

            result = pre_image_verify(content, file_path)
            assert result == content

    def test_invalid_local_image(self):
        """测试无效的本地图片"""
        with tempfile.TemporaryDirectory() as temp_dir:
            content = "这是图片![alt text](nonexistent.jpg) 测试。"
            file_path = str(Path(temp_dir) / "test.md")

            with pytest.raises(ValueError):
                pre_image_verify(content, file_path)

    def test_network_image(self):
        """测试网络图片（应该失败）"""
        content = "这是网络图片![alt text](http://example.com/image.jpg) 测试。"
        file_path = "/tmp/test.md"

        with pytest.raises(ValueError):
            pre_image_verify(content, file_path)

    def test_https_image(self):
        """测试 HTTPS 网络图片（应该失败）"""
        content = "这是 HTTPS 图片![alt text](https://example.com/image.jpg) 测试。"
        file_path = "/tmp/test.md"

        with pytest.raises(ValueError):
            pre_image_verify(content, file_path)

    def test_multiple_valid_images(self):
        """测试多个有效图片"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试图片文件
            (Path(temp_dir) / "image1.jpg").touch()
            (Path(temp_dir) / "image2.png").touch()

            content = "图片 1![alt1](image1.jpg) 和图片 2![alt2](image2.png)。"
            file_path = str(Path(temp_dir) / "test.md")

            result = pre_image_verify(content, file_path)
            assert result == content

    def test_mixed_valid_invalid_images(self):
        """测试混合有效和无效图片"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 只创建一个图片文件
            (Path(temp_dir) / "valid.jpg").touch()

            content = "有效图片![valid](valid.jpg) 和无效图片![invalid](invalid.jpg)。"
            file_path = str(Path(temp_dir) / "test.md")

            with pytest.raises(ValueError):
                pre_image_verify(content, file_path)

    def test_image_with_path(self):
        """测试带路径的图片"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建子目录和图片
            subdir = Path(temp_dir) / "images"
            subdir.mkdir()
            (subdir / "test.jpg").touch()

            content = "这是图片![alt text](images/test.jpg) 测试。"
            file_path = str(Path(temp_dir) / "test.md")

            result = pre_image_verify(content, file_path)
            assert result == content

    def test_empty_alt_text(self):
        """测试空 alt 文本的图片"""
        with tempfile.TemporaryDirectory() as temp_dir:
            (Path(temp_dir) / "test.jpg").touch()

            content = "这是图片![](test.jpg) 测试。"
            file_path = str(Path(temp_dir) / "test.md")

            result = pre_image_verify(content, file_path)
            assert result == content

    def test_image_with_special_characters(self):
        """测试包含特殊字符的图片路径"""
        with tempfile.TemporaryDirectory() as temp_dir:
            (Path(temp_dir) / "test-image_123.jpg").touch()

            content = "这是图片![alt text](test-image_123.jpg) 测试。"
            file_path = str(Path(temp_dir) / "test.md")

            result = pre_image_verify(content, file_path)
            assert result == content

    def test_ignore_images_in_code_block(self, tmp_path):
        """测试代码块中的图片不参与验证"""
        content = """示例：
```
![alt](missing.png)
```
"""
        file_path = str(tmp_path / "test.md")
        result = pre_image_verify(content, file_path)
        assert result == content

    def test_ignore_images_in_inline_code(self, tmp_path):
        """测试行内代码中的图片不参与验证"""
        content = "示例：`![alt](missing.png)`"
        file_path = str(tmp_path / "test.md")
        result = pre_image_verify(content, file_path)
        assert result == content

    def test_image_with_title(self, tmp_path):
        """测试图片标题语法"""
        image_path = tmp_path / "test.jpg"
        image_path.touch()
        content = '![alt](test.jpg "title")'
        file_path = str(tmp_path / "test.md")
        result = pre_image_verify(content, file_path)
        assert result == content

    def test_image_with_parentheses(self, tmp_path):
        """测试图片路径包含括号"""
        image_path = tmp_path / "test(1).png"
        image_path.touch()
        content = "![alt](test(1).png)"
        file_path = str(tmp_path / "test.md")
        result = pre_image_verify(content, file_path)
        assert result == content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
