import copy
import re
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path

import yaml
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

# Precompiled Regex Patterns
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)
LINK_PATTERN_REMOVE = re.compile(r"(?<!\!) ?\[([^\]]*)\]\(([^)]+)\) ?")
LINK_PATTERN_PROTECT = re.compile(r"(!?\[([^\]]*)\]\(([^)]+)\))")
IMAGE_PATTERN_PROTECT = re.compile(r"!\[[^\]]*\]\([^)]+\)")

CODE_BLOCK_FOUR_BACKTICKS = re.compile(r"````[\s\S]*?````")
CODE_BLOCK_THREE_BACKTICKS = re.compile(r"```[\s\S]*?```")
CODE_INLINE = re.compile(r"`[^`\n]+`")

MATH_BLOCK = re.compile(r"\$\$[\s\S]*?\$\$")
MATH_INLINE = re.compile(r"(?<!\$)\$(?!\s)(?:[^\n$])*?[^\s$]\$(?!\$)")
MATH_LATEX_INLINE = re.compile(r"\\\([^)]+\\\)")
MATH_LATEX_BLOCK = re.compile(r"\\\[[^\]]+\\\]")

TITLE_STAR_PATTERN = re.compile(r"^#{1,6}\s+")
TITLE_BOLD_CONTENT_PATTERN = re.compile(r"\*\*([^*]+)\*\*")

# List item patterns
LIST_UNORDERED = re.compile(r"^[-*+]\s+")
LIST_ORDERED = re.compile(r"^\d+\.\s+")
LIST_TASK = re.compile(r"^[-*+]\s+\[[ x]\]\s+")

# Heading patterns
HEADING_ATX = re.compile(r"^#{1,6}\s+")
HEADING_SETEXT = re.compile(r"^=+$|^-+$")

FOOTNOTE_PATTERN = re.compile(r"^\[\^[^\]]+\]:")
TABLE_SEPARATOR_PATTERN = re.compile(r"^[:|\-\s]+$")


r"""
Markdown 预处理模块

包含所有以 pre 开头的预处理函数：
- pre_clean_frontmatter: 清理 YAML frontmatter
- pre_image_verify: 验证图片引用
- pre_remove_links: 移除链接（保留图片）
- pre_remove_titlestar: 去掉标题中的加粗标记
- pre_trim_whitespace: 去除每行前后的空格
- pre_add_line_breaks: 添加空行分隔，跳过表格、引用块、代码块
- pre_dash_to_star: 将下划线斜体改为星号加粗
- pre_for_typst_at: 将不在链接 URL 中的 @ 转义为 \@
- pre_for_typst_dollarmark: 将普通文本中的 $ 转义为 \$（不影响数学公式）
- pre_for_typst: 组合多个 Typst 预处理函数

测试脚本：
- test_md_preprocess_line_breaks.py: 测试 pre_add_line_breaks 功能
  使用方法: uv run test_md_preprocess_line_breaks.py --verbose
"""

_FRONTMATTER_CACHE_MAX = 128
_FRONTMATTER_CACHE: OrderedDict[Path, tuple[float, int, dict]] = OrderedDict()


@lru_cache(maxsize=1)
def _build_markdown_parser() -> MarkdownIt:
    md = MarkdownIt("commonmark")
    md.use(dollarmath_plugin)
    return md


def pre_clean_frontmatter(content: str, verbose: bool = False) -> str:
    """预处理：清理 frontmatter"""

    # 匹配 YAML frontmatter: 以---开头和结尾的块
    # 使用 re.DOTALL 让。匹配换行符
    match = FRONTMATTER_PATTERN.match(content)

    if match:
        frontmatter_content = match.group(1)
        if frontmatter_content.strip() == "":
            if verbose:
                print("  - frontmatter 为空，保持原样")
            return content
        # 移除 frontmatter，保留其余内容
        cleaned_content = content[match.end() :]
        if verbose:
            frontmatter_lines = len(frontmatter_content.split("\n"))
            print(f"  - 移除了 {frontmatter_lines} 行 frontmatter")
        return cleaned_content
    else:
        if verbose:
            print("  - 未发现 frontmatter")
        return content


