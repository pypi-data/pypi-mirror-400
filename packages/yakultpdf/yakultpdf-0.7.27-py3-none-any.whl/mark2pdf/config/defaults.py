# mark2pdf 配置管理默认值
# 从全局 defaults.py 导入

from mark2pdf.defaults import CONFIG_FILENAME, DEFAULT_TEMPLATE  # noqa: F401

DEFAULT_CONFIG_CONTENT = """# mark2pdf.config.toml

[project]
name = ""

[paths]
in = "in"
out = "out"
tmp = "tmp"
template = "template"
fonts = "fonts"

[options]
default_template = "nb"
overwrite = false
"""

HELPER_SCRIPT_CONTENT = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mark2pdf 帮助脚本 - 在此工作区中转换 Markdown 为 PDF

使用方法:
    python createpdf.py <文件名.md>
    python createpdf.py <文件名.md> --verbose
"""

import os
import sys

from mark2pdf.core import convert_file


def main():
    # 默认文件名
    default_file = "index.md"
    
    # 解析参数
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    filename = args[0] if args else default_file
    
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    tc = "--tc" in sys.argv
    show_help = "--help" in sys.argv or "-h" in sys.argv
    
    if show_help:
        print("使用方法: python createpdf.py [文件名.md] [选项]")
        print(f"默认文件: {default_file}")
        print("\n选项:")
        print("  --verbose, -v   显示详细信息")
        print("  --tc            转换为繁体中文")
        print("  --help, -h      显示此帮助")
        sys.exit(0)

    success = convert_file(
        input_file=filename,
        indir="in",
        outdir="out",
        tc=tc,
        verbose=verbose,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
'''

INDEX_MD_CONTENT = """---
title: 我的文档
---

# 标题

在此开始编写...
"""
