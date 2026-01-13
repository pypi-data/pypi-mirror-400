#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "mark2pdf",
#     "click",
# ]
# [tool.uv.sources]
# mark2pdf = { path = "/Users/fangjun/python/pdfwork", editable = true }
# ///
# -*- coding: utf-8 -*-
"""
Markdown → PDF 转换脚本

使用方法:
    ./createpdf.py [文件名]           # 转换单个文件（默认 index.md）
    ./createpdf.py --dir 目录名       # 合并目录中所有 Markdown 为一个 PDF
    ./createpdf.py --batch 目录名     # 逐一转换目录中每个 Markdown
    ./createpdf.py --batchall         # 等价于 --batch .

选项:
    -v, --verbose     详细输出
    --overwrite       覆盖已有文件
    -t, --template    指定模板
    --tc              转换为繁体中文
    -o, --open        转换完成后打开文件
"""

from pathlib import Path

import click

from mark2pdf import run_batch_conversion, run_conversion, run_directory_conversion

WORKSPACE_DIR = Path(__file__).parent.resolve()


def postprocess(content: str) -> str:
    """工作区特定的后处理逻辑（可选扩展点）"""
    return content


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("filename", required=False, default="index.md")
@click.option(
    "--dir", "-d", "directory", default=None, help="目录模式：合并目录中所有 Markdown 并转换"
)
@click.option(
    "--batch", "-b", "batch_dir", default=None, help="批量模式：逐一转换目录中每个 Markdown"
)
@click.option(
    "--batchall", is_flag=True, help="批量模式：转换当前目录所有 Markdown（等价于 --batch .）"
)
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
@click.option("--overwrite", is_flag=True, help="覆盖输出文件（不添加时间戳）")
@click.option("--template", "-t", default=None, help="指定模板文件（优先级最高）")
@click.option("--tc", is_flag=True, help="转换为繁体中文")
@click.option("--open", "-o", "open_file", is_flag=True, help="转换完成后打开文件")
def main(filename, directory, batch_dir, batchall, verbose, overwrite, template, tc, open_file):
    """在当前工作区转换 Markdown 为 PDF。"""
    # --batchall 等价于 --batch .
    if batchall:
        batch_dir = "."

    if directory and batch_dir:
        raise click.UsageError("--dir 和 --batch/--batchall 不能同时使用")

    if directory:
        # 目录模式（合并）
        success = run_directory_conversion(
            directory=directory,
            workspace_dir=WORKSPACE_DIR,
            verbose=verbose,
            overwrite=overwrite,
            template=template,
            tc=tc,
            open_file=open_file,
        )
    elif batch_dir:
        # 批量模式（逐一）
        success = run_batch_conversion(
            directory=batch_dir,
            workspace_dir=WORKSPACE_DIR,
            verbose=verbose,
            overwrite=overwrite,
            template=template,
            tc=tc,
            open_file=open_file,
        )
    else:
        # 文件模式
        success = run_conversion(
            filename=filename,
            workspace_dir=WORKSPACE_DIR,
            postprocess=postprocess,
            verbose=verbose,
            overwrite=overwrite,
            template=template,
            tc=tc,
            open_file=open_file,
        )
    if not success:
        raise click.Abort()


if __name__ == "__main__":
    main()
