"""
稿纸专用预处理模块

提供稿纸格式（方格纸）的 Markdown 预处理函数：
- center_with_cnspace: 用中文空格居中文本
- md_pre_process: 清理 frontmatter、移除空格、转换段落格式
- process_for_typ: 稿纸专用排版（标题居中、作者居中、正文段首缩进）
"""

import re


def center_with_cnspace(text: str, linelength: int = 20) -> str:
    """在文本前添加中文空格，使其在指定长度的一行中居中

    参数：
        text: 需要居中的文本
        linelength: 行的总长度（字符数）

    返回：
        添加了中文空格前缀的居中文本
    """
    cnspace = "\u3000"  # '\u3000' 为中文空格
    length = len(text)
    spaces_needed = (linelength - length - 1) // 2
    if spaces_needed > 0 and length <= linelength:
        return cnspace * (spaces_needed + 1) + text
    else:
        return text


def md_pre_process(content: str) -> list[str]:
    """前置处理内容，包括清理 frontmatter、多余换行、转换段落格式等

    处理步骤：
    1. 清除 YAML frontmatter
    2. 移除每行前后的空格
    3. 移除所有英文空格
    4. 移除所有中文空格（稍后统一添加）
    5. 将单换行转为双换行，规范化换行
    6. 将双换行替换为反斜杠+换行（Typst 段落格式）

    参数：
        content: 原始 Markdown 内容

    返回：
        处理后的行列表
    """
    if not content.strip():
        return []

    # - 清除 frontmatter（在 split 之前处理）
    content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)  # re.DOTALL 用来匹配换行符

    # - 移除每行前后的空格
    content = re.sub(r"^[ \t]+|[ \t]+$", "", content, flags=re.MULTILINE)

    # - 移除所有空格（注意这个可能带来的负面影响!）
    content = re.sub(r" ", "", content)

    # - 移除所有中文空格（包括连续的），稍后会统一添加
    content = re.sub(r"\u3000+", "", content)

    # - 将所有单个换行转换为双换行，再将 3 个或更多连续换行转换为 2 个换行
    content = re.sub(r"\n", "\n\n", content)
    content = re.sub(r"\n{3,}", "\n\n", content)

    # - 去除开头和结尾的空行（使用 strip 处理所有空白字符）
    content = content.strip()

    # - 将所有的双换行（段落分隔符）替换为反斜杠 + 换行
    content = re.sub(r"\n\n", "\\\n", content)

    # - 去除开头和结尾的空行（使用 strip 处理所有空白字符）
    lines = content.strip().split("\n")

    return lines


def process_for_typ(content: str) -> str:
    """处理 markdown 内容，按照指定格式处理，便于 Typst 稿纸模板使用

    排版规则：
    1. 第一行（标题）：用中文空格居中
    2. 第二行（作者）：如果少于8个字符则居中，否则添加两个中文空格缩进
    3. 其余行（正文）：添加两个中文空格作为段首缩进

    参数：
        content: 原始 Markdown 内容

    返回：
        处理后适合稿纸模板的文本
    """
    # 前置处理
    result_lines = md_pre_process(content)

    # (A) 处理标题和作者行
    if len(result_lines) >= 1:
        # 第一行是标题，添加中文空格居中
        result_lines[0] = center_with_cnspace(result_lines[0])

    if len(result_lines) >= 2:
        # 第二行是作者，只有少于 8 个字才进行居中处理，否则视为普通行
        maybe_author_line = result_lines[1].strip()
        if len(maybe_author_line) < 8:  # "某某某\"(4)，"作者：某某某\"(7)
            result_lines[1] = center_with_cnspace(maybe_author_line)
        else:
            result_lines[1] = "\u3000\u3000" + maybe_author_line

    # (B) 为所有非空行添加中文空格前缀（除了标题和作者）
    for i, line in enumerate(result_lines):
        if i > 1 and line.strip() != "":
            result_lines[i] = "\u3000\u3000" + line

    return "\n".join(result_lines)
