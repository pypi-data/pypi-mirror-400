# /// script
# dependencies = ["click","pyyaml"]
# ///

import re
from pathlib import Path

import click

from helper_markdown.md_preprocess import get_protected_regions


def remove_image_wrapper_link(content: str) -> str:
    """
    去掉图片的外链，并将 name=medium 改为 name=large

    处理模式：
    [

    ![Image](url)



    ](link)

    变成：
    ![Image](url_with_name=large)
    """
    # 匹配 [ 开头，中间有图片，](link) 结尾的模式
    # 使用更灵活的正则，允许任意数量的空白和换行
    pattern = r"\[\s*\n\s*!\[([^\]]*)\]\(([^\)]+)\)\s*\n\s*\]\([^\)]+\)"

    def replace_image(match):
        alt_text = match.group(1)
        img_url = match.group(2)

        # 将 name=medium 改为 name=large
        if "name=medium" in img_url:
            img_url = img_url.replace("name=medium", "name=large")
        elif "name=" in img_url:
            # 如果已经有 name 参数但不是 medium，也替换为 large
            img_url = re.sub(r"name=[^&]+", "name=large", img_url)
        else:
            # 如果没有 name 参数，添加 name=large
            if "?" in img_url:
                img_url = f"{img_url}&name=large"
            else:
                img_url = f"{img_url}?name=large"

        return f"![{alt_text}]({img_url})"

    cleaned = re.sub(pattern, replace_image, content, flags=re.MULTILINE)
    return cleaned


def fix_link_line_breaks(content: str) -> str:
    """
    修复链接前后的错误换行

    处理模式：
    After

    [@StreamDefi](link)

    disclosed

    变成：
    After [@StreamDefi](link) disclosed

    也处理：
    [@elixir](link)

    's synthetic dollar pair

    变成：
    [@elixir](link) 's synthetic dollar pair

    以及列表项中的：
    -   [@StablesLabs](link)

        USDX...

    变成：
    -   [@StablesLabs](link) USDX...
    """
    # 多次应用模式，直到没有更多的匹配
    cleaned = content
    max_iterations = 10
    for _ in range(max_iterations):
        prev_content = cleaned

        # 先处理链接前面有文本的情况（包括缩进的情况）
        # 匹配模式：非空白字符 + 至少一个换行 + 可选空白 + [...]](link) + 至少一个换行 + 可选空白 + 非空白字符
        pattern_before = r"(\S+)\s*\n+\s*(\[[^\]]+\]\([^\)]+\))\s*\n+\s*(\S[^\n]*)"

        def replace_link_before(match):
            before = match.group(1)
            link = match.group(2)
            after = match.group(3).strip()

            # 如果后面是列表项标记、标题或另一个链接，不处理
            if (
                after.startswith("-")
                or after.startswith("*")
                or after.startswith("#")
                or after.startswith("[")
            ):
                return match.group(0)

            return f"{before} {link} {after}"

        cleaned = re.sub(pattern_before, replace_link_before, cleaned, flags=re.MULTILINE)

        # 再处理链接后面跟着换行和文本的情况（不管前面是什么）
        # 匹配模式：[...](link) + 至少一个换行 + 空白 + 非空白字符开头的文本
        pattern_after = r"(\[[^\]]+\]\([^\)]+\))\s*\n+\s+(\S[^\n]*)"

        def replace_link_after(match):
            link = match.group(1)
            after = match.group(2).strip()

            # 如果后面是列表项标记、标题或另一个链接，不处理
            if (
                after.startswith("-")
                or after.startswith("*")
                or after.startswith("#")
                or after.startswith("[")
            ):
                return match.group(0)

            return f"{link} {after}"

        cleaned = re.sub(pattern_after, replace_link_after, cleaned, flags=re.MULTILINE)

        # 如果内容没有变化，停止迭代
        if cleaned == prev_content:
            break

    return cleaned


