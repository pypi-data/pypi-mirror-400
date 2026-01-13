import sys
from pathlib import Path

import pytest

# 添加父目录到路径，以便导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_preprocess import pre_remove_links


class TestPreRemoveLinks:
    """测试 pre_remove_links 函数"""

    def test_remove_simple_link(self):
        """测试移除简单链接"""
        content = "这是一个 [链接](http://example.com) 测试。"
        expected = "这是一个链接测试。"
        result = pre_remove_links(content)
        assert result == expected

    def test_remove_multiple_links(self):
        """测试移除多个链接"""
        content = "这是 [第一个链接](http://example1.com) 和 [第二个链接](http://example2.com)。"
        expected = "这是第一个链接和第二个链接。"
        result = pre_remove_links(content)
        assert result == expected

    def test_preserve_images(self):
        """测试保留图片（不删除）"""
        content = "这是图片![alt text](image.jpg) 和链接 [文本](http://example.com)。"
        expected = "这是图片![alt text](image.jpg) 和链接文本。"
        result = pre_remove_links(content)
        assert result == expected

    def test_empty_link_text(self):
        """测试空链接文本"""
        content = "这是空链接 [](http://example.com) 测试。"
        expected = "这是空链接测试。"
        result = pre_remove_links(content)
        assert result == expected

    def test_no_links(self):
        """测试没有链接的内容"""
        content = "这是普通文本，没有链接。"
        expected = "这是普通文本，没有链接。"
        result = pre_remove_links(content)
        assert result == expected

    def test_links_with_special_characters(self):
        """测试包含特殊字符的链接"""
        content = "这是 [特殊链接](http://example.com/path?param=value&other=123) 测试。"
        expected = "这是特殊链接测试。"
        result = pre_remove_links(content)
        assert result == expected

    def test_links_with_anchors(self):
        """测试包含锚点的链接"""
        content = "这是 [锚点链接](http://example.com#section) 测试。"
        expected = "这是锚点链接测试。"
        result = pre_remove_links(content)
        assert result == expected

    def test_relative_links(self):
        """测试相对路径链接"""
        content = "这是 [相对链接](./page.html) 测试。"
        expected = "这是相对链接测试。"
        result = pre_remove_links(content)
        assert result == expected

    def test_links_in_code_block_preserved(self):
        """测试代码块中的链接不应被移除"""
        content = """这是代码：
```
[code](http://example.com)
```
这是 [链接](http://example.com)。"""
        expected = """这是代码：
```
[code](http://example.com)
```
这是链接。"""
        result = pre_remove_links(content)
        assert result == expected

    def test_links_in_inline_code_preserved(self):
        """测试行内代码中的链接不应被移除"""
        content = "内联代码：`[code](http://example.com)` 和 [链接](http://example.com)。"
        expected = "内联代码：`[code](http://example.com)` 和链接。"
        result = pre_remove_links(content)
        assert result == expected

    def test_mixed_content(self):
        """测试混合内容（链接、图片、普通文本）"""
        content = """这是普通文本。
这是 [链接](http://example.com)。
这是图片![图片](image.jpg)。
这是另一个 [链接](http://test.com)。"""
        expected = """这是普通文本。
这是链接。
这是图片![图片](image.jpg)。
这是另一个链接。"""
        result = pre_remove_links(content)
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
