import sys
from pathlib import Path

import pytest

# 添加父目录到路径，以便导入 md_preprocess 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_preprocess import pre_add_line_breaks


class TestPreAddLineBreaks:
    """测试 pre_add_line_breaks 函数"""

    def test_simple_paragraphs(self):
        """测试简单段落之间添加空行"""
        content = "这是第一段。\n这是第二段。"
        expected = "这是第一段。\n\n这是第二段。"
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_already_separated_paragraphs(self):
        """测试已经分隔的段落（不重复添加）"""
        content = "这是第一段。\n\n这是第二段。"
        expected = "这是第一段。\n\n这是第二段。"
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_skip_code_blocks(self):
        """测试跳过代码块"""
        content = """这是段落。
```python
def hello():
    print("Hello")
```
这是代码块后的段落。"""
        expected = """这是段落。

```python
def hello():
    print("Hello")
```

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_skip_tables(self):
        """测试表格前后添加空行"""
        content = """这是段落。
| 列 1 | 列 2 |
|-----|-----|
| 数据 1 | 数据 2 |
这是表格后的段落。"""
        expected = """这是段落。

| 列 1 | 列 2 |
|-----|-----|
| 数据 1 | 数据 2 |

这是表格后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_skip_quote_blocks(self):
        """测试跳过引用块"""
        content = """这是段落。
> 这是引用内容
> 多行引用
这是引用后的段落。"""
        expected = """这是段落。

> 这是引用内容
> 多行引用
这是引用后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_skip_lists(self):
        """测试列表前后添加空行"""
        content = """这是段落。
- 列表项 1
- 列表项 2
这是列表后的段落。"""
        expected = """这是段落。

- 列表项 1
- 列表项 2
这是列表后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_list_continuation_lines(self):
        """测试列表续行不被拆分"""
        content = """这是段落。
- 列表项 1
  续行内容
- 列表项 2
这是列表后的段落。"""
        expected = """这是段落。

- 列表项 1
  续行内容
- 列表项 2
这是列表后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_nested_list_continuation(self):
        """测试嵌套列表续行不被拆分"""
        content = """开始段落。
- 一级列表
  - 二级列表
    续行内容
- 另一个一级
结束段落。"""
        expected = """开始段落。

- 一级列表
  - 二级列表
    续行内容
- 另一个一级
结束段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_skip_ordered_lists(self):
        """测试有序列表前后添加空行"""
        content = """这是段落。
1. 第一项
2. 第二项
这是列表后的段落。"""
        expected = """这是段落。

1. 第一项
2. 第二项
这是列表后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_skip_task_lists(self):
        """测试任务列表前后添加空行"""
        content = """这是段落。
- [x] 已完成
- [ ] 未完成
这是列表后的段落。"""
        expected = """这是段落。

- [x] 已完成
- [ ] 未完成
这是列表后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_skip_math_blocks(self):
        """测试跳过数学公式块"""
        content = """这是段落。
$$
E = mc^2
$$
这是公式后的段落。"""
        expected = """这是段落。

$$
E = mc^2
$$

这是公式后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_skip_footnotes(self):
        """测试脚注前后添加空行"""
        content = """这是段落 [^1]。

[^1]: 这是脚注内容
     多行脚注
这是脚注后的段落。"""
        expected = """这是段落 [^1]。

[^1]: 这是脚注内容
     多行脚注

这是脚注后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_skip_html_blocks(self):
        """测试 HTML 块前后添加空行"""
        content = """这是段落。
<div class="special">
  HTML 内容
</div>
这是 HTML 后的段落。"""
        expected = """这是段落。

<div class="special">
  HTML 内容
</div>
这是 HTML 后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_skip_frontmatter(self):
        """测试跳过 frontmatter"""
        content = """---
title: 测试
---
这是正文段落。
这是另一个段落。"""
        expected = """---
title: 测试
---

这是正文段落。

这是另一个段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_unclosed_frontmatter_treated_as_content(self):
        """测试未闭合 frontmatter 当作普通内容"""
        content = """---
title: 没有闭合
正文内容。"""
        expected = """---

title: 没有闭合

正文内容。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_complex_mixed_content(self):
        """测试复杂的混合内容"""
        content = """---
title: 测试文档
---
# 标题
这是段落 1。
这是段落 2。

## 列表
- 项目 1
- 项目 2

这是段落 3。
```python
print("代码")
```
这是段落 4。"""
        expected = """---
title: 测试文档
---

# 标题

