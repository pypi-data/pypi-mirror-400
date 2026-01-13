import sys
from pathlib import Path

import pytest

# 添加父目录到路径，以便导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_preprocess import pre_clean_frontmatter


class TestPreCleanFrontmatter:
    """测试 pre_clean_frontmatter 函数"""

    def test_remove_simple_frontmatter(self):
        """测试移除简单的 frontmatter"""
        content = """---
title: 测试文档
author: 作者
---
这是正文内容。"""
        expected = "这是正文内容。"
        result = pre_clean_frontmatter(content)
        assert result == expected

    def test_remove_complex_frontmatter(self):
        """测试移除复杂的 frontmatter"""
        content = """---
title: 测试文档
author: 作者
date: 2024-01-01
tags: [测试，文档]
description: 这是一个测试文档
---
这是正文内容。
包含多行。"""
        expected = "这是正文内容。\n包含多行。"
        result = pre_clean_frontmatter(content)
        assert result == expected

    def test_no_frontmatter(self):
        """测试没有 frontmatter 的情况"""
        content = "这是普通内容，没有 frontmatter。"
        expected = "这是普通内容，没有 frontmatter。"
        result = pre_clean_frontmatter(content)
        assert result == expected

    def test_incomplete_frontmatter(self):
        """测试不完整的 frontmatter（只有开始标记）"""
        content = """---
title: 测试文档
这是正文内容。"""
        expected = content  # 应该保持原样
        result = pre_clean_frontmatter(content)
        assert result == expected

    def test_frontmatter_with_extra_dashes(self):
        """测试 frontmatter 中有额外的破折号"""
        content = """---
title: 测试文档
---
这是正文内容。"""
        expected = "这是正文内容。"
        result = pre_clean_frontmatter(content)
        assert result == expected

    def test_frontmatter_eof_no_trailing_newline(self):
        """测试 frontmatter 在 EOF 结束（无尾随换行）"""
        content = """---
title: 测试文档
---"""
        expected = ""
        result = pre_clean_frontmatter(content)
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
