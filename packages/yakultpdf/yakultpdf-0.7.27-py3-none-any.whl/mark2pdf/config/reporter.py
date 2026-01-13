"""
mark2pdf 报告器

负责 --show-config、--dry-run 和 --verbose 模式下的配置和计划输出。
"""

import click

from .types import PdfworkConfig


def print_config_report(
    config: PdfworkConfig,
    cli_params: dict,
    merged_fm: dict,
    final_template: str | None,
    final_overwrite: bool,
    tc: bool = False,
) -> None:
    """
    打印配置报告

    Args:
        config: 加载的配置对象
        cli_params: CLI 参数字典
        merged_fm: 合并后的 frontmatter
        final_template: 最终使用的模板
        final_overwrite: 最终的覆盖设置
        tc: 是否启用繁体转换
    """
    click.echo("=" * 50)
    click.echo("📋 合并后的完整配置")
    click.echo("=" * 50)

    click.echo("\n[CLI 参数]")
    for key, value in cli_params.items():
        if value:
            click.echo(f"  {key}: {value}")

    click.echo("\n[mark2pdf.config.toml]")
    click.echo(f"  paths.input: {config.paths.input}")
    click.echo(f"  paths.output: {config.paths.output}")
    click.echo(f"  paths.fonts: {config.paths.fonts}")
    click.echo(f"  options.overwrite: {config.options.overwrite}")
    if config.options.default_template:
        click.echo(f"  options.default_template: {config.options.default_template}")

    click.echo("\n[frontmatter 合并结果]")
    if merged_fm:
        for key, value in merged_fm.items():
            # 截断过长的值
            str_value = str(value)
            if len(str_value) > 60:
                str_value = str_value[:57] + "..."
            click.echo(f"  {key}: {str_value}")
    else:
        click.echo("  (无 frontmatter)")

    click.echo("\n[最终生效值]")
    click.echo(f"  template: {final_template}")
    click.echo(f"  overwrite: {final_overwrite}")
    click.echo(f"  tc: {tc}")
    click.echo("=" * 50)


def print_execution_plan(
    directory: str | None,
    batch_dir: str | None,
    filename: str,
    jobs: int = 1,
) -> None:
    """
    打印执行计划（dry-run 模式）

    Args:
        directory: 目录合并模式的目录名
        batch_dir: 批量模式的目录名
        filename: 输入文件名
    """
    click.echo("\n🔧 执行计划:")
    if directory:
        click.echo(f"  合并目录 '{directory}' 中所有 Markdown 并转换为 PDF")
    elif batch_dir:
        if jobs > 1:
            click.echo(f"  并发转换目录 '{batch_dir}' 中每个 Markdown（jobs={jobs}）")
        else:
            click.echo(f"  逐一转换目录 '{batch_dir}' 中每个 Markdown")
    else:
        click.echo(f"  转换文件 '{filename}' 为 PDF")
