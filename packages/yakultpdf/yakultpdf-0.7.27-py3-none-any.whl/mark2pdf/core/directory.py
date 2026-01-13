"""
mark2pdf.core 目录模式 API

提供目录合并和转换功能。
"""

from collections.abc import Callable
from pathlib import Path

from mark2pdf.helper_markdown import extract_frontmatter, pre_clean_frontmatter
from mark2pdf.helper_typst import check_pandoc_typst

from .core import execute_in_sandbox
from .options import ConversionOptions
from .postprocess import ensure_tc_postprocess
from .utils import (
    apply_default_preprocessing,
    get_output_filename,
    inject_default_frontmatter,
)


def merge_directory_markdown(dir_path: Path, verbose: bool = False) -> str:
    """
    合并目录中的所有 markdown 文件

    参数：
        dir_path: 目录路径
        verbose: 是否显示详细信息

    返回：
        合并后的内容字符串
    """
    if not dir_path.is_dir():
        raise ValueError(f"目录不存在：{dir_path}")

    merged_content = []

    # 首先处理 index.mdx 或 index.md（优先 mdx）
    index_path = dir_path / "index.mdx"
    if not index_path.exists():
        index_path = dir_path / "index.md"
    if index_path.exists():
        if verbose:
            print(f"读取 {index_path.name}...")
        with open(index_path, encoding="utf-8") as f:
            merged_content.append(f.read())

    # 获取所有其他 .md 文件并排序
    md_files = []
    for md_file in dir_path.glob("*.md"):
        if md_file.name not in ["index.md", "merged.md"] and not md_file.name.startswith("md2pdf_"):
            md_files.append(md_file)

    md_files.sort(key=lambda x: x.name)

    for md_file in md_files:
        if verbose:
            print(f"读取 {md_file.name}...")
        with open(md_file, encoding="utf-8") as f:
            content = f.read()
            if merged_content:
                # 使用更健壮的 frontmatter 移除函数
                content = pre_clean_frontmatter(content)
            merged_content.append(content)

    if len(merged_content) > 0:
        final_content = merged_content[0]
        if len(merged_content) > 1:
            final_content += "\n\n" + merged_content[1]
            for content in merged_content[2:]:
                final_content += "\n\n---\n\n" + content
    else:
        final_content = ""

    if verbose:
        print(f"合并完成，共 {len(md_files) + (1 if index_path.exists() else 0)} 个文件")

    return final_content


def convert_directory(
    directory: str,
    output_file: str | None = None,
    options: ConversionOptions = ConversionOptions(),
    indir: str | None = None,
    outdir: str | None = None,
    default_frontmatter: dict | None = None,
    postprocess: Callable[[str], str] | None = None,
    config: object | None = None,
) -> Path | None:
    """
    合并目录中所有 Markdown 并转换为 PDF

    参数：
        directory: 目录路径（相对于 indir）
        output_file: 输出文件名（可选）
        options: 转换配置选项
        indir: 输入目录（默认从配置读取）
        outdir: 输出目录（默认从配置读取）
        default_frontmatter: 默认 frontmatter 字典，用于注入缺失的字段
        postprocess: 后处理函数，接收内容返回处理后内容。在内置预处理之后追加执行
        config: PdfworkConfig 配置对象（可选）

    返回：
        成功返回输出文件路径 Path，失败返回 None
    """
    check_pandoc_typst()

    if options.verbose:
        print(f"使用目录模式：{directory}")

    if config is None:
        try:
            from mark2pdf import ConfigManager

            config = ConfigManager.load()
        except ImportError:
            config = None

    base_dir = Path.cwd()
    if config is not None and config.data_root is not None:
        base_dir = config.data_root

    if indir is None and config is not None:
        indir_path = config.input_dir
    else:
        indir_path = Path(indir or "in")
        if not indir_path.is_absolute():
            indir_path = base_dir / indir_path

    if outdir is None and config is not None:
        out_dir = config.output_dir
    else:
        out_dir = Path(outdir or "out")
        if not out_dir.is_absolute():
            out_dir = base_dir / out_dir

    dir_path = indir_path / directory

    content = merge_directory_markdown(dir_path, verbose=options.verbose)

    # 系统级：注入默认 frontmatter（在所有预处理之前）
    if default_frontmatter:
        content = inject_default_frontmatter(content, default_frontmatter, verbose=options.verbose)

    frontmatter = extract_frontmatter(content)

    if not output_file:
        output_name = dir_path.name
    else:
        output_name = output_file

    ext = "typ" if options.to_typst else "pdf"
    output_path = out_dir / f"{output_name}.{ext}"

    # 获取最终输出文件名
    output_path = get_output_filename(
        content,
        output_path,
        options.tc,
        options.verbose,
        options.force_filename,
        frontmatter=frontmatter,
    )

    # 预处理
    if options.verbose:
        print("应用 Markdown 预处理...")

    content = apply_default_preprocessing(
        content, removelink=options.removelink, verbose=options.verbose
    )

    if options.tc:
        postprocess = ensure_tc_postprocess(postprocess)

    if postprocess:
        content = postprocess(content)

    # 创建沙箱并执行转换
    if config is not None and config.data_root is not None:
        tmp_dir = config.tmp_dir
    else:
        tmp_dir = base_dir / "tmp"

    return execute_in_sandbox(
        content=content,
        temp_filename=f"{output_name}.md",
        output_path=output_path,
        images_source_dir=dir_path,  # 目录模式：使用目录本身（in/目录名/images/）
        tmp_dir=tmp_dir,
        sandbox_prefix="md2pdf_dir_",
        options=options,
        config=config,
        frontmatter=frontmatter,
    )
