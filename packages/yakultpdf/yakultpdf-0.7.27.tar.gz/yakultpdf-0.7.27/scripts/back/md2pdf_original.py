# /// script
# dependencies = [
#     "click>=8.0.0","PyYaml","opencc"
# ]
# ///

import re
import tempfile
from pathlib import Path

import click
import yaml
from opencc import OpenCC

from helper_interfile.interfile_manager import *
from helper_markdown import pre_add_line_breaks, pre_for_typst, pre_remove_links
from helper_typst import check_pandoc_typst, run_pandoc_typst
from helper_workingpath import resolve_inout_paths, resolve_template_path

############################################################################
#  重要使用说明：
#    -  需安装有 pandoc
#    -  需安装有 typst
#    -  输入文件必须在 _working/in 中 (注意模板与缺省路径设置)
#    -  输出结果保存在 _working/out 中
############################################################################

DEFAULT_TEMPLATE = "nb.typ"


def extract_frontmatter(content: str) -> dict:
    """
    从 markdown 内容中提取 frontmatter

    返回：
        frontmatter_dict
    """
    # 匹配 YAML frontmatter
    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if match:
        frontmatter_str = match.group(1)
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            return frontmatter or {}
        except yaml.YAMLError:
            return {}

    return {}


def get_output_filename(content: str, default_output_path: Path, tc: bool, verbose: bool) -> Path:
    """
    从 frontmatter 中提取自定义输出文件名，或使用默认值

    参数：
        content: markdown 文件内容
        default_output_path: 默认输出路径
        tc: 是否转换为繁体中文
        verbose: 是否显示详细信息

    返回：
        最终的输出路径
    """
    frontmatter = extract_frontmatter(content)

    if frontmatter.get("exportFilename"):
        export_filename = frontmatter["exportFilename"]

        # 如果启用了繁体转换，也转换文件名
        if tc:
            cc = OpenCC("s2t")
            export_filename = cc.convert(export_filename)

        # 更新输出路径，保持在同一输出目录
        output_path = Path(default_output_path).parent / export_filename

        if verbose:
            click.echo(f"使用 frontmatter 中的输出文件名：{export_filename}")

        return output_path

    return default_output_path


def merge_directory_markdown(dir_path: Path, verbose: bool = False) -> tuple[str, Path]:
    """
    合并目录中的所有 markdown 文件

    参数：
        dir_path: 目录路径
        verbose: 是否显示详细信息

    返回：
        (合并后的内容, 合并文件保存路径)
    """
    if not dir_path.is_dir():
        raise ValueError(f"目录不存在：{dir_path}")

    merged_content = []

    # 首先处理 index.md
    index_path = dir_path / "index.md"
    if index_path.exists():
        if verbose:
            click.echo("读取 index.md...")
        with open(index_path, encoding="utf-8") as f:
            merged_content.append(f.read())

    # 获取所有其他 .md 文件并排序
    md_files = []
    for md_file in dir_path.glob("*.md"):
        # 排除 index.md、merged.md 和临时文件（md2pdf_*.md）
        if md_file.name not in ["index.md", "merged.md"] and not md_file.name.startswith("md2pdf_"):
            md_files.append(md_file)

    # 按文件名排序
    md_files.sort(key=lambda x: x.name)

    # 读取并合并内容
    for md_file in md_files:
        if verbose:
            click.echo(f"读取 {md_file.name}...")
        with open(md_file, encoding="utf-8") as f:
            content = f.read()
            # 移除可能存在的 frontmatter（除了第一个文件）
            if merged_content:  # 不是第一个文件
                content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)
            merged_content.append(content)

    # 用分隔符连接所有内容
    # index.md 后的第一个文件只用 \n\n 连接，不加 ---
    # 从第二个文件开始才加 \n\n---\n\n
    if len(merged_content) > 0:
        final_content = merged_content[0]
        if len(merged_content) > 1:
            final_content += "\n\n" + merged_content[1]  # 第一个文件不加 ---
            for content in merged_content[2:]:
                final_content += "\n\n---\n\n" + content
    else:
        final_content = ""

    # 临时保存合并后的文件到目录中（用于后续处理）
    merged_file_path = dir_path / "merged.md"
    with open(merged_file_path, "w", encoding="utf-8") as f:
        f.write(final_content)

    if verbose:
        click.echo(f"合并完成，共 {len(md_files) + (1 if index_path.exists() else 0)} 个文件")

    return final_content, merged_file_path


