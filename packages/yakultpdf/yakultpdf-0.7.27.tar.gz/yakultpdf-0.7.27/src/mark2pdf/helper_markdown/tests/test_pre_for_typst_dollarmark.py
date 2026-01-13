r"""
测试 pre_for_typst_dollarmark 功能
将普通文本中的 $ 改为 \$ ，但不影响数学公式
"""

import sys
from pathlib import Path

# 添加父目录到 sys.path，使得可以导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_preprocess import pre_for_typst_dollarmark


def test_inline_math_formula():
    """测试行内数学公式中的 $ 不应该被转义"""
    content = "The formula is $\\sqrt{3x-1}+(1+x)^2$ in the equation."
    expected = "The formula is $\\sqrt{3x-1}+(1+x)^2$ in the equation."
    result = pre_for_typst_dollarmark(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_block_math_formula():
    """测试块数学公式中的 $ 不应该被转义"""
    content = """Some text
$$
x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}
$$
More text"""
    expected = content  # 应该保持不变
    result = pre_for_typst_dollarmark(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_dollar_in_link_url_not_escaped():
    """测试链接 URL 中的 $ 不应该被转义"""
    content = "[link](https://example.com/$value)"
    expected = "[link](https://example.com/$value)"
    result = pre_for_typst_dollarmark(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_dollar_in_link_text_escaped():
    """测试链接文本中的 $ 应该被转义"""
    content = "[$price](https://example.com)"
    expected = "[\\$price](https://example.com)"
    result = pre_for_typst_dollarmark(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_dollar_in_inline_code_not_escaped():
    """测试行内代码中的 $ 不应该被转义"""
    content = "Use `$PATH` to resolve the binary."
    expected = "Use `$PATH` to resolve the binary."
    result = pre_for_typst_dollarmark(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_dollar_in_code_block_not_escaped():
    """测试代码块中的 $ 不应该被转义"""
    content = "```\n$VALUE=1\n```"
    expected = "```\n$VALUE=1\n```"
    result = pre_for_typst_dollarmark(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_already_escaped():
    """测试已经转义的 $ 不会被重复转义"""
    content = "The price is \\$100"
    expected = "The price is \\$100"
    result = pre_for_typst_dollarmark(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_inline_simple_math_letters_not_escaped():
    """$S$ 这样的简单数学变量不应被转义"""
    content = "能够正确输出链的状态 $S$。"
    expected = "能够正确输出链的状态 $S$。"
    result = pre_for_typst_dollarmark(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_inline_math_function_not_escaped():
    """$STF(S,B)$ 这样的数学表达式不应被转义"""
    content = "证明 $STF(S,B)$ 能够正确输出状态。"
    expected = "证明 $STF(S,B)$ 能够正确输出状态。"
    result = pre_for_typst_dollarmark(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"


def test_currency_tokens_still_escaped():
    """$BTC 和 $500 这样的货币/代币仍应转义"""
    content = "价格为 $500，代币 $BTC。"
    expected = "价格为 \\$500，代币 \\$BTC。"
    result = pre_for_typst_dollarmark(content)
    assert result == expected, f"Expected: {expected}\nGot: {result}"
