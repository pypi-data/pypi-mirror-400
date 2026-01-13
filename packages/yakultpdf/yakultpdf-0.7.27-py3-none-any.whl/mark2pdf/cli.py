"""
mark2pdf CLI

主命令行接口，提供工作区管理和 Markdown 转 PDF 功能。
"""

import click

from .commands import (
    clean,
    compress,
    convert,
    coverimg,
    fonts,
    gaozhi,
    init,
    mdimage,
    template,
    version,
)
from .commands.version import get_version


@click.group()
@click.version_option(version=get_version(), prog_name="yakultpdf")
def main():
    """mark2pdf - Markdown 转 PDF 工具集"""
    pass


# 注册子命令
main.add_command(clean)
main.add_command(compress)
main.add_command(coverimg)
main.add_command(fonts)
main.add_command(gaozhi)
main.add_command(mdimage)
main.add_command(init)
main.add_command(template)
main.add_command(version)
main.add_command(convert)


if __name__ == "__main__":
    main()