@click.command()
@click.argument("mdfilename", default="")
@click.option("--dir", "directory", help="处理整个目录，合并所有 markdown 文件")
@click.option("--template", default=DEFAULT_TEMPLATE, help="typst 模板文件")
@click.option("--coverimg", help="封面图片")
@click.option("--cover", is_flag=True, help="显示封面")
@click.option("--to-typst", is_flag=True, help="输出 typst 文件")
@click.option("--output", help="自定义输出文件名（不含路径，会自动添加.pdf 或.typ 扩展名）")
@click.option("--savemd", is_flag=True, help="保留预处理后的中间 Markdown 文件")
@click.option("--removelink", is_flag=True, help="移除链接（保留图片）")
@click.option("--tc", is_flag=True, help="将简体中文转换为繁体中文")
@click.option("--verbose", is_flag=True, help="显示详细的复制和清除操作信息")
def cli(
    mdfilename: str,
    directory: str,
    template: str,
    coverimg: str,
    cover: bool,
    to_typst: bool,
    output: str,
    savemd: bool,
    removelink: bool,
    tc: bool,
    verbose: bool,
) -> None:
    # 检查 pandoc、typst 是否已安装
    check_pandoc_typst()

    # 初始化 merged_file_path（用于 directory 模式的清理）
    merged_file_path = None

    # === 处理 --dir 模式 ===
    if directory:
        # 使用目录模式
        if verbose:
            click.echo(f"使用目录模式：{directory}")

        # 解析目录路径
        dir_path = Path("_working/in") / directory
        if not dir_path.is_absolute():
            dir_path = Path.cwd() / dir_path

        # 合并目录中的 markdown 文件
        content, merged_file_path = merge_directory_markdown(dir_path, verbose=verbose)

        # 使用合并后的文件作为输入
        input_path = merged_file_path

        # 输出文件保存到 _working/out 目录
        out_dir = Path.cwd() / "_working/out"
        if not output:
            # 使用目录名作为输出文件名
            output_name = dir_path.name
        else:
            output_name = output

        # 根据输出类型确定文件扩展名
        ext = "typ" if to_typst else "pdf"
        output_path = out_dir / f"{output_name}.{ext}"

    else:
        # 使用文件模式（原有逻辑）
        # 解析输入输出路径、获取模板路径
        # 根据输出类型确定文件扩展名
        ext = "typ" if to_typst else "pdf"

        input_path, output_path = resolve_inout_paths(
            infile=mdfilename,
            outfile=output,
            indir="_working/in",
            outdir="_working/out",
            ext=ext,
        )

        # 读取 markdown 文件内容
        with open(input_path, encoding="utf-8") as f:
            content = f.read()

    # 获取最终输出文件名（可能从 frontmatter 中覆盖）
    output_path = get_output_filename(content, output_path, tc, verbose)

    # === 应用预处理 markdown ===
    if verbose:
        click.echo("应用 Markdown 预处理...")

    # 移除链接（如果启用）
    if removelink:
        content = pre_remove_links(content, verbose=verbose)

    # 添加空行分隔
    content = pre_add_line_breaks(content, verbose=verbose)

    # 应用 Typst 格式预处理
    content = pre_for_typst(content, verbose=verbose)

    # 转换为繁体中文（如果启用）
    if tc:
        if verbose:
            click.echo("转换为繁体中文...")
        cc = OpenCC("s2t")  # 简体到繁体
        content = cc.convert(content)

    # 使用 helper_interfile 创建和写入临时文件
    if directory:
        # 在 --dir 模式下，临时文件放在目标目录中
        temp_fd = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix="md2pdf_", suffix=".md", dir=dir_path, delete=False
        )
        temp_path = Path(temp_fd.name)
        temp_fd.write(content)
        temp_fd.close()
        if verbose:
            click.echo(f"创建临时文件：{temp_path}")

        # 使用目标目录作为工作目录
        pandoc_workdir = dir_path
        temp_filename = temp_path.name
    else:
        # 原有逻辑
        temp_fd, temp_path = create_md_tmpfile(input_path, prefix="md2pdf_", verbose=verbose)
        write_to_tmpfile(temp_fd, content, verbose=verbose)
        pandoc_workdir = Path(temp_path).parent
        temp_filename = Path(temp_path).name

    template_path = resolve_template_path(template)

    # 构建参数字典，支持 coverimg 和 nocover
    pandoc_args = {}
    if coverimg:
        pandoc_args["coverimg"] = coverimg
    if not cover:  # 默认不显示封面，只有设置了 --cover 才显示
        pandoc_args["nocover"] = "true"

    try:
        success = run_pandoc_typst(
            input_file=temp_filename,
            output_file=output_path,
            template_path=template_path,
            pandoc_workdir=pandoc_workdir,
            verbose=verbose,
            to_typst=to_typst,
            **pandoc_args,
        )
    finally:
        # 根据 savemd 参数决定是否保留临时文件
        if savemd:
            if verbose or success:
                click.echo(f"预处理后的 Markdown 已保存至：{temp_path}")
                # 如果是 directory 模式，也显示 merged.md 的位置
                if directory:
                    click.echo(f"合并后的 Markdown 已保存至：{merged_file_path}")
        else:
            # 使用 helper_interfile 清理临时文件
            cleanup_tmpfile(temp_path, verbose=verbose)

            # 如果是 directory 模式，也清理 merged.md
            if directory and merged_file_path and merged_file_path.exists():
                merged_file_path.unlink()
                if verbose:
                    click.echo(f"清理临时文件：{merged_file_path}")

    if success:
        click.echo(f"转换成功：{output_path}")
    else:
        click.echo("转换失败")


if __name__ == "__main__":
    cli()
