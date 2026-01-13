# /// script
# dependencies = [ "click","PyYaml"]
# ///

############################################################################
#  功能说明：
#    -  批量处理 _working/in/notes 目录下的所有 md 文件
#       -  从 index.mdx 或 index.md 中提取 frontmatter
#       -  按文件名排序合并所有 md 文件
#    -  使用 helper_typst 将合并后的文件转换为 PDF
#       -  使用 template/letter-personal-notes.typ 模板
#       -  输出结果保存在 _working/out 中
############################################################################

# Typst 模板会处理如下 frontmatter，形成封面
# ---
# title: Typst Notes
# author: Author name
# date: 2025-09-27
# version: v0.0.2
# ---
# ========================================

OUTPUT_DIR = "./_working/out/"
INPUT_BASE = "./_working/in/"
TEMPLATE = "./template/letter-personal-notes.typ"
TEMPLATE_BIGFONT = "./template/letter-personal-notes-bigfont.typ"


import re
from pathlib import Path

import click
import yaml

from helper_interfile import *
from helper_markdown import *
from helper_typst.helper_typst import *


def get_note_dir(notedir: str) -> Path:
    """根据目录名构建输入目录路径"""
    return Path(f"{INPUT_BASE}{notedir}")


def find_index_file(notedir: str) -> Path:
    """查找 index.mdx 或 index.md 文件"""
    inpath = get_note_dir(notedir)

    # 优先查找 index.mdx，然后 index.md
    for filename in ["index.mdx", "index.md"]:
        index_file = inpath / filename
        if index_file.exists():
            return index_file

    return None


def get_frontmatter(notedir: str, verbose: bool = False) -> tuple[dict, str]:
    """从 index 文件中提取返回 frontmatter 和输出文件名"""
    index_file = find_index_file(notedir)

    if not index_file:
        click.echo("错误：未找到 index.mdx 或 index.md 文件", err=True)
        raise click.Abort()

    frontmatter = extract_frontmatter(index_file)
    if verbose and frontmatter:
        click.echo(f"提取到 frontmatter: {list(frontmatter.keys())}")

    # 生成输出文件名：title + version
    title = frontmatter.get("title", "Notes")
    version = frontmatter.get("version", "v1.0")

    # 清理文件名中的特殊字符
    safe_title = re.sub(r"[^\w\s-]", "", title).strip()
    safe_title = re.sub(r"[-\s]+", "-", safe_title)

    # 使用绝对路径，确保无论 workdir 在哪里都能正确保存
    output_dir = Path.cwd() / OUTPUT_DIR.lstrip("./")
    output_filename = str(output_dir / f"{safe_title}-{version}.pdf")

    return frontmatter, output_filename


def find_md_files(notedir: str) -> list[Path]:
    """在指定目录中查找所有 md 文件（排除 index 文件）"""
    inpath = get_note_dir(notedir)
    if not inpath.exists():
        click.echo(f"错误：目录 {inpath} 不存在", err=True)
        raise click.Abort()

    md_files = list(inpath.glob("*.md")) + list(inpath.glob("*.mdx"))
    md_files = [f for f in md_files if f.stem not in ["index"]]

    if not md_files:
        click.echo(f"错误：在目录 {inpath} 中没有找到 md 文件", err=True)
        raise click.Abort()

    return sorted(md_files)


def create_merged_md(
    notedir: str,
    frontmatter: dict,
    verbose: bool = False,
    no_preprocess: bool = False,
) -> str:
    """创建合并后的 markdown 文件，返回临时文件路径"""

    # 查找所有 md 文件
    md_files = find_md_files(notedir)
    if verbose:
        click.echo(f"找到 {len(md_files)} 个 md 文件")

    # 创建一个参考文件用于确定临时文件位置（在 notedir 目录下）
    notedir_path = get_note_dir(notedir)
    reference_file = str(notedir_path / "reference.md")
    temp_fd, temp_path = create_md_tmpfile(
        reference_file, prefix=f"{notedir}_merged_", verbose=verbose
    )

    # 构建合并内容
    merged_content = ""

    # 写入 frontmatter（使用 yaml.dump 确保格式正确）
    if frontmatter:
        merged_content += "---\n"
        # 使用 yaml.dump 正确格式化 frontmatter
        yaml_content = yaml.dump(
            frontmatter,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
        merged_content += yaml_content
        merged_content += "---\n\n"

    # 写入各个文件的内容
    for md_file in md_files:
        if verbose:
            click.echo(f"  添加文件：{md_file.name}")

        with open(md_file, encoding="utf-8") as in_f:
            content = in_f.read()

            # 如果文件有 frontmatter，只取内容部分
            if content.startswith("---"):
                end_pos = content.find("---", 3)
                if end_pos != -1:
                    content = content[end_pos + 3 :].strip()

            merged_content += content
            merged_content += "\n\n"

    # 如果没有禁用预处理，对合并后的内容进行预处理
    if not no_preprocess:
        merged_content = pre_add_line_breaks(merged_content, verbose)
        merged_content = pre_for_typst(merged_content, verbose)

    # 将内容写入临时文件
    write_to_tmpfile(temp_fd, merged_content, verbose=verbose)

    return temp_path


@click.command()
@click.argument("notedir", default="notes")
@click.option("--savemd", is_flag=True, help="保留临时合并文件")
@click.option("--no-preprocess", is_flag=True, help="禁用预处理功能（默认启用）")
@click.option("--bigfont", is_flag=True, help="使用大字体模板")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
def cli(
    notedir: str,
    savemd: bool,
    no_preprocess: bool,
    bigfont: bool,
    verbose: bool,
) -> None:
    check_pandoc_typst()

    # 选择模板
    template = TEMPLATE_BIGFONT if bigfont else TEMPLATE

    # 创建合并的 md
    if verbose:
        click.echo(f"开始批量处理 {notedir} 目录")
    frontmatter, output_filename = get_frontmatter(notedir, verbose)
    merged = create_merged_md(notedir, frontmatter, verbose, no_preprocess)

    # 转换为 PDF
    notedir_path = get_note_dir(notedir)
    try:
        run_pandoc_typst(
            input_file=merged,
            output_file=output_filename,
            template_path=template,
            pandoc_workdir=str(notedir_path),
            verbose=verbose,
        )
        if not savemd:
            cleanup_tmpfile(merged, verbose=verbose)
    except Exception as e:
        if not savemd:
            cleanup_tmpfile(merged, verbose=verbose)
        click.echo(f"错误：调用 Typst 转换时出错：{e}")


if __name__ == "__main__":
    cli()
