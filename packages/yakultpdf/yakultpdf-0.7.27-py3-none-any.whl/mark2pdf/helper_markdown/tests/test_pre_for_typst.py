import sys
from pathlib import Path

import pytest

# 添加父目录到路径，以便导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_preprocess import pre_for_typst


class TestPreForTypst:
    """测试 pre_for_typst 组合链路"""

    def test_pre_for_typst_combined(self):
        """测试组合链路的基础转换"""
        content = "# **Title**\n\nThis is _italic_ and @user costs $5.\n\nMath $x$.\n"
        expected = "# Title\n\nThis is **italic** and \\@user costs \\$5.\n\nMath $x$.\n"
        result = pre_for_typst(content)
        assert result == expected

    def test_pre_for_typst_keeps_code_blocks(self):
        """测试代码块内内容不被组合链路处理"""
        content = "Outside _italic_ @user $5\n\n```\n@code $10 _italic_\n```\n"
        expected = "Outside **italic** \\@user \\$5\n\n```\n@code $10 _italic_\n```\n"
        result = pre_for_typst(content)
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
