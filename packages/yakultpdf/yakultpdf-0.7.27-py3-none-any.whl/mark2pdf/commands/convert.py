"""
mark2pdf convert 命令
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import click

from mark2pdf.core.utils import merge_frontmatter
from mark2pdf.helper_markdown import extract_frontmatter
from mark2pdf.helper_typst import check_pandoc_typst, set_tool_check_skip

from ..config import (
    ConfigManager,
    load_frontmatter_yaml,
    print_config_report,
    print_execution_plan,
    resolve_template,
)
from ..conversion import run_batch_conversion, run_conversion, run_directory_conversion
from ..process_builder import build_postprocessor_chain


def get_processor_names_from_flags(
    removelink: bool = False,
    tc: bool = False,
    postprocess: str | None = None,
) -> list[str]:
    """
    从 CLI 标志构建处理器名称列表

    Args:
        removelink: 是否启用移除链接
        tc: 是否启用繁体转换
        postprocess: 自定义处理器名称

    Returns:
        处理器名称列表
    """
    processors: list[str] = []
    if removelink:
        processors.append("remove_links")
    if postprocess:
        processors.append(postprocess)
    if tc:
        processors.append("to_traditional_chinese")

    seen: set[str] = set()
    deduped: list[str] = []
    for name in processors:
        if name in seen:
            continue
        seen.add(name)
        deduped.append(name)
    return deduped


@dataclass
class ConvertContext:
    """转换上下文，包含所有执行所需的配置信息"""
    config: ConfigManager
    workspace: Path
    processor_names: list[str]
    final_postprocess: Callable[[str], str] | None
    merged_fm: dict
    final_template: str | None
    final_overwrite: bool


def _validate_convert_args(
    directory: str | None,
    batch_dir: str | None,
    batchall: bool,
) -> str | None:
    """验证参数并返回规范化的 batch_dir"""
    if batchall:
        if batch_dir:
            click.echo("错误: --batchall 与 --batch 不能同时使用", err=True)
            sys.exit(1)
        return "."
    
    if directory and batch_dir:
        click.echo("错误: --dir 和 --batch/--batchall 不能同时使用", err=True)
        sys.exit(1)
        
    return batch_dir


def _prepare_convert_config(
    filename: str,
    directory: str | None,
    template: str | None,
    overwrite: bool,
    removelink: bool,
    tc: bool,
    postprocess: str | None,
    verbose: bool,
) -> ConvertContext:
    """加载配置、构建后处理器、准备 frontmatter"""
    # 1. 加载完整配置
    config = ConfigManager.load()
    workspace = config.data_root or Path.cwd()
    if verbose:
        if config.standalone:
            click.echo("⚠️  未检测到工作区配置，使用独立模式")
        else:
            click.echo(f"📂 工作区: {workspace}")

    # 2. 构建后处理器链
    processor_names = get_processor_names_from_flags(removelink, tc, postprocess)
    postprocess_result = build_postprocessor_chain(processor_names)
    
    if postprocess_result.missing:
        click.echo(f"⚠️  未找到处理器: {', '.join(postprocess_result.missing)}", err=True)
    if verbose and processor_names:
        shown = postprocess_result.loaded or processor_names
        click.echo(f"📦 后处理器: {', '.join(shown)}")

    # 3. 加载并合并 frontmatter
    default_fm = load_frontmatter_yaml(workspace)
    if config.frontmatter:
        default_fm = merge_frontmatter(config.frontmatter, default_fm)

    if directory:
        input_path = config.input_dir / directory / "index.md"
    else:
        input_path = config.input_dir / filename

    file_fm = extract_frontmatter(input_path) if input_path.exists() else {}
    merged_fm = merge_frontmatter(default_fm, file_fm)

    # 4. 解析模板和覆盖选项
    final_template = resolve_template(
        cli_template=template,
        frontmatter_template=merged_fm.get("theme", {}).get("template"),
        config_template=config.options.default_template,
    )
    final_overwrite = overwrite or config.options.overwrite

    return ConvertContext(
        config=config,
        workspace=workspace,
        processor_names=processor_names,
        final_postprocess=postprocess_result.chain,
        merged_fm=merged_fm,
        final_template=final_template,
        final_overwrite=final_overwrite,
    )


def _dispatch_conversion(
    ctx: ConvertContext,
    filename: str,
    directory: str | None,
    batch_dir: str | None,
    verbose: bool,
    open_file: bool,
    tc: bool,
    force_filename: bool,
    jobs: int,
    template: str | None,
) -> bool:
    """根据模式分发执行转换"""
    if directory:
        return run_directory_conversion(
            directory=directory,
            workspace_dir=ctx.workspace,
            verbose=verbose,
            overwrite=ctx.final_overwrite,
            template=template,
            postprocess=ctx.final_postprocess,
            open_file=open_file,
            tc=tc,
            force_filename=force_filename,
        )
    elif batch_dir:
        return run_batch_conversion(
            directory=batch_dir,
            workspace_dir=ctx.workspace,
            verbose=verbose,
            overwrite=ctx.final_overwrite,
            template=template,
            postprocess=ctx.final_postprocess,
            processor_names=ctx.processor_names,
            open_file=open_file,
            tc=tc,
            force_filename=force_filename,
            jobs=jobs,
        )
    else:
        return run_conversion(
            filename=filename,
            workspace_dir=ctx.workspace,
            verbose=verbose,
            overwrite=ctx.final_overwrite,
            template=template,
            postprocess=ctx.final_postprocess,
            open_file=open_file,
            tc=tc,
            force_filename=force_filename,
        )


@click.command()
@click.argument("filename", required=False, default="index.md")
@click.option("--dir", "-d", "directory", help="目录合并模式：合并目录中所有 Markdown 并转换")
@click.option("--batch", "-b", "batch_dir", help="批量模式：逐一转换目录中每个 Markdown")
@click.option("--batchall", is_flag=True, help="批量模式：等价于 --batch .")
@click.option("--jobs", "-j", default=4, type=click.IntRange(1, None), help="并发数（仅批量模式有效，默认 4）")
@click.option("--template", "-t", help="指定模板文件")
@click.option("--tc", is_flag=True, help="转换为繁体中文")
@click.option("--removelink", is_flag=True, help="移除链接（保留图片）")
@click.option("--open", "-o", "open_file", is_flag=True, help="转换完成后打开文件")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
@click.option("--overwrite", is_flag=True, help="覆盖输出文件（不添加时间戳）")
@click.option("--postprocess", "-p", help="后处理器名称（预留）")
@click.option("--show-config", is_flag=True, help="仅显示配置，不执行转换")
@click.option("--dry-run", is_flag=True, help="试运行模式，显示配置和执行计划")
@click.option("--force-filename", is_flag=True, help="强制使用原始文件名（忽略 exportFilename）")
@click.option("--skip-tool-check", is_flag=True, help="跳过 pandoc/typst 安装检查")
def convert(
    filename: str,
    directory: str | None,
    batch_dir: str | None,
    batchall: bool,
    jobs: int,
    template: str | None,
    tc: bool,
    removelink: bool,
    open_file: bool,
    verbose: bool,
    overwrite: bool,
    postprocess: str | None,
    show_config: bool,
    dry_run: bool,
    force_filename: bool,
    skip_tool_check: bool,
):
    """转换 Markdown 为 PDF

    使用方式：
        mark2pdf convert sample.md              # 转换单个文件
        mark2pdf convert --dir docs             # 合并目录转换
        mark2pdf convert --batch .              # 批量转换目录中所有文件
        mark2pdf convert --batchall             # 批量转换当前目录
    """
    # 1. 验证参数
    batch_dir = _validate_convert_args(directory, batch_dir, batchall)

    # 2. 准备配置上下文
    ctx = _prepare_convert_config(
        filename=filename,
        directory=directory,
        template=template,
        overwrite=overwrite,
        removelink=removelink,
        tc=tc,
        postprocess=postprocess,
        verbose=verbose,
    )

    # 3. 显示配置或执行计划
    if show_config or dry_run or verbose:
        cli_params = {
            "filename": filename if not directory else None,
            "directory": directory,
            "batch_dir": batch_dir,
            "jobs": jobs if jobs != 1 else None,
            "template": template,
            "tc": tc,
            "removelink": removelink,
            "overwrite": overwrite,
            "postprocess": postprocess,
            "force_filename": force_filename,
            "skip_tool_check": skip_tool_check,
        }
        print_config_report(
            config=ctx.config,
            cli_params=cli_params,
            merged_fm=ctx.merged_fm,
            final_template=ctx.final_template,
            final_overwrite=ctx.final_overwrite,
            tc=tc,
        )

        if show_config:
            return

    if dry_run:
        print_execution_plan(directory, batch_dir, filename, jobs=jobs)
        return

    # 4. 执行转换
    # 工具检查（仅在实际转换前执行）
    set_tool_check_skip(skip_tool_check)
    if not skip_tool_check:
        check_pandoc_typst()

    success = _dispatch_conversion(
        ctx=ctx,
        filename=filename,
        directory=directory,
        batch_dir=batch_dir,
        verbose=verbose,
        open_file=open_file,
        tc=tc,
        force_filename=force_filename,
        jobs=jobs,
        template=template,
    )

    if not success:
        sys.exit(1)
