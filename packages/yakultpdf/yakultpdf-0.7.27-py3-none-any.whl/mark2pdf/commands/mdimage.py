"""
mark2pdf 图片处理命令

提供图片清理与目录结构迁移。
"""

import click

from mark2pdf.helper_mdimage import StructureMigrator, process_path_auto, resolve_input_path


@click.group(name="mdimage")
def mdimage():
    """图片处理工具 (清理与结构迁移)"""
    pass


@mdimage.command(name="download")
@click.argument("input_path", required=False)
@click.option("--delay", default=1.5, type=float, help="每次下载之间的延迟（秒），默认 1.5 秒")
@click.option("--overwrite", is_flag=True, help="直接覆盖原始文件而非保存为 *_processed.md")
def download(input_path: str | None, delay: float, overwrite: bool):
    """清理 Markdown 图片链接并下载到本地"""
    if not input_path:
        raise click.ClickException("请指定要处理的路径")

    path = resolve_input_path(input_path)
    if not path.exists():
        raise click.ClickException(f"路径不存在: {path}")

    # click.echo("🔧 微信图片特殊处理：下载失败时将使用占位符")

    process_path_auto(
        path,
        delay=delay,
        wechat_placeholder=True,
        overwrite=overwrite,
        log=click.echo,
    )


@mdimage.command(name="todir")
@click.argument("input_path", required=False)
@click.option("--keep", is_flag=True, help="保留原文件及图片")
def todir(input_path: str | None, keep: bool):
    """单文件模式 -> 文件夹模式"""
    if not input_path:
        raise click.ClickException("请指定要迁移的路径")

    path = resolve_input_path(input_path)
    if not path.exists():
        raise click.ClickException(f"路径不存在: {path}")

    migrator = StructureMigrator(log=click.echo)
    migrator.migrate_to_folder(path, keep_original=keep)


@mdimage.command(name="tofile")
@click.argument("input_path", required=False)
@click.option("--keep", is_flag=True, help="保留原文件及图片")
def tofile(input_path: str | None, keep: bool):
    """文件夹模式 -> 单文件模式"""
    if not input_path:
        raise click.ClickException("请指定要迁移的路径")

    path = resolve_input_path(input_path)
    if not path.exists():
        raise click.ClickException(f"路径不存在: {path}")

    migrator = StructureMigrator(log=click.echo)
    migrator.migrate_to_file(path, keep_original=keep)
