# /// script
# dependencies = ["click", "PyYAML"]
# ///

DEFAULT_TEMPLATE = "wensi_fe.typ"

import re
import shutil
from pathlib import Path

import click

from helper_markdown import extract_frontmatter
from helper_typst import check_pandoc_typst, run_pandoc_typst
from helper_workingpath import resolve_template_path


def copy_all_content(origin_path: Path, target_dir: Path, verbose: bool = False) -> None:
    """
    复制目录及其所有内容到目标目录

    参数：
        origin_path: 源目录路径
        target_dir: 目标目录
    """
    if not origin_path.exists():
        click.echo(f"错误：源路径不存在：{origin_path}")
        raise click.Abort()

    # 使用 copytree 复制整个目录树
    shutil.copytree(origin_path, target_dir, dirs_exist_ok=True)
    if verbose:
        click.echo(f"复制完成：{origin_path} -> {target_dir}")


def find_index_file(work_dir: Path) -> Path:
    """查找 index.mdx 或 index.md 文件"""
    # 先查找 index.mdx，然后查找 index.md
    for filename in ["index.mdx", "index.md"]:
        index_file = work_dir / filename
        if index_file.exists():
            return index_file
    return None


def create_section_cover(md_file: Path, all_title: str) -> str:
    """
    从 markdown 文件提取 frontmatter 并创建章节封面内容

    参数：
        md_file: markdown 文件路径
        all_title: 总标题

    返回：
        str: 章节封面的 typst 代码，如果没有 section_number 则返回空字符串
    """
    fm = extract_frontmatter(md_file)

    section_title = ""
    section_number = ""
    if "title" in fm and fm["title"]:
        section_title = fm["title"]
    if "section_number" in fm and fm["section_number"]:
        section_number = fm["section_number"]

    if section_number:
        return (
            "\n```{=typst}\n"
            + "#create-section-page("
            # + 'cover :'
            # + '"./images/cover.jpg",'
            + 'modulename: "'
            + all_title
            + '",'
            + 'title: "'
            + section_title
            + '",'
            + 'section_number: "'
            + str(section_number)
            + '"'
            + ")\n```\n"
        )
    return ""


def merge_markdown_files(work_dir: Path, output_file: Path, verbose: bool = False) -> str:
    """
    将所有 markdown 文件合并为一个大的中间文件

    参数：
        work_dir: 工作目录（包含要合并的 markdown 文件）
        output_file: 输出文件路径
        verbose: 是否显示详细信息

    返回：
        str: 从 frontmatter 中提取的 title，用于生成输出文件名
    """
    # 查找所有 markdown 文件
    md_files = list(work_dir.rglob("*.md")) + list(work_dir.rglob("*.mdx"))

    if not md_files:
        click.echo(f"错误：在目录 {work_dir} 中没有找到 markdown 文件")
        raise click.Abort()

    # 按路径排序以确保一致性
    md_files.sort()

    if verbose:
        click.echo(f"找到 {len(md_files)} 个 markdown 文件")

    # 查找索引文件并提取 frontmatter
    index_file = find_index_file(work_dir)
    frontmatter = {}

    if index_file:
        frontmatter = extract_frontmatter(index_file)
        if verbose:
            click.echo(f"从 {index_file.name} 提取了 frontmatter")
            if frontmatter:
                click.echo(f"  Frontmatter 键：{list(frontmatter.keys())}")

    alltitle = ""
    if "title" in frontmatter and frontmatter["title"]:
        alltitle = frontmatter["title"]

    # 构建合并内容
    merged_content = ""

    # 写入 frontmatter（如果有）
    if frontmatter:
        merged_content += "---\n"
        for key, value in frontmatter.items():
            merged_content += f"{key}: {value}\n"
        merged_content += "---\n\n"

    # 从每个文件写入内容
    for md_file in md_files:
        # 跳过索引文件（已处理 frontmatter）
        if md_file.name in ["index.mdx", "index.md"]:
            continue

        if verbose:
            click.echo(f"  添加文件：{md_file.relative_to(work_dir)}")

        with open(md_file, encoding="utf-8") as in_f:
            content = in_f.read()

            # 生成章节封面
            section_cover = create_section_cover(md_file, alltitle)
            if section_cover:
                merged_content += section_cover

            # 如果文件有 frontmatter，只取内容部分
            if content.startswith("---"):
                end_pos = content.find("---", 3)
                if end_pos != -1:
                    content = content[end_pos + 3 :].strip()

            merged_content += content
            merged_content += "\n\n"

    # 写入合并文件
    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write(merged_content)

    if verbose:
        click.echo(f"合并完成：{output_file}")

    # 返回 title 用于生成输出文件名
    return alltitle