def pre_image_verify(content: str, file_path: str, verbose: bool = False) -> str:
    """预处理：验证图片引用"""

    md = _build_markdown_parser()
    image_urls = []
    for token in md.parse(content):
        if token.type != "inline" or not token.children:
            continue
        for child in token.children:
            if child.type != "image":
                continue
            src = child.attrGet("src")
            if src:
                image_urls.append(src)

    file_dir = Path(file_path).parent
    errors = []

    for image_url in image_urls:
        if image_url.startswith(("http://", "https://")):
            # 网络图片
            errors.append(f"网络图片不支持：{image_url}")
        else:
            # 本地图片
            image_path = file_dir / image_url
            if not image_path.exists():
                errors.append(f"本地图片不存在：{image_url}")

    if errors:
        print("图片验证失败：")
        for error in errors:
            print(f"  ✗ {error}")
        raise ValueError("图片验证失败")

    if verbose:
        print(f"  - 验证了 {len(image_urls)} 个图片引用，全部通过")

    return content


def _find_code_ranges(content: str) -> list[tuple[int, int]]:
    ranges = []
    code_patterns = (
        CODE_BLOCK_FOUR_BACKTICKS,
        CODE_BLOCK_THREE_BACKTICKS,
        CODE_INLINE,
    )
    for pattern in code_patterns:
        for match in pattern.finditer(content):
            ranges.append((match.start(), match.end()))
    return _merge_ranges(ranges)


def _iter_unprotected_segments(content: str, protected_ranges: list[tuple[int, int]]):
    if not protected_ranges:
        yield content
        return
    last = 0
    for start, end in protected_ranges:
        if last < start:
            yield content[last:start]
        last = end
    if last < len(content):
        yield content[last:]


def _apply_to_unprotected(content: str, protected_ranges: list[tuple[int, int]], transform) -> str:
    if not protected_ranges:
        return transform(content)
    parts = []
    last = 0
    for start, end in protected_ranges:
        if last < start:
            parts.append(transform(content[last:start]))
        parts.append(content[start:end])
        last = end
    if last < len(content):
        parts.append(transform(content[last:]))
    return "".join(parts)


def pre_remove_links(content: str, verbose: bool = False) -> str:
    """预处理：移除链接（保留图片）"""

    # 匹配链接语法：[text](url) 但不匹配图片 ![](url)
    # 使用负向前瞻确保不是图片，并匹配可能的前后空格
    
    code_ranges = _find_code_ranges(content)
    matches = []
    for segment in _iter_unprotected_segments(content, code_ranges):
        matches.extend(LINK_PATTERN_REMOVE.findall(segment))

    if matches:
        # 移除链接，保留链接文本
        def replace_link(match):
            link_text = match.group(1)
            # 如果链接文本为空，返回空字符串，否则返回链接文本
            return link_text if link_text else ""

        def remove_links(segment: str) -> str:
            return LINK_PATTERN_REMOVE.sub(replace_link, segment)

        cleaned_content = _apply_to_unprotected(content, code_ranges, remove_links)

        if verbose:
            print(f"  - 移除了 {len(matches)} 个链接")
        return cleaned_content
    else:
        if verbose:
            print("  - 未发现链接")
        return content


def pre_trim_whitespace(content: str, verbose: bool = False) -> str:
    """预处理：去除每行前后的空格"""
    lines = content.split("\n")
    processed_lines = []

    for line in lines:
        # 清除每行前后的空格
        processed_line = line.strip()
        processed_lines.append(processed_line)

    return "\n".join(processed_lines)


