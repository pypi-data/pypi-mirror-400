# 预处理步骤优化方案

- **计划内容**：
  - 全局缓存 `MarkdownIt` 实例，避免单文件多次重建。
  - 预编译所有正则表达式（Frontmatter, Link, CodeBlock, Math 等）。
  - 合并 `pre_for_typst` 中的字符转义逻辑：
    - 将 `@` 和 `$` 的转义合并为单次扫描 (`pre_escape_typst_chars`)。
    - 减少 50% 的 `get_protected_regions` 调用开销。

说明：“全局缓存 MarkdownIt 实例”的意思是：

在代码中，_build_markdown_parser() 函数负责创建一个 Markdown 解析器对象（比较重，还需要加载插件）。

优化前： 每次处理图片验证、计算空行或其他需要解析 Markdown 的时候，都会调用这个函数，每次都全新创建一个新的解析器对象。处理 100 个文件可能就创建 100+ 次，非常浪费 CPU。

优化后（使用 @lru_cache）： 第一次调用时创建对象，并把它存下来（缓存）。 后面再调用这个函数时，直接返回之前存好的那个对象，不再重新创建。 这样整个程序运行期间，只创建一次解析器，大大节省了开销。

## 目标描述
优化 `src/mark2pdf/helper_markdown/md_preprocess.py` 以降低 CPU 使用率并减少冗余计算。
当前存在的问题：
1. `MarkdownIt` 解析器被重复实例化。
2. 正则表达式被重复编译。
3. `pre_for_typst` 为了相似的操作（`@` 和 `$` 转义）多次调用 `get_protected_regions`，导致重复扫描。

## 建议变更

### src/mark2pdf/helper_markdown/md_preprocess.py

#### [修改] [md_preprocess.py](file:///Users/fangjun/python/pdfwork/src/mark2pdf/helper_markdown/md_preprocess.py)

1.  **缓存 MarkdownIt 实例**：
    -   导入 `functools.lru_cache`。
    -   使用 `@lru_cache(maxsize=1)` 装饰 `_build_markdown_parser`。

2.  **预编译正则表达式**：
    -   将正则表达式字符串移动到模块级的大写常量中，并使用 `re.compile` 预编译：
        -   `FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)`
        -   `LINK_PATTERN = re.compile(r"(?<!\!) ?\[([^\]]*)\]\(([^)]+)\) ?")`
        -   `IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\([^)]+\)")`
        -   `CODE_PATTERNS`: 包含四反引号、三反引号、行内代码的正则列表
        -   `MATH_PATTERNS`: 包含块级数学、行内数学、LaTeX 风格数学的正则列表
        -   HTML 相关正则：`HTML_START_PATTERN`, `HTML_END_PATTERN` 等

3.  **合并 Typst 转义函数**：
    -   **新增核心函数** `_pre_escape_chars(content: str, chars: set[str]) -> tuple[str, int]`：
        -   计算一次 `protected_regions = get_protected_regions(content)`。
        -   一次性遍历内容字符串：
            -   若当前索引在保护区内，直接跳过。
            -   若当前字符在 `chars` 集合中（如 `@` 或 `$`），且未被转义，则执行转义（插入 `\`）。
    -   **新增统一入口** `pre_escape_typst_chars(content: str) -> str`：
        -   调用 `_pre_escape_chars(content, {'@', '$'})`。
        -   此函数将替代 `pre_for_typst` 中原本顺序调用的 `pre_for_typst_at` 和 `pre_for_typst_dollarmark`，实现一次扫描处理两种字符。
    -   **保留兼容性**：
        -   保留 `pre_for_typst_at` 和 `pre_for_typst_dollarmark` 函数接口，但在内部实现上改为调用 `_pre_escape_chars`，以保持向后兼容（测试代码依赖）。

## 验证计划

### 自动化测试
-   运行现有测试以确保无回归：
    ```bash
    uv run pytest src/mark2pdf/helper_markdown/tests/
    ```
-   特别验证 `test_pre_for_typst.py` 在合并优化后仍通过。
