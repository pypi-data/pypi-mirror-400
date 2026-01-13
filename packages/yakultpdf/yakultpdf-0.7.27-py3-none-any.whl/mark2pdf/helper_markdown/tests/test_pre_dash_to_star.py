"""
测试 pre_dash_to_star 功能
将下划线斜体改为星号加粗
"""

import sys
from pathlib import Path

import pytest

# 添加父目录到 sys.path，使得可以导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_preprocess import pre_dash_to_star


class TestDashToStar:
    """测试 pre_dash_to_star 功能: 将下划线斜体改为星号加粗"""

    @pytest.mark.parametrize(
        "content, expected",
        [
            # 基本转换
            (
                "_TVL: Increased from $5.88B to $7.55B (+28.4%)_",
                "**TVL: Increased from $5.88B to $7.55B (+28.4%)**",
            ),
            ("Normal text without italic", "Normal text without italic"),
            # 复杂基本场景
            ("_First italic_ and _second italic_", "**First italic** and **second italic**"),
            (
                """First line with _italic text_.

Second line with _another italic_.

[Link](https://example.com/test_page)""",
                """First line with **italic text**.

Second line with **another italic**.

[Link](https://example.com/test_page)""",
            ),
            # 混合链接场景
            ("_[abc](https://x.com/@ethena_labs)_", "**[abc](https://x.com/@ethena_labs)**"),
            (
                "_Important:_ Check [this link](https://example.com/some_page)",
                "**Important:** Check [this link](https://example.com/some_page)",
            ),
            (
                "_See_ [Ethena Labs](https://x.com/@ethena_labs) for details",
                "**See** [Ethena Labs](https://x.com/@ethena_labs) for details",
            ),
            # 带标点
            ("_Note:_ This is important.", "**Note:** This is important."),
            # 保护场景：不应转换的情况
            ("[Ethena](https://x.com/@ethena_labs)", "[Ethena](https://x.com/@ethena_labs)"),
            ("Use `snake_case` in Python", "Use `snake_case` in Python"),
            ("This is $V_total = V_A + V_B$ in math", "This is $V_total = V_A + V_B$ in math"),
            (
                "$$\n  (V_A+V_B)- V_{total} \\ > \\ \\\n$$",
                "$$\n  (V_A+V_B)- V_{total} \\ > \\ \\\n$$",
            ),
            (
                "![desc](./images/ethereum_evan/MEV_pareto_distribution.PNG)",
                "![desc](./images/ethereum_evan/MEV_pareto_distribution.PNG)",
            ),
            (
                "![*A graphic by @cripticwoods_ *](./img.PNG)",
                "![*A graphic by @cripticwoods_ *](./img.PNG)",
            ),
            ("__Bold__ text", "__Bold__ text"),  # 双下划线加粗保持不变
            ("foo_bar_baz", "foo_bar_baz"),  # 单词内部下划线不转换
            # 加粗与斜体交互
            ("**_单个笔记的设计_**", "**单个笔记的设计**"),
            ("**Bold _italic_ text**", "**Bold italic text**"),
            ("**_text1_** and _text2_", "**text1** and **text2**"),
            ("**_First_** and **_Second_**", "**First** and **Second**"),
            # 转义下划线
            ("\\_\\_\\_\\_", "\\_\\_\\_\\_"),
            ("\\_escaped\\_ and _italic_", "\\_escaped\\_ and **italic**"),
            ("\\\\_text_", "\\\\**text**"),  # 双转义，下划线本身未被转义
        ],
    )
    def test_conversion_rules(self, content, expected):
        """测试各种转换规则和保护场景"""
        assert pre_dash_to_star(content) == expected

    @pytest.mark.parametrize(
        "fence_char, fence_count",
        [
            ("`", 3),
            ("`", 4),
        ],
    )
    def test_code_block_protection(self, fence_char, fence_count):
        """测试代码块中的下划线保护"""
        fence = fence_char * fence_count
        content = f"""Use the function:

{fence}
run_pandoc_typst()
{fence}

This is normal text."""
        assert pre_dash_to_star(content) == content