def pre_add_line_breaks(content: str, verbose: bool = False) -> str:
    """
    预处理：添加空行分隔，使所有行变成 markdown 有效的行（即空一行）
    但要跳过 table, 多行 > quote, ``` code ```, frontmatter, 列表，HTML 块，脚注，数学公式块

    使用字符串模式匹配识别特殊块，然后在原始内容上添加空行
    """
    result = _add_line_breaks_to_content(content, verbose)

    # if verbose:
    #     print("  - 使用字符串模式匹配添加了空行分隔，跳过了特殊块")

    return result


def _token_protected_ranges(tokens):
    protected = []
    for token in tokens:
        if token.map is None:
            continue
        if token.type in ("fence", "code_block"):
            protected.append((token.map[0], token.map[1]))
        elif token.type in ("bullet_list_open", "ordered_list_open"):
            protected.append((token.map[0], token.map[1]))
        elif token.type == "blockquote_open":
            protected.append((token.map[0], token.map[1]))
        elif token.type == "html_block":
            protected.append((token.map[0], token.map[1]))
        elif token.type == "table_open":
            protected.append((token.map[0], token.map[1]))
        elif token.type == "math_block":
            protected.append((token.map[0], token.map[1]))
    return protected


def _find_frontmatter_range(lines):
    first_non_empty_idx = -1
    for idx, line in enumerate(lines):
        if line.strip() != "":
            first_non_empty_idx = idx
            break

    if first_non_empty_idx == -1:
        return None

    if lines[first_non_empty_idx].strip() != "---":
        return None

    for i in range(first_non_empty_idx + 1, len(lines)):
        if lines[i].strip() == "---":
            return (first_non_empty_idx, i + 1)

    return None


def _merge_ranges(ranges):
    if not ranges:
        return []
    ranges = sorted(ranges, key=lambda item: (item[0], item[1]))
    merged = [list(ranges[0])]
    for start, end in ranges[1:]:
        last = merged[-1]
        if start < last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def _apply_ranges_to_lines(line_count, ranges):
    line_ids = [None] * line_count
    for idx, (start, end) in enumerate(ranges):
        for line_idx in range(start, min(end, line_count)):
            line_ids[line_idx] = idx
    return line_ids


def _find_footnote_ranges(lines, line_ids):
    ranges = []
    i = 0
    while i < len(lines):
        if line_ids[i] is not None:
            i += 1
            continue
        if not FOOTNOTE_PATTERN.match(lines[i].strip()):
            i += 1
            continue
        start = i
        i += 1
        while i < len(lines):
            if lines[i].startswith(("    ", "\t")):
                i += 1
                continue
            if lines[i].strip() == "" and i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.startswith(("    ", "\t")):
                    i += 1
                    continue
            if line_ids[i] is not None:
                break
            break
        ranges.append((start, i))
    return ranges


def _looks_like_table_separator(line):
    stripped = line.strip()
    if "|" not in stripped or "-" not in stripped:
        return False
    return bool(TABLE_SEPARATOR_PATTERN.match(stripped))


def _find_table_ranges(lines, line_ids):
    ranges = []
    i = 0
    while i + 1 < len(lines):
        if line_ids[i] is not None:
            i += 1
            continue
        line = lines[i]
        next_line = lines[i + 1]
        if line.count("|") >= 2 and _looks_like_table_separator(next_line):
            start = i
            i += 2
            while i < len(lines):
                if line_ids[i] is not None:
                    break
                if lines[i].count("|") >= 1:
                    i += 1
                    continue
                break
            ranges.append((start, i))
            continue
        i += 1
    return ranges


def _find_math_block_ranges(lines, line_ids):
    """使用正则表达式识别数学公式块 $$ ... $$，解决解析器在无空行时无法识别的问题"""
    ranges = []
    i = 0
    while i < len(lines):
        if line_ids[i] is not None:
            i += 1
            continue
        stripped = lines[i].strip()
        # 检查是否是独立的 $$ 开始行
        if stripped == "$$":
            start = i
            i += 1
            # 寻找结束的 $$
            while i < len(lines):
                if lines[i].strip() == "$$":
                    i += 1  # 包含结束行
                    break
                i += 1
            ranges.append((start, i))
            continue
        # 检查是否是单行数学块 $$ ... $$
        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            ranges.append((i, i + 1))
        i += 1
    return ranges


