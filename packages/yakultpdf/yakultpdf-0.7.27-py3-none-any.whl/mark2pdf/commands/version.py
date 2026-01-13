"""
mark2pdf 版本命令
"""

import click


def get_version() -> str:
    """获取包版本号"""
    try:
        from importlib.metadata import version

        return version("yakultpdf")
    except Exception:
        return "unknown"


@click.command()
def version():
    """显示版本信息"""
    click.echo(f"mark2pdf {get_version()}")