这是段落 1。

这是段落 2。

## 列表

- 项目 1
- 项目 2

这是段落 3。

```python
print("代码")
```

这是段落 4。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_trim_whitespace_in_regular_lines(self):
        """测试去掉普通行前后的空格"""
        content = """  这是有前导空格的段落。  
这是正常段落。
  这是有前导和尾随空格的段落。  
- 列表项（保持原样）
  这是另一个有空格的行。  """
        expected_lines = [
            "这是有前导空格的段落。",
            "",
            "这是正常段落。",
            "",
            "这是有前导和尾随空格的段落。",
            "",
            "- 列表项（保持原样）",
            "  这是另一个有空格的行。",
        ]
        expected = "\n".join(expected_lines)
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_heading_before_blocks(self):
        """测试标题和下方块之间需要空行"""
        content = """# 标题
- 列表项 1
- 列表项 2

## 另一个标题
> 引用块内容

### 第三个标题
```python
print("代码")
```

#### 第四个标题
| 列 1 | 列 2 |
|-----|-----|
| 数据 1 | 数据 2 |"""
        expected = """# 标题

- 列表项 1
- 列表项 2

## 另一个标题

> 引用块内容

### 第三个标题

```python
print("代码")
```

#### 第四个标题

| 列 1 | 列 2 |
|-----|-----|
| 数据 1 | 数据 2 |"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_user_frontmatter_case(self):
        """测试用户提供的具体案例：frontmatter 内部有空行的情况"""
        # 用户提供的实际内容：frontmatter 内部有空行
        content = """---
title: fmtitle
author: fmauthor
---

# 测试文档

这是一个测试文档，用于演示 pandoc 生成 PDF 的功能。"""

        # 期望输出：应该保持原样，不添加多余的空行
        expected = """---
title: fmtitle
author: fmauthor
---

# 测试文档

这是一个测试文档，用于演示 pandoc 生成 PDF 的功能。"""

        result = pre_add_line_breaks(content, verbose=True)
        print(f"Input:\n{repr(content)}")
        print(f"Expected:\n{repr(expected)}")
        print(f"Result:\n{repr(result)}")

        # 检查是否在 frontmatter 前面添加了空行
        assert not result.startswith("\n"), "frontmatter 前面不应该有空行"
        assert result == expected

    def test_horizontal_rule_in_middle(self):
        """测试文件中间的 --- 应被视为水平线，而非 frontmatter"""
        content = """第一段内容。

---

第二段内容。

---

第三段内容。"""

        # 期望：--- 被当作普通内容，周围添加空行
        expected = """第一段内容。

---

第二段内容。

---

第三段内容。"""

        result = pre_add_line_breaks(content)
        assert result == expected

    def test_horizontal_rule_after_frontmatter(self):
        """测试 frontmatter 后面的 --- 应被视为水平线"""
        content = """---
title: 测试
---
正文开始。

---

这是分隔线后的内容。"""

        expected = """---
title: 测试
---

正文开始。

---

这是分隔线后的内容。"""

        result = pre_add_line_breaks(content)
        assert result == expected

    def test_merged_files_with_separator(self):
        """测试合并文件时的 --- 分隔符不应影响数学公式"""
        # 模拟合并后的内容：第一个文件 + \n\n---\n\n + 第二个文件
        content = """$$| -3\\frac{8}{11} | - | -\\frac{27}{10} | + (-\\frac{9}{11}) - (-3\\frac{4}{5})$$

$$-117 \\times (\\frac{1}{32} - 0.125) \\div (-1.2) \\times (-1\\frac{3}{13})$$

---

$$
\\left(-2.8+3\\dfrac{3}{11}\\right)-\\left(7\\dfrac{1}{2}-6\\dfrac{8}{11}\\right)
$$

$$
-\\frac{1}{42}\\div\\left(\\frac{1}{6}-\\frac{3}{14}-\\frac{2}{3}-\\dfrac{2}{7}\\right)
$$"""

        result = pre_add_line_breaks(content)

        # 验证：所有 $$ 都应该被保留，不应该被破坏
        assert result.count("$$") == content.count("$$"), "数学公式标记应该被完整保留"
        # 验证：数学公式内容应该被保留
        assert "\\dfrac{3}{11}" in result, "数学公式内容应该被保留"
        assert "\\frac{1}{42}" in result, "数学公式内容应该被保留"
        # 验证：--- 应该被保留
        assert "---" in result, "分隔符应该被保留"

    def test_no_frontmatter_only_horizontal_rule(self):
        """测试没有 frontmatter，只有水平线的情况"""
        content = """# 标题