def _add_line_breaks_to_content(content, verbose):
    """在原始内容上添加空行，跳过特殊块，最后统一处理多余空行"""
    lines = content.split("\n")
    if not lines:
        return content

    md = _build_markdown_parser()
    tokens = md.parse(content)

    protected_ranges = _token_protected_ranges(tokens)
    frontmatter_range = _find_frontmatter_range(lines)
    if frontmatter_range:
        protected_ranges.append(frontmatter_range)

    protected_ranges = _merge_ranges(protected_ranges)
    line_ids = _apply_ranges_to_lines(len(lines), protected_ranges)

    extra_ranges = []
    extra_ranges.extend(_find_footnote_ranges(lines, line_ids))
    extra_ranges.extend(_find_table_ranges(lines, line_ids))
    extra_ranges.extend(_find_math_block_ranges(lines, line_ids))
    if extra_ranges:
        protected_ranges.extend(extra_ranges)
        protected_ranges = _merge_ranges(protected_ranges)
        line_ids = _apply_ranges_to_lines(len(lines), protected_ranges)

    processed_lines = []
    for idx, line in enumerate(lines):
        if line_ids[idx] is None:
            processed_lines.append(line.strip())
        else:
            processed_lines.append(line)

    blocks = []
    i = 0
    while i < len(lines):
        if line_ids[i] is not None:
            current_id = line_ids[i]
            start = i
            i += 1
            while i < len(lines) and line_ids[i] == current_id:
                i += 1
            blocks.append((start, i))
            continue

        if processed_lines[i].strip() == "":
            start = i
            i += 1
            while i < len(lines) and line_ids[i] is None and processed_lines[i].strip() == "":
                i += 1
            blocks.append((start, i))
            continue

        blocks.append((i, i + 1))
        i += 1

    output_lines = []
    for block_idx, (start, end) in enumerate(blocks):
        if block_idx > 0:
            prev_start, prev_end = blocks[block_idx - 1]
            prev_last = processed_lines[prev_end - 1].strip()
            curr_first = processed_lines[start].strip()
            if prev_last != "" and curr_first != "":
                output_lines.append("")
        output_lines.extend(processed_lines[start:end])

    result = "\n".join(output_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    result = result.strip()

    if verbose:
        print("  - 使用 markdown-it-py 解析并添加空行分隔，跳过特殊块")

    return result


def _parse_frontmatter_from_text(content: str) -> dict:
    match = FRONTMATTER_PATTERN.match(content)

    if not match:
        return {}

    frontmatter_content = match.group(1).strip()
    return yaml.safe_load(frontmatter_content) or {}


def extract_frontmatter(source: Path | str) -> dict:
    """从文件路径或字符串内容提取 frontmatter

    Args:
        source: 可以是 Path 对象（读取文件）或 str（直接解析内容）

    Returns:
        解析后的 frontmatter 字典，如果无 frontmatter 或解析失败则返回空字典
    """
    try:
        if isinstance(source, Path):
            stat = source.stat()
            cache_key = source.resolve()
            cached = _FRONTMATTER_CACHE.get(cache_key)
            if cached and cached[0] == stat.st_mtime and cached[1] == stat.st_size:
                _FRONTMATTER_CACHE.move_to_end(cache_key)
                return copy.deepcopy(cached[2])

            content = source.read_text(encoding="utf-8")
            frontmatter = _parse_frontmatter_from_text(content)
            _FRONTMATTER_CACHE[cache_key] = (stat.st_mtime, stat.st_size, frontmatter)
            _FRONTMATTER_CACHE.move_to_end(cache_key)
            if len(_FRONTMATTER_CACHE) > _FRONTMATTER_CACHE_MAX:
                _FRONTMATTER_CACHE.popitem(last=False)
            return copy.deepcopy(frontmatter)

        content = source
        return _parse_frontmatter_from_text(content)
    except Exception as e:
        source_info = source if isinstance(source, Path) else "<string>"
        print(f"警告：提取 frontmatter 时出错 ({source_info}): {e}")
        return {}


def get_protected_regions(
    content: str, protect_image_alt: bool = False, protect_link_text: bool = True
) -> list[tuple[int, int]]:
    """
    获取需要保护的区域（不应被文本替换处理的区域）
    包括：链接 URL、图片（整体或仅 URL）、代码块、数学公式

    Args:
        content: Markdown 内容
        protect_image_alt: 是否保护图片 alt 文本（即保护整个图片语法），默认为 False（只保护 URL）
        protect_link_text: 是否保护链接文本部分，默认为 True（保护整个链接语法）
    """
    protected_regions = []

    # 1. 找出所有链接/图片 URL 的位置
    # 匹配 [text](url) 或 ![text](url)
    for match in LINK_PATTERN_PROTECT.finditer(content):
        if protect_link_text:
            # 保护整个链接语法（包括文本和URL）
            protected_regions.append((match.start(), match.end()))
        else:
            # 只保护 URL 部分
            url_start = match.start(3)
            url_end = match.end(3)
            protected_regions.append((url_start, url_end))

    # 1.1 额外保护整段图片语法：![alt](url) 整段范围
    if protect_image_alt:
        for im in IMAGE_PATTERN_PROTECT.finditer(content):
            protected_regions.append((im.start(), im.end()))

    # 2. 保护代码块
    # 2.1 四个反引号代码块
    for match in CODE_BLOCK_FOUR_BACKTICKS.finditer(content):
        protected_regions.append((match.start(), match.end()))

    # 2.2 三个反引号代码块
    for match in CODE_BLOCK_THREE_BACKTICKS.finditer(content):
        protected_regions.append((match.start(), match.end()))

    # 2.3 行内代码
    for match in CODE_INLINE.finditer(content):
        protected_regions.append((match.start(), match.end()))

    # 3. 保护数学公式
    # 3.1 块级数学
    for match in MATH_BLOCK.finditer(content):
        protected_regions.append((match.start(), match.end()))

    # 3.2 行内数学
    # 使用严格模式：$ 后不能有空白，结束 $ 前不能有空白，且中间不能包含换行或 $
    for match in MATH_INLINE.finditer(content):
        protected_regions.append((match.start(), match.end()))

    # 3.3 LaTeX 风格
    for match in MATH_LATEX_INLINE.finditer(content):
        protected_regions.append((match.start(), match.end()))
    for match in MATH_LATEX_BLOCK.finditer(content):
        protected_regions.append((match.start(), match.end()))

    # 按位置排序
    protected_regions.sort()

    # 合并重叠区域
    if not protected_regions:
        return []

    merged = [protected_regions[0]]
    for current in protected_regions[1:]:
        last = merged[-1]
        if current[0] < last[1]:  # 重叠
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)

    return merged


