"""
mark2pdf compress 命令

使用 PyMuPDF 压缩 PDF 文件大小。
"""

from pathlib import Path

import click
import fitz  # PyMuPDF

from ..config import ConfigManager


def compress_pdf(
    input_path: Path, output_path: Path, dpi: int = 150, verbose: bool = False
) -> tuple[int, int]:
    """压缩单个 PDF 文件

    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        dpi: 图片重采样 DPI（预留参数，暂未实现）
        verbose: 是否显示详细信息

    Returns:
        (原始大小, 压缩后大小) 字节数
    """
    # TODO: dpi 参数暂未使用，后续可实现真正的图片 DPI 重采样
    original_size = input_path.stat().st_size

    doc = fitz.open(input_path)

    # 统计
    png_count = 0
    jpeg_count = 0
    other_count = 0
    converted_count = 0

    # 遍历处理图片
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]

            try:
                # 提取图片
                base_image = doc.extract_image(xref)
                if not base_image:
                    continue

                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                if image_ext == "png":
                    png_count += 1
                elif image_ext in ("jpeg", "jpg"):
                    jpeg_count += 1
                else:
                    other_count += 1

                # PNG 转 JPEG（仅 >1MB 且无透明通道）
                if image_ext == "png" and len(image_bytes) > 1024 * 1024:
                    # 使用 fitz 的 Pixmap 处理
                    pix = fitz.Pixmap(image_bytes)

                    # 有 alpha 通道则跳过
                    if pix.alpha:
                        pix = None
                        continue

                    # 转为 JPEG
                    new_image = pix.tobytes("jpeg", jpg_quality=85)
                    pix = None

                    # 替换图片
                    page.replace_image(xref, stream=new_image)
                    converted_count += 1

            except Exception as e:
                if verbose:
                    click.echo(f"  ⚠️ 图片处理跳过: {e}")
                continue

    if verbose:
        click.echo(
            f"  📊 图片统计: PNG={png_count}, JPEG={jpeg_count}, 其他={other_count}, 已转换={converted_count}"
        )

    # 清理元数据等
    doc.scrub()

    # 保存（使用 ez_save 自动启用 garbage=3 + deflate）
    doc.ez_save(str(output_path))
    doc.close()

    compressed_size = output_path.stat().st_size
    return original_size, compressed_size


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"


@click.command()
@click.argument("filename", required=False)
@click.option("--all", "compress_all", is_flag=True, help="压缩 out 目录下所有 PDF")
@click.option("--no-overwrite", is_flag=True, help="不覆盖原文件，输出为 xxx_sm.pdf")
@click.option("--dpi", default=150, help="图片重采样 DPI（默认 150）")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
def compress(filename: str | None, compress_all: bool, no_overwrite: bool, dpi: int, verbose: bool):
    """压缩 PDF 文件大小

    使用方式：
        mark2pdf compress sample.pdf      # 压缩单个文件
        mark2pdf compress --all           # 压缩 out 目录下所有 PDF
        mark2pdf compress --no-overwrite  # 不覆盖，输出 xxx_sm.pdf
    """
    config = ConfigManager.load()
    out_dir = config.output_dir

    if not out_dir.exists():
        click.echo(f"❌ 输出目录不存在: {out_dir}", err=True)
        return

    # 确定要处理的文件列表
    if compress_all:
        pdf_files = list(out_dir.glob("*.pdf"))
        # 排除已压缩的 _sm.pdf
        pdf_files = [f for f in pdf_files if not f.stem.endswith("_sm")]
    elif filename:
        pdf_path = out_dir / filename
        if not pdf_path.exists():
            click.echo(f"❌ 文件不存在: {pdf_path}", err=True)
            return
        pdf_files = [pdf_path]
    else:
        # 默认处理 out 目录下所有 PDF
        pdf_files = list(out_dir.glob("*.pdf"))
        pdf_files = [f for f in pdf_files if not f.stem.endswith("_sm")]

    if not pdf_files:
        click.echo("📭 没有找到需要压缩的 PDF 文件")
        return

    # 按文件名排序
    pdf_files.sort(key=lambda f: f.name)

    total_original = 0
    total_compressed = 0
    success_count = 0

    for pdf_path in pdf_files:
        # 确定输出路径
        if no_overwrite:
            output_path = pdf_path.parent / f"{pdf_path.stem}_sm.pdf"
        else:
            output_path = pdf_path

        try:
            if verbose:
                click.echo(f"🔄 处理: {pdf_path.name}")

            # 如果覆盖模式，先保存到临时文件
            if not no_overwrite:
                temp_path = pdf_path.parent / f"{pdf_path.stem}_temp.pdf"
                orig_size, comp_size = compress_pdf(pdf_path, temp_path, dpi, verbose)
                temp_path.replace(pdf_path)
            else:
                orig_size, comp_size = compress_pdf(pdf_path, output_path, dpi, verbose)

            total_original += orig_size
            total_compressed += comp_size
            success_count += 1

            reduction = (1 - comp_size / orig_size) * 100 if orig_size > 0 else 0
            output_name = output_path.name if no_overwrite else pdf_path.name
            click.echo(
                f"✅ {output_name}: {format_size(orig_size)} → {format_size(comp_size)} (-{reduction:.0f}%)"
            )

        except OSError as e:
            click.echo(f"❌ {pdf_path.name}: {e}", err=True)

    # 显示汇总
    if success_count > 1:
        total_saved = total_original - total_compressed
        click.echo(f"📊 共压缩 {success_count} 个文件，节省 {format_size(total_saved)}")
