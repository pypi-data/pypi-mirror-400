"""
Overview 编译处理器

将 React/MDX 风格的 `<div className="overview">` 转换为 Pandoc fence div 语法 `:::{#overview}`。
仅处理 overview 类，忽略其他 div。
"""

import re

# 仅匹配 className="overview" 或 className='overview'，允许前后有其他属性
OVERVIEW_OPEN_RE = re.compile(r'<div\b[^>]*\bclassName=["\']overview["\'][^>]*>')
# 匹配任意 div 开标签
ANY_DIV_OPEN_RE = re.compile(r"<div\b[^>]*>")
# 匹配 div 闭标签
DIV_CLOSE_RE = re.compile(r"</div>")


def process(content: str) -> str:
    """
    转换 overview div 标签为 Typst fence div

    采用简单的栈机制来处理嵌套 div：
    - 遇到 <div className="overview"> -> 替换为 :::{#overview}，入栈 "overview"
    - 遇到其他 <div ...> -> 保持原样，入栈 "other"
    - 遇到 </div> -> 出栈
      - 若栈顶是 "overview" -> 替换为 :::
      - 若栈顶是 "other" -> 保持 </div>
      - 若栈空 -> 保持 </div>

    Args:
        content: Markdown 内容

    Returns:
        转换后的内容
    """

    # 查找所有相关标签的位置
    # 我们需要合并所有三种正则的匹配结果，按位置排序
    matches = []

    for m in ANY_DIV_OPEN_RE.finditer(content):
        # 区分是否是 overview
        is_overview = bool(OVERVIEW_OPEN_RE.match(m.group()))
        matches.append(
            (m.start(), m.end(), "OPEN", "overview" if is_overview else "other", m.group())
        )

    for m in DIV_CLOSE_RE.finditer(content):
        matches.append((m.start(), m.end(), "CLOSE", None, m.group()))

    # 按起始位置排序
    matches.sort(key=lambda x: x[0])

    if not matches:
        return content

    # 构建新内容
    new_content = []
    last_pos = 0
    stack = []

    for start, end, tag_type, div_type, original_text in matches:
        # 添加此标签之前的内容
        new_content.append(content[last_pos:start])

        if tag_type == "OPEN":
            stack.append(div_type)
            if div_type == "overview":
                new_content.append(":::{#overview}")
            else:
                new_content.append(original_text)
        elif tag_type == "CLOSE":
            if stack:
                top = stack.pop()
                if top == "overview":
                    new_content.append(":::")
                else:
                    new_content.append(original_text)
            else:
                # 栈空，保留原样（可能是孤立的闭标签）
                new_content.append(original_text)

        last_pos = end

    # 添加剩余内容
    new_content.append(content[last_pos:])

    return "".join(new_content)
