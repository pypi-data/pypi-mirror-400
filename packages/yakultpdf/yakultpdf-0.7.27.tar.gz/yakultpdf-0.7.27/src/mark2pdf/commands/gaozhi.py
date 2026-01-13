"""
mark2pdf 稿纸模式命令

提供专门的稿纸格式转换功能。
"""

import sys
from pathlib import Path

import click

from mark2pdf.core import ConversionOptions
from mark2pdf.core.core import convert_file
from mark2pdf.core.utils import open_with_system
from mark2pdf.helper_gaozhi import process_for_typ

from ..config import ConfigManager


def convert_single_file(
    filename: str,
    verbose: bool = False,
    open_file: bool = False,
    indir: str | Path | None = None,
    outdir: str | Path | None = None,
) -> Path | None:
    """转换单个 md 文件为稿纸格式 PDF"""
    options = ConversionOptions(
        template="gaozhi.typ",
        overwrite=True,  # 目录模式下覆盖，避免时间戳
        verbose=verbose,
    )

    result = convert_file(
        input_file=filename,
        options=options,
        indir=indir,
        outdir=outdir,
        postprocess=process_for_typ,
    )

    if result and open_file:
        open_with_system(result, verbose=verbose)

    return result


def convert_directory(
    directory: str,
    output_name: str | None = None,
    verbose: bool = False,
    open_file: bool = False,
    indir: str | Path | None = None,
    outdir: str | Path | None = None,
) -> bool:
    """批量处理目录中所有 md 文件，逐个转换后合并为一个 PDF"""
    try:
        import fitz  # pymupdf
    except ImportError:
        click.echo("错误：需要安装 pymupdf。请运行：uv pip install pymupdf")
        return False

    indir_path = Path(indir) if indir is not None else Path.cwd()
    outdir_path = Path(outdir) if outdir is not None else Path.cwd()
    input_path = indir_path / directory
    if not input_path.exists():
        click.echo(f"错误：目录 {input_path} 不存在")
        return False

    # 查找所有 md 文件（排序），排除 index.md
    md_files = [f for f in sorted(input_path.glob("*.md")) if f.name != "index.md"]
    if not md_files:
        click.echo(f"错误：在目录 {input_path} 中没有找到 md 文件（排除 index.md）")
        return False

    if verbose:
        click.echo(f"找到 {len(md_files)} 个 md 文件")

    # 使用子目录作为输出目录
    sub_indir = indir_path / directory
    sub_outdir = outdir_path / directory

    # 确保输出目录存在
    sub_outdir.mkdir(parents=True, exist_ok=True)

    # 逐个转换
    pdf_files = []
    for md_file in md_files:
        if verbose:
            click.echo(f"处理：{md_file.name}")

        result = convert_single_file(
            filename=md_file.name,
            verbose=verbose,
            open_file=False,  # 单个文件不打开
            indir=sub_indir,
            outdir=sub_outdir,
        )

        if result:
            pdf_files.append(result)
        else:
            click.echo(f"警告：转换 {md_file.name} 失败")

    if not pdf_files:
        click.echo("错误：没有成功生成任何 PDF 文件")
        return False

    # 合并 PDF
    if directory == ".":
        # 如果是当前目录，尝试使用配置中的 project.name 或目录名
        default_name = "gaozhi_merged"
        final_output_name = output_name or default_name
    else:
        final_output_name = output_name or f"{directory}_gaozhi"

    merged_path = outdir_path / f"{final_output_name}.pdf"

    if verbose:
        click.echo(f"正在合并 {len(pdf_files)} 个 PDF 文件...")

    merged_doc = fitz.open()
    for pdf_file in pdf_files:
        if pdf_file.exists():
            doc = fitz.open(str(pdf_file))
            merged_doc.insert_pdf(doc)
            doc.close()
            if verbose:
                click.echo(f"  已添加：{pdf_file.name}")

    merged_doc.save(str(merged_path))
    merged_doc.close()

    click.echo(f"⚡️ 合并完成：{merged_path}")

    if open_file:
        open_with_system(merged_path, verbose=verbose)

    return True


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("filename", required=False, default=None)
@click.option(
    "--dir", "-d", "directory", default=None, help="目录模式：逐个处理目录中所有 md 文件后合并"
)
@click.option("--output", default=None, help="输出文件名（目录模式下使用，不含扩展名）")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
@click.option("--open", "-o", "open_file", is_flag=True, help="转换完成后打开文件")
def gaozhi(
    filename: str | None,
    directory: str | None,
    output: str | None,
    verbose: bool,
    open_file: bool,
):
    """Gaozhi 稿纸排版转换器

    支持单文件和目录两种模式。目录模式会逐个转换后合并 PDF。
    """
    # 加载配置
    config = ConfigManager.load()
    input_dir = config.input_dir
    output_dir = config.output_dir

    if directory:
        # 目录模式
        success = convert_directory(
            directory=directory,
            output_name=output,
            verbose=verbose,
            open_file=open_file,
            indir=input_dir,
            outdir=output_dir,
        )
        if not success:
            sys.exit(1)
    elif filename:
        # 单文件模式
        options = ConversionOptions(
            template="gaozhi.typ",
            overwrite=False,  # 单文件模式不覆盖
            verbose=verbose,
        )

        result = convert_file(
            input_file=filename,
            options=options,
            indir=input_dir,
            outdir=output_dir,
            postprocess=process_for_typ,
        )

        if result and open_file:
            open_with_system(result, verbose=verbose)

        if not result:
            sys.exit(1)
    else:
        click.echo("错误：请提供文件名或使用 --dir 指定目录")
        click.echo("使用 -h 查看帮助")
        sys.exit(1)