def fix_username_line_breaks(content: str) -> str:
    """
    修复 @username 前后的错误换行

    极度简化：所有 @username 前后的换行都去掉
    但要跳过保护区域（代码块、链接 URL 等）
    """

    # 获取保护区域
    protected_regions = get_protected_regions(content)

    # 辅助函数：检查位置是否在保护区域内
    def is_protected(pos):
        for start, end in protected_regions:
            if start <= pos < end:
                return True
        return False

    cleaned = content
    max_iterations = 10
    for _ in range(max_iterations):
        prev_content = cleaned

        # 去掉 @username 前面的换行：非空白字符 + 换行 + @username -> 非空白字符 + 空格 + @username
        pattern1 = r"(\S)(\s*\n+\s*)(@\w+)"

        def replace_before(match):
            # 检查匹配位置是否在保护区域内
            if is_protected(match.start(2)) or is_protected(match.start(3)):
                return match.group(0)

            before = match.group(1)
            username = match.group(3)
            # 如果前面是逗号或冒号，后面加空格
            if before in ",:":
                return f"{before} {username}"
            # 如果是其他非空格字符，也加空格
            elif before not in " \t.;!?)]}":
                return f"{before} {username}"
            return f"{before}{username}"

        cleaned = re.sub(pattern1, replace_before, cleaned, flags=re.MULTILINE)

        # 去掉 @username 后面的换行：@username + 换行 + 非空白字符 -> @username + 空格 + 非空白字符
        pattern2 = r"(@\w+)(\s*\n+\s*)(\S)"

        def replace_after(match):
            # 检查匹配位置是否在保护区域内
            if is_protected(match.start(1)) or is_protected(match.start(2)):
                return match.group(0)

            username = match.group(1)
            after = match.group(3)
            # 如果后面是逗号，不加空格（逗号前不应该有空格）
            if after == ",":
                return f"{username}{after}"
            # 如果是其他非标点符号，加空格
            elif after not in ".;:!?)]}":
                return f"{username} {after}"
            return f"{username}{after}"

        cleaned = re.sub(pattern2, replace_after, cleaned, flags=re.MULTILINE)

        # 如果内容没有变化，停止迭代
        if cleaned == prev_content:
            break

    return cleaned


def fix_heading_spaces(content: str) -> str:
    """
    修复小标题错误，去掉 ## 后面的多余换行和空格

    处理模式：
    ##

    A Chain of Failures

    变成：
    ## A Chain of Failures
    """
    # 匹配 ## 后面有换行和空格的情况，匹配到下一行非空内容
    pattern = r"(##+)\s+\n+\s*\n+\s*([^\n]+)"

    def replace_heading(match):
        hashes = match.group(1)
        text = match.group(2).strip()
        return f"{hashes} {text}"

    cleaned = re.sub(pattern, replace_heading, content, flags=re.MULTILINE)

    return cleaned


@click.command()
@click.argument("input_path_arg")
@click.option("--samefile", is_flag=True, help="直接保存到原始文件")
def main(input_path_arg, samefile):
    """
    清理 Markdown 文件中的 X (Twitter) 相关格式问题

    INPUT_PATH_ARG: 要处理的 Markdown 文件路径

    清理功能：
    1. 去掉图片的外链，并将 name=medium 改为 name=large
    2. 修复 [@...](link) 链接前后的错误换行
    3. 修复 @username 前后的错误换行
    4. 修复小标题错误，去掉 ## 后面的多余换行和空格
    """
    # 如果输入路径不包含目录分隔符，尝试在 _working/in/ 下查找
    if "/" not in input_path_arg and "\\" not in input_path_arg:
        project_root = Path.cwd()
        working_in_path = project_root / "_working" / "in" / input_path_arg
        if working_in_path.exists():
            input_path = working_in_path.resolve()
            click.echo(f"📂 自动使用路径：{input_path}")
        else:
            # 尝试原始路径
            input_path = Path(input_path_arg).resolve()
    else:
        input_path = Path(input_path_arg).resolve()

    # 检查路径是否存在
    if not input_path.exists():
        raise click.BadParameter(f"Path '{input_path}' does not exist.")

    click.echo(f"📖 正在读取：{input_path.name}")
    with open(input_path, encoding="utf-8") as f:
        content = f.read()

    click.echo("\n🧹 步骤 1: 去掉图片的外链，并将 name=medium 改为 name=large...")
    content = remove_image_wrapper_link(content)

    click.echo("🧹 步骤 2: 修复 [@...](link) 链接前后的错误换行...")
    content = fix_link_line_breaks(content)

    click.echo("🧹 步骤 3: 修复 @username 前后的错误换行...")
    content = fix_username_line_breaks(content)

    click.echo("🧹 步骤 4: 修复小标题错误...")
    content = fix_heading_spaces(content)

    # 根据 samefile 选项决定输出路径
    if samefile:
        output_path = input_path
    else:
        input_dir = input_path.parent
        base_name = input_path.stem
        output_filename = f"{base_name}_cleaned.md"
        output_path = input_dir / output_filename

    click.echo("\n💾 保存处理后的文件...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    click.echo(f"\n✅ 完成！文件已保存：{output_path}")


if __name__ == "__main__":
    main()
