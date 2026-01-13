import sys
from pathlib import Path

import pytest

# 添加父目录到路径，以便导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_preprocess import extract_frontmatter


class TestExtractFrontmatter:
    """测试 extract_frontmatter 函数"""

    def test_extract_simple_frontmatter(self, tmp_path):
        """测试提取简单的 frontmatter"""
        # 创建临时文件
        test_file = tmp_path / "test.md"
        test_file.write_text("""---
title: 测试文档
author: 作者
---
这是正文内容。""")

        expected = {"title": "测试文档", "author": "作者"}
        result = extract_frontmatter(test_file)
        assert result == expected

    def test_extract_complex_frontmatter(self, tmp_path):
        """测试提取复杂的 frontmatter"""
        test_file = tmp_path / "test.md"
        test_file.write_text("""---
title: 测试文档
author: 作者
date: 2024-01-01
tags: [测试, 文档]
description: 这是一个测试文档
---
这是正文内容。""")

        result = extract_frontmatter(test_file)
        assert result["title"] == "测试文档"
        assert result["author"] == "作者"
        assert result["date"].year == 2024  # YAML 会将日期解析为 datetime.date 对象
        assert result["tags"] == ["测试", "文档"]
        assert result["description"] == "这是一个测试文档"

    def test_no_frontmatter(self, tmp_path):
        """测试没有 frontmatter 的情况"""
        test_file = tmp_path / "test.md"
        test_file.write_text("这是普通内容，没有 frontmatter。")

        result = extract_frontmatter(test_file)
        assert result == {}

    def test_empty_frontmatter(self, tmp_path):
        """测试空的 frontmatter"""
        test_file = tmp_path / "test.md"
        test_file.write_text("""---
---
这是正文内容。""")

        result = extract_frontmatter(test_file)
        assert result == {}

    def test_incomplete_frontmatter(self, tmp_path):
        """测试不完整的 frontmatter（只有开始标记）"""
        test_file = tmp_path / "test.md"
        test_file.write_text("""---
title: 测试文档
这是正文内容。""")

        result = extract_frontmatter(test_file)
        assert result == {}

    def test_frontmatter_with_comments(self, tmp_path):
        """测试 frontmatter 中包含注释"""
        test_file = tmp_path / "test.md"
        test_file.write_text("""---
title: 测试文档
# 这是一个注释
author: 作者
---
这是正文内容。""")

        expected = {"title": "测试文档", "author": "作者"}
        result = extract_frontmatter(test_file)
        assert result == expected

    def test_multiline_values(self, tmp_path):
        """测试多行值"""
        test_file = tmp_path / "test.md"
        test_file.write_text("""---
title: 测试文档
description: |
  这是一个多行
  描述文本
author: 作者
---
这是正文内容。""")

        expected = {
            "title": "测试文档",
            "description": "这是一个多行\n描述文本\n",
            "author": "作者",
        }
        result = extract_frontmatter(test_file)
        assert result == expected

    def test_nonexistent_file(self):
        """测试文件不存在的情况"""
        nonexistent_file = Path("/nonexistent/path/test.md")
        result = extract_frontmatter(nonexistent_file)
        assert result == {}

    def test_invalid_yaml(self, tmp_path):
        """测试无效的 YAML 内容"""
        test_file = tmp_path / "test.md"
        test_file.write_text("""---
title: 测试文档
author: 作者
invalid_yaml: [unclosed list
---
这是正文内容。""")

        # 应该返回空字典，并打印警告
        result = extract_frontmatter(test_file)
        assert result == {}

    def test_frontmatter_eof_no_trailing_newline(self, tmp_path):
        """测试 frontmatter 在 EOF 结束（无尾随换行）"""
        test_file = tmp_path / "test.md"
        test_file.write_text("""---
title: 测试文档
---""")

        result = extract_frontmatter(test_file)
        assert result == {"title": "测试文档"}

    # ===== 字符串输入测试 =====

    def test_string_basic_frontmatter(self):
        """测试字符串输入：基本 frontmatter 提取"""
        content = """---
title: 测试文档
author: 张三
---

# 正文内容
"""
        result = extract_frontmatter(content)
        assert result["title"] == "测试文档"
        assert result["author"] == "张三"

    def test_string_no_frontmatter(self):
        """测试字符串输入：无 frontmatter 的情况"""
        content = """# 标题

这是正文内容。
"""
        result = extract_frontmatter(content)
        assert result == {}

    def test_string_empty_frontmatter(self):
        """测试字符串输入：空 frontmatter"""
        content = """---
---

# 内容
"""
        result = extract_frontmatter(content)
        assert result == {}

    def test_string_with_list(self):
        """测试字符串输入：包含列表的 frontmatter"""
        content = """---
title: 测试
tags:
  - python
  - markdown
---

正文
"""
        result = extract_frontmatter(content)
        assert result["tags"] == ["python", "markdown"]

    def test_string_invalid_yaml(self):
        """测试字符串输入：无效 YAML frontmatter"""
        content = """---
title: [invalid
yaml:
---

正文
"""
        result = extract_frontmatter(content)
        assert result == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