def _find_protected_end(index: int, ranges: list[tuple[int, int]]) -> int | None:
    for start, end in ranges:
        if start <= index < end:
            return end
    return None


def _is_escaped(content: str, index: int) -> bool:
    backslash_count = 0
    i = index - 1
    while i >= 0 and content[i] == "\\":
        backslash_count += 1
        i -= 1
    return backslash_count % 2 == 1


def _is_ascii_alnum(char: str) -> bool:
    return ("0" <= char <= "9") or ("A" <= char <= "Z") or ("a" <= char <= "z")


def _is_double_underscore(content: str, index: int) -> bool:
    if content[index] != "_":
        return False
    if index > 0 and content[index - 1] == "_":
        return True
    if index + 1 < len(content) and content[index + 1] == "_":
        return True
    return False


def _is_intraword_underscore(content: str, index: int) -> bool:
    if content[index] != "_":
        return False
    before = content[index - 1] if index > 0 else ""
    after = content[index + 1] if index + 1 < len(content) else ""
    return _is_ascii_alnum(before) and _is_ascii_alnum(after)


def _find_strong_ranges(
    content: str, protected_ranges: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    ranges = []
    stack = []
    i = 0
    while i + 1 < len(content):
        protected_end = _find_protected_end(i, protected_ranges)
        if protected_end is not None:
            i = protected_end
            continue
        if content[i : i + 2] in ("**", "__") and not _is_escaped(content, i):
            marker = content[i : i + 2]
            if stack and stack[-1][0] == marker:
                start = stack.pop()[1]
                ranges.append((start, i + 2))
            else:
                stack.append((marker, i))
            i += 2
            continue
        i += 1
    return _merge_ranges(ranges)


def _is_within_ranges(index: int, ranges: list[tuple[int, int]]) -> bool:
    for start, end in ranges:
        if start < index < end:
            return True
    return False


def _pre_escape_chars(content: str, chars: set[str]) -> str:
    """
    内部辅助函数：转义指定字符，跳过保护区域
    Args:
        content: markdown 内容
        chars: 需要转义的字符集合，如 {'@', '$'}
    """
    # 不保护链接文本，因为需要转义链接文本中的字符
    protected_regions = get_protected_regions(content, protect_link_text=False)
    
    # 优化：如果是单字符集合，可以先快速检查是否存在
    # if len(chars) == 1 and list(chars)[0] not in content:
    #     return content

    result = []
    i = 0
    count = 0
    
    # 将 protected_regions 转为迭代器以便顺序处理
    regions_iter = iter(protected_regions)
    next_region = next(regions_iter, None)

    while i < len(content):
        # 检查是否进入保护区域
        if next_region and i >= next_region[0]:
            # 进入保护区，直接复制整个区域
            end = next_region[1]
            result.append(content[i:end])
            i = end
            next_region = next(regions_iter, None)
            continue

        char = content[i]
        
        if char in chars:
            # 检查是否已转义
            if i > 0 and content[i-1] == "\\":
                result.append(char)
                i += 1
            else:
                result.append("\\" + char)
                i += 1
                count += 1
        else:
            result.append(char)
            i += 1

    return "".join(result)


def pre_escape_typst_chars(content: str, verbose: bool = False) -> str:
    """
    预处理：一次性转义 Typst 特殊字符 (@ 和 $)，跳过保护区域
    替代了原本分开调用的 pre_for_typst_at 和 pre_for_typst_dollarmark
    """
    return _pre_escape_chars(content, {'@', '$'})


def pre_for_typst_at(content: str, verbose: bool = False) -> str:
    r"""
    预处理：将不在链接 URL 中的 @ 转义为 \@
    保留此函数以兼容测试代码，内部改为调用 _pre_escape_chars
    """
    result = _pre_escape_chars(content, {'@'})
    if verbose and result != content:
         # 简单统计（不精确，仅用于保持 verbose 行为兼容，或者干脆简化打印）
         count = result.count(r"\@") - content.count(r"\@")
         if count > 0:
             print(f"  - 转义了 {count} 个 @ 符号（保留了链接 URL 和代码块中的 @）")
    return result


def pre_for_typst_dollarmark(content: str, verbose: bool = False) -> str:
    r"""
    预处理：将普通文本中的 $ 转义为 \$，但不影响数学公式
    保留此函数以兼容测试代码，内部改为调用 _pre_escape_chars
    """
    result = _pre_escape_chars(content, {'$'})
    if verbose and result != content:
        count = result.count(r"\$") - content.count(r"\$")
        if count > 0:
            print(f"  - 转义了 {count} 个 $ 符号（保留了数学公式和代码块中的 $）")
    return result


def pre_dash_to_star(content: str, verbose: bool = False) -> str:
    """
    预处理：将下划线斜体改为星号加粗

    - 将 _content_ 改为 **content**
    - 但如果 _content_ 已经在 **...** 内部，则只去掉 _，不添加新的 **
    - 不影响链接 URL 中的下划线
    - 不影响行内代码中的下划线
    - 不影响代码块中的下划线
    """
    # 使用共享的保护区域逻辑，并启用图片 alt 保护
    protected_regions = get_protected_regions(content, protect_image_alt=True)
    strong_ranges = _find_strong_ranges(content, protected_regions)

    # 找出所有的 _..._ 并处理（不在保护区域内的）
    # 使用状态机逐字符处理
    result = []
    i = 0
    count = 0

    while i < len(content):
        protected_end = _find_protected_end(i, protected_regions)
        if protected_end is not None:
            result.append(content[i:protected_end])
            i = protected_end
            continue

        if content[i] != "_":
            result.append(content[i])
            i += 1
            continue

        if (
            _is_escaped(content, i)
            or _is_double_underscore(content, i)
            or _is_intraword_underscore(content, i)
        ):
            result.append(content[i])
            i += 1
            continue

        j = i + 1
        found_end = False
        while j < len(content):
            protected_end = _find_protected_end(j, protected_regions)
            if protected_end is not None:
                j = protected_end
                continue

            if content[j] == "\n":
                break

            if content[j] == "_":
                if (
                    _is_escaped(content, j)
                    or _is_double_underscore(content, j)
                    or _is_intraword_underscore(content, j)
                ):
                    j += 1
                    continue

                italic_content = content[i + 1 : j]
                if _is_within_ranges(i, strong_ranges):
                    result.append(italic_content)
                else:
                    result.append("**")
                    result.append(italic_content)
                    result.append("**")
                i = j + 1
                found_end = True
                count += 1
                break

            j += 1

        if not found_end:
            result.append(content[i])
            i += 1

    final_result = "".join(result)

    if verbose and count > 0:
        print(f"  - 转换了 {count} 个下划线斜体为星号加粗")

    return final_result


def pre_remove_titlestar(content: str, verbose: bool = False) -> str:
    r"""
    预处理：去掉标题中的加粗标记

    - 将 ## **Premise** 改为 ## Premise
    - 将 ###### **Revenue Mechanics:** 改为 ###### Revenue Mechanics:
    - 只处理标题行，不影响普通文本中的加粗
    """
    # 使用正则表达式匹配标题行并去掉加粗
    # 匹配：行首 + # 号 + 空格，然后去掉该行中的所有 **...**
    # 支持文件开头的标题（没有前导 \n）

    # 方法：逐行处理
    lines = content.split("\n")
    processed_lines = []
    count = 0

    for line in lines:
        # 检查是否是标题行（以 # 开头）
        stripped = line.strip()
        if TITLE_STAR_PATTERN.match(stripped):
            # 是标题行，去掉所有加粗标记
            original_line = line
            # 去掉 **...**
            line = TITLE_BOLD_CONTENT_PATTERN.sub(r"\1", line)
            if line != original_line and verbose:
                count += 1

        processed_lines.append(line)

    result = "\n".join(processed_lines)

    if verbose and count > 0:
        print(f"  - 去掉了 {count} 个标题中的加粗标记")

    return result


def pre_for_typst(content: str, verbose: bool = False) -> str:
    """
    预处理：组合多个 Typst 预处理函数
    为 Typst 格式准备 Markdown 内容

    - 去掉标题中的加粗标记
    - 将下划线斜体改为星号加粗
    - 转义不在链接 URL 中的 @
    - 转义不在数学公式中的 $
    """
    if verbose:
        print("  - 应用 Typst 预处理（标题加粗去除、斜体转加粗、@、$ 转义）")

    # 先处理标题加粗
    content = pre_remove_titlestar(content, verbose=False)

    # 再处理下划线斜体转星号加粗
    content = pre_dash_to_star(content, verbose=False)

    # 再处理 @ 和 $
    # content = pre_for_typst_at(content, verbose=False)
    # content = pre_for_typst_dollarmark(content, verbose=False)
    # 优化：合并 @ 和 $ 处理
    content = pre_escape_typst_chars(content, verbose=False)

    return content
