"""
mark2pdf 工作区管理命令

提供 init 和 template 命令。
"""

import sys
from pathlib import Path

import click

from ..config import init_workspace, install_template


@click.command()
@click.argument("target_dir", type=click.Path())
@click.option(
    "--template",
    "template_name",
    help="复制指定模板（文件或目录，若同名目录存在则优先目录）",
)
@click.option(
    "--simple",
    is_flag=True,
    help="仅创建配置与 frontmatter 示例，允许非空目录",
)
def init(target_dir: str, template_name: str | None, simple: bool):
    """初始化工作区

    TARGET_DIR: 目标目录 (例如 "." 或 "/path/to/dir")
    --simple: 仅创建配置与 frontmatter 示例
    """

    target = Path(target_dir).resolve()
    try:
        init_workspace(
            target,
            template_name=template_name,
            simple=simple,
        )
    except (FileExistsError, FileNotFoundError, ValueError) as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("template_name", type=str)
def template(template_name: str):
    """复制指定模板到当前工作区 template/ 目录（目录优先）"""

    try:
        target_dir = install_template(template_name)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)

    click.echo(f"模板已复制到: {target_dir}")