def convert_to_pdf(
    merged_file: Path,
    output_dir: Path,
    title: str = "",
    template: str = None,
    verbose: bool = False,
) -> Path:
    """
    使用 helper_typst 将合并的 markdown 文件转换为 PDF

    参数：
        merged_file: 合并的 markdown 文件路径
        output_dir: 输出目录
        title: 文档标题，用于生成输出文件名
        template: 模板文件路径
        verbose: 是否显示详细信息

    返回：
        Path: 生成的 PDF 文件路径
    """
    # 生成输出文件名
    if title:
        # 使用 title 生成文件名，移除特殊字符

        safe_filename = re.sub(r"[^\w\s-]", "", title).strip()
        safe_filename = re.sub(r"[-\s]+", "-", safe_filename)
        pdf_filename = safe_filename + ".pdf"
    else:
        pdf_filename = merged_file.stem + ".pdf"
    pdf_path = output_dir / pdf_filename

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 将模板路径解析为绝对路径
    template_path = resolve_template_path(template)
    # 使用 helper_typst 进行转换
    # 修复说明：
    # 1. input_file 使用相对路径 merged_file.name，因为 pandoc 在 merged_file.parent 目录下执行
    # 2. output_file 使用绝对路径 pdf_path.absolute()，避免 pandoc 工作目录导致的路径解析错误
    # 参考 md2pdf.py 的实现方式，确保 pandoc 能正确找到输入和输出文件
    success = run_pandoc_typst(
        input_file=merged_file.name,  # 只传递文件名，不传递完整路径
        output_file=str(pdf_path.absolute()),  # 使用绝对路径
        template_path=template_path,
        pandoc_workdir=str(merged_file.parent),
        verbose=verbose,
        to_typst=False,
    )

    if success:
        return pdf_path
    else:
        return None


@click.command()
@click.argument("input-dir", type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.option("--output-dir", "-o", default="_working/out", help="Output directory")
@click.option("--template", "-t", default=DEFAULT_TEMPLATE, help="Typst template file path")
@click.option("--savemd", is_flag=True, help="Keep merged intermediate file")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
def cli(
    input_dir: str,
    output_dir: str,
    template: str,
    savemd: bool,
    verbose: bool,
) -> None:
    """
    从输入目录生成 PDF 文档

    工作流程：
    1. 将内容从输入目录复制到_working/in/subdir
    2. 将所有 markdown 文件合并为一个大的中间文件
    3. 使用 helper_typst 转换为 PDF

    使用示例：
    --------
    # 基本用法
    python scripts/make_wensi_fe.py /Users/fangjun/projects/wensi/content/fe/scene

    # 指定输出目录
    python scripts/make_wensi_fe.py /path/to/source --output-dir ./output

    # 使用自定义模板
    python scripts/make_wensi_fe.py /path/to/source --template ./my_template.template

    # 保留合并的中间文件
    python scripts/make_wensi_fe.py /path/to/source --keep-merged

    # 显示详细信息
    python scripts/make_wensi_fe.py /path/to/source --verbose
    """
    try:
        # 检查 pandoc 和 typst 是否已安装
        check_pandoc_typst()

        # 解析路径，构建工作目录路径
        origin_path = Path(input_dir)
        output_dir_path = Path(output_dir)
        work_dir = Path("_working/in") / origin_path.name

        # 任务 1: 将内容复制到工作目录
        if verbose:
            click.echo(f"任务 1: 复制内容到 {work_dir}")
        copy_all_content(origin_path, work_dir, verbose)

        # 任务 2: 合并 markdown 文件
        if verbose:
            click.echo("任务 2: 合并 markdown 文件")
        merged_file = work_dir / "merged.md"
        title = merge_markdown_files(work_dir, merged_file, verbose)

        # 任务 3: 转换为 PDF
        if verbose:
            click.echo("任务 3: 转换为 PDF")
        pdf_path = convert_to_pdf(merged_file, output_dir_path, title, template, verbose)

        if pdf_path:
            click.echo(f"✓ 最终输出：{pdf_path}")
        else:
            click.echo("✗ PDF 转换失败")
            raise click.Abort()

        # 清理中间文件（除非指定保留）
        if not savemd and merged_file.exists():
            merged_file.unlink()
            if verbose:
                click.echo("✓ 清理了中间文件")

            # 清理工作目录
            if work_dir.exists():
                shutil.rmtree(work_dir)
                if verbose:
                    click.echo(f"✓ 清理了工作目录：{work_dir}")

    except Exception as e:
        click.echo(f"程序执行错误：{str(e)}")
        raise click.Abort()


if __name__ == "__main__":
    cli()