这是内容。

---

这是更多内容。"""

        expected = """# 标题

这是内容。

---

这是更多内容。"""

        result = pre_add_line_breaks(content)
        assert result == expected

    def test_frontmatter_must_be_at_start(self):
        """测试 frontmatter 必须在文件开头（前面只能有空行）"""
        # 前面有空行，应该识别为 frontmatter
        content1 = """

---
title: 测试
---
内容"""
        result1 = pre_add_line_breaks(content1)
        # frontmatter 应该被识别
        assert result1.strip().startswith("---")

        # 前面有非空内容，不应该识别为 frontmatter
        content2 = """一些文本
---
title: 这不是 frontmatter
---
内容"""
        result2 = pre_add_line_breaks(content2)
        # 这些 --- 应该被当作普通内容处理
        lines = result2.split("\n")
        # 检查是否有适当的空行分隔
        assert len([line for line in lines if line.strip() == ""]) >= 2


class TestCodeBlockEmptyLines:
    """测试代码块前后空行处理的边界条件（从 test_code_block_extra_newline.py 合并）"""

    def test_code_block_no_extra_newline_after_start(self):
        """测试代码块开始后不应该有多余的空行"""
        content = """这是普通文本

```typst
= 测试文档

这是内容
```

更多文本"""

        result = pre_add_line_breaks(content)
        lines = result.split("\n")

        # 找到 ```typst 行
        typst_start_idx = None
        for i, line in enumerate(lines):
            if line.strip() == "```typst":
                typst_start_idx = i
                break

        assert typst_start_idx is not None, "应该找到 ```typst 行"

        # 检查 ```typst 后面不应该有空行
        next_line = lines[typst_start_idx + 1]
        assert next_line.strip() != "", f"```typst 后面不应该有空行，但发现：'{next_line}'"

        # 检查下一行应该是代码内容
        assert lines[typst_start_idx + 1] == "= 测试文档", (
            f"下一行应该是代码内容，但发现：'{lines[typst_start_idx + 1]}'"
        )

    def test_multiple_code_blocks_no_extra_newlines(self):
        """测试多个代码块都不应该有多余的空行"""
        content = """文本 1

```typst
代码 1
```

文本 2

```bash
代码 2
```

文本 3"""

        result = pre_add_line_breaks(content)
        lines = result.split("\n")

        # 检查所有代码块开始后都没有空行
        for i, line in enumerate(lines):
            if line.strip().startswith("```") and not line.strip().startswith("````"):
                # 这是代码块开始或结束
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # 如果是代码块开始（带语言标识符），下一行不应该是空行
                    if (
                        line.strip().startswith("```")
                        and not line.strip().endswith("```")
                        and line.strip() != "```"
                    ):
                        # 这是代码块开始（带语言标识符）
                        if next_line.strip() == "":
                            pytest.fail(f"代码块开始 {line} 后面不应该有空行")


class TestCodeBlockProtection:
    """测试代码块隔离功能（合并自 test_code_block_isolation.py 和 test_four_backtick_isolation.py）"""

    # ===== 三反引号代码块隔离测试 =====

    def test_code_block_contains_table_syntax(self):
        """测试代码块内包含表格语法时不被处理为表格"""
        content = """这是段落。
```markdown
| 列 1 | 列 2 |
|-----|-----|
| 数据 1 | 数据 2 |
```
这是代码块后的段落。"""
        expected = """这是段落。

```markdown
| 列 1 | 列 2 |
|-----|-----|
| 数据 1 | 数据 2 |
```

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_code_block_contains_quote_syntax(self):
        """测试代码块内包含引用语法时不被处理为引用块"""
        content = """这是段落。
```text
> 这不是引用块
> 这是代码块内的内容
```
这是代码块后的段落。"""
        expected = """这是段落。

```text
> 这不是引用块
> 这是代码块内的内容
```

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_code_block_contains_list_syntax(self):
        """测试代码块内包含列表语法时不被处理为列表"""
        content = """这是段落。
```markdown
- 这不是列表项
- 这是代码块内的内容
1. 这也不是有序列表
2. 这是代码块内的内容
```
这是代码块后的段落。"""
        expected = """这是段落。

