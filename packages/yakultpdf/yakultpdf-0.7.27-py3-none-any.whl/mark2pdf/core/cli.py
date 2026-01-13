"""
mark2pdf.core CLI 入口

使用 Click 解析命令行参数，调用 core.py 中的转换函数。
"""

import click

from .core import convert_file
from .defaults import DEFAULT_TEMPLATE, get_build_defaults, get_default_dirs
from .directory import convert_directory
from .options import ConversionOptions
from .utils import open_with_system


@click.command()
@click.argument("mdfilename", default="")
@click.option("--dir", "directory", help="处理整个目录，合并所有 markdown 文件")
@click.option("--template", default=DEFAULT_TEMPLATE, help="typst 模板文件")
@click.option("--coverimg", help="封面图片")
@click.option("--to-typst", is_flag=True, help="输出 typst 文件")
@click.option("--output", help="自定义输出文件名（不含路径，会自动添加.pdf 或.typ 扩展名）")
@click.option("--savemd", is_flag=True, help="保留预处理后的中间 Markdown 文件")
@click.option("--removelink", is_flag=True, help="移除链接（保留图片）")
@click.option("--tc", is_flag=True, help="将简体中文转换为繁体中文")
@click.option("--verbose", is_flag=True, help="显示详细的复制和清除操作信息")
@click.option("--indir", default=None, help="输入目录（默认从配置读取）")
@click.option("--outdir", default=None, help="输出目录（默认从配置读取）")
@click.option("--overwrite", is_flag=True, help="允许覆盖旧文件（不添加时间戳）")
@click.option("--open", "-o", "open_file", is_flag=True, help="转换完成后打开文件")
def cli(
    mdfilename: str,
    directory: str,
    template: str,
    coverimg: str,
    to_typst: bool,
    output: str,
    savemd: bool,
    removelink: bool,
    tc: bool,
    verbose: bool,
    indir: str | None,
    outdir: str | None,
    overwrite: bool,
    open_file: bool,
) -> None:
    """
    将 Markdown 文件转换为 PDF

    使用方式（推荐）：
        uv run mark2pdf sample.md            # 转换单个文件
        uv run mark2pdf --dir docs           # 转换整个目录
        uv run mark2pdf sample.md --indir in # 自定义输入目录
    """
    # 获取默认目录（如果用户未指定）
    default_indir, default_outdir = get_default_dirs()
    build_defaults = get_build_defaults()

    indir = indir or default_indir
    outdir = outdir or default_outdir

    # 构造通用选项对象
    options = ConversionOptions(
        template=template,
        coverimg=coverimg,
        to_typst=to_typst,
        savemd=savemd,
        removelink=removelink,
        tc=tc,
        overwrite=overwrite or build_defaults.get("overwrite", False),
        verbose=verbose,
    )

    postprocess = None
    if tc:
        from mark2pdf.postprocess.to_traditional_chinese import process as tc_process

        postprocess = tc_process

    result = None
    if directory:
        # 目录模式
        result = convert_directory(
            directory=directory,
            output_file=output,
            options=options,
            indir=indir,
            outdir=outdir,
            postprocess=postprocess,
        )
    elif mdfilename:
        # 文件模式
        result = convert_file(
            input_file=mdfilename,
            output_file=output,
            options=options,
            indir=indir,
            outdir=outdir,
            postprocess=postprocess,
        )
    else:
        click.echo("请提供 Markdown 文件名或使用 --dir 指定目录")
        click.echo("使用 --help 查看帮助")

    if result and open_file:
        open_with_system(result, verbose=verbose)


if __name__ == "__main__":
    cli()