```markdown
- 这不是列表项
- 这是代码块内的内容
1. 这也不是有序列表
2. 这是代码块内的内容
```

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_code_block_contains_math_syntax(self):
        """测试代码块内包含数学公式语法时不被处理为数学块"""
        content = """这是段落。
```text
$$
这不是数学公式块
这是代码块内的内容
$$
```
这是代码块后的段落。"""
        expected = """这是段落。

```text
$$
这不是数学公式块
这是代码块内的内容
$$
```

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_code_block_contains_html_syntax(self):
        """测试代码块内包含 HTML 语法时不被处理为 HTML 块"""
        content = """这是段落。
```html
<div class="test">
这不是 HTML 块
这是代码块内的内容
</div>
```
这是代码块后的段落。"""
        expected = """这是段落。

```html
<div class="test">
这不是 HTML 块
这是代码块内的内容
</div>
```

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_code_block_contains_footnote_syntax(self):
        """测试代码块内包含脚注语法时不被处理为脚注"""
        content = """这是段落。
```text
[^1]: 这不是脚注
这是代码块内的内容
```
这是代码块后的段落。"""
        expected = """这是段落。

```text
[^1]: 这不是脚注
这是代码块内的内容
```

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_code_block_contains_frontmatter_syntax(self):
        """测试代码块内包含 frontmatter 语法时不被处理为 frontmatter"""
        content = """这是段落。
```yaml
---
title: 这不是 frontmatter
author: 这是代码块内的内容
---
```
这是代码块后的段落。"""
        expected = """这是段落。

```yaml
---
title: 这不是 frontmatter
author: 这是代码块内的内容
---
```

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_code_block_preserves_whitespace(self):
        """测试代码块内的空格和缩进被保持原样"""
        content = """这是段落。
```python
    def hello():
        print("Hello")
        if True:
            print("Indented")
```
这是代码块后的段落。"""
        expected = """这是段落。

```python
    def hello():
        print("Hello")
        if True:
            print("Indented")
```

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    # ===== 四反引号代码块隔离测试 =====

    def test_four_backtick_contains_three_backtick(self):
        """测试四个反引号代码块内包含三个反引号时不被处理为代码块"""
        content = """这是段落。
````markdown
```{=typst}
#pagebreak()
```
````
这是代码块后的段落。"""
        expected = """这是段落。

````markdown
```{=typst}
#pagebreak()
```
````

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_four_backtick_contains_mixed_syntax(self):
        """测试四个反引号代码块内包含各种特殊语法时都不被处理"""
        content = """这是段落。
````markdown
# 这不是标题
这是普通文本。

## 这也不是标题
- 这不是列表
- 这是代码块内容

> 这不是引用块
> 这是代码块内容

| 列 1 | 列 2 |
|-----|-----|
| 数据 1 | 数据 2 |

$$
这不是数学公式
$$

<div>
这不是 HTML 块
</div>

[^1]: 这不是脚注

---
title: 这不是 frontmatter
author: 这是代码块内的内容
---

```python
这是嵌套的三个反引号代码块
print("Hello")
```
````
这是代码块后的段落。"""
        expected = """这是段落。

````markdown
# 这不是标题
这是普通文本。

## 这也不是标题
- 这不是列表
- 这是代码块内容

> 这不是引用块
> 这是代码块内容

| 列 1 | 列 2 |
|-----|-----|
| 数据 1 | 数据 2 |

$$
这不是数学公式
$$

<div>
这不是 HTML 块
</div>

[^1]: 这不是脚注

---
title: 这不是 frontmatter
author: 这是代码块内的内容
---

```python
这是嵌套的三个反引号代码块
print("Hello")
```
````

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_four_backtick_with_three_backtick_around(self):
        """测试四个反引号代码块前后有普通三个反引号代码块"""
        content = """这是段落。
```python
这是普通代码块
print("Hello")
```

````markdown
```{=typst}
#pagebreak()
```
````

```javascript
这是另一个普通代码块
console.log("World")
```
这是最后的段落。"""
        expected = """这是段落。

```python
这是普通代码块
print("Hello")
```

````markdown
```{=typst}
#pagebreak()
```
````

```javascript
这是另一个普通代码块
console.log("World")
```

这是最后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected

    def test_four_backtick_priority_over_three_backtick(self):
        """测试四个反引号优先级高于三个反引号"""
        content = """这是段落。
````
这里有三个反引号：```
但不会被处理为代码块结束
````
这是代码块后的段落。"""
        expected = """这是段落。

````
这里有三个反引号：```
但不会被处理为代码块结束
````

这是代码块后的段落。"""
        result = pre_add_line_breaks(content)
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
