from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import click
import tomllib

from .mdimage_rewrite import rewrite_markdown_images

MARKDOWN_SUFFIXES = {".md"}
CONFIG_FILENAME = "mark2pdf.config.toml"


@dataclass(frozen=True)
class ImageMode:
    name: str
    images_dir: Path
    rel_dir: str


def _resolve_default_input_dir() -> Path | None:
    try:
        from mark2pdf import ConfigManager

        config = ConfigManager.load()
        return config.input_dir
    except Exception:
        pass

    config_path = Path.cwd() / CONFIG_FILENAME
    if config_path.exists():
        try:
            with config_path.open("rb") as f:
                data = tomllib.load(f)
            input_value = data.get("paths", {}).get("in", "in")
            input_path = Path(input_value)
            if not input_path.is_absolute():
                input_path = config_path.parent / input_path
            if input_path.exists():
                return input_path
        except Exception:
            pass

    fallback = Path.cwd() / "in"
    if fallback.exists():
        return fallback
    return None


def resolve_input_path(raw: str) -> Path:
    if "/" not in raw and "\\" not in raw:
        default_dir = _resolve_default_input_dir()
        if default_dir is not None:
            candidate = default_dir / raw
            if candidate.exists():
                return candidate.resolve()
    return Path(raw).resolve()


def _ensure_md_file(md_path: Path) -> None:
    if md_path.suffix.lower() != ".md":
        raise click.ClickException("仅支持 .md 文件")


def _rewrite_and_save(
    md_path: Path,
    images_dir: Path,
    rel_dir: str,
    delay: float,
    wechat_placeholder: bool,
    overwrite: bool,
    log: Callable[[str], None],
):
    content = md_path.read_text(encoding="utf-8")
    result = rewrite_markdown_images(
        content,
        images_dir,
        rel_dir,
        delay=delay,
        wechat_placeholder=wechat_placeholder,
        log=log,
    )

    output_path = md_path if overwrite else md_path.with_name(f"{md_path.stem}_processed.md")
    output_path.write_text(result.content, encoding="utf-8")
    return output_path, result


def resolve_image_mode(md_path: Path) -> ImageMode:
    _ensure_md_file(md_path)
    base_name = md_path.stem
    flat_images = md_path.parent / "images" / base_name
    folder_images = md_path.parent / "images"

    if flat_images.is_dir():
        return ImageMode("flat", flat_images, f"images/{base_name}")
    if folder_images.is_dir():
        return ImageMode("folder", folder_images, "images")

    # 默认回退到目录模式，允许首次下载时自动创建 images/
    return ImageMode("folder", folder_images, "images")


def process_single(md_path: Path, delay: float, wechat_placeholder: bool, overwrite: bool) -> None:
    _ensure_md_file(md_path)
    base_name = md_path.stem
    images_dir = md_path.parent / "images" / base_name
    rel_dir = f"images/{base_name}"

    click.echo(f"📖 正在读取：{md_path.name}")
    click.echo("\n🧹 步骤 1: 清理 'Copy Image' 标记并处理图片...")
    output_path, _result = _rewrite_and_save(
        md_path,
        images_dir,
        rel_dir,
        delay=delay,
        wechat_placeholder=wechat_placeholder,
        overwrite=overwrite,
        log=click.echo,
    )
    click.echo(f"\n💾 步骤 2: 保存处理后的文件 -> {output_path.name}")
    click.echo(f"✅ 完成！图片目录：{images_dir}")


def process_directory(
    dir_path: Path, delay: float, wechat_placeholder: bool, overwrite: bool
) -> None:
    dir_name = dir_path.name
    images_dir = dir_path / "images" / dir_name
    rel_dir = f"images/{dir_name}"

    click.echo(f"📁 目录模式：{dir_path}")
    md_files = sorted(
        p for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() in MARKDOWN_SUFFIXES
    )
    if not md_files:
        click.echo("⚠️ 未找到 .md 文件。")
        return

    click.echo(f"🗂️  图片统一保存到：{images_dir}")
    for md_file in md_files:
        click.echo(f"\n📖 正在读取：{md_file.name}")
        click.echo("🧹 清理 'Copy Image' 标记并处理图片...")
        output_path, result = _rewrite_and_save(
            md_file,
            images_dir,
            rel_dir,
            delay=delay,
            wechat_placeholder=wechat_placeholder,
            overwrite=overwrite,
            log=click.echo,
        )
        click.echo(f"💾 保存处理后的文件 -> {output_path.name}")
        click.echo(f"✅ 完成：{output_path.name}，跳过 {result.skipped}，下载 {result.downloaded}")


def process_path_auto(
    input_path: Path,
    delay: float,
    wechat_placeholder: bool,
    overwrite: bool,
    log: Callable[[str], None] | None = None,
) -> None:
    log = log or click.echo

    if input_path.is_dir():
        md_files = sorted(
            p for p in input_path.iterdir() if p.is_file() and p.suffix.lower() in MARKDOWN_SUFFIXES
        )
        if not md_files:
            log("⚠️ 未找到 .md 文件。")
            return
        log(f"📁 目录模式：{input_path}")
        for md_file in md_files:
            mode = resolve_image_mode(md_file)
            log(f"📖 正在读取：{md_file.name}")
            log(f"🧭 模式: {mode.name}，图片目录：{mode.images_dir}")
            log("🧹 清理 'Copy Image' 标记并处理图片...")
            output_path, result = _rewrite_and_save(
                md_file,
                mode.images_dir,
                mode.rel_dir,
                delay=delay,
                wechat_placeholder=wechat_placeholder,
                overwrite=overwrite,
                log=log,
            )
            log(f"✅ 完成：{output_path.name}，跳过 {result.skipped}，下载 {result.downloaded}")
        return

    _ensure_md_file(input_path)
    mode = resolve_image_mode(input_path)
    log(f"📖 正在读取：{input_path.name}")
    log(f"🧭 模式: {mode.name}，图片目录：{mode.images_dir}")
    log("🧹 清理 'Copy Image' 标记并处理图片...")
    output_path, result = _rewrite_and_save(
        input_path,
        mode.images_dir,
        mode.rel_dir,
        delay=delay,
        wechat_placeholder=wechat_placeholder,
        overwrite=overwrite,
        log=log,
    )
    log(f"✅ 完成：{output_path.name}，跳过 {result.skipped}，下载 {result.downloaded}")


@click.command()
@click.argument("input_path_arg")
@click.option("--delay", default=1.5, type=float, help="每次下载之间的延迟（秒），默认 1.5 秒")
@click.option(
    "--wechat-placeholder/--no-wechat-placeholder",
    default=True,
    help="微信图片下载失败时是否插入占位符（默认开启）",
)
@click.option("--overwrite", is_flag=True, help="直接覆盖原始文件而非保存为 *_processed.md")
def main(input_path_arg: str, delay: float, wechat_placeholder: bool, overwrite: bool) -> None:
    """清理 Markdown 文件中的图片并下载到本地。"""
    input_path = resolve_input_path(input_path_arg)
    if not input_path.exists():
        raise click.BadParameter(f"Path '{input_path}' does not exist.")

    if wechat_placeholder:
        click.echo("🔧 微信图片特殊处理：下载失败时将使用占位符")
    else:
        click.echo("⚠️  微信图片占位符已禁用，下载失败将保留原链接")

    if input_path.is_dir():
        process_directory(input_path, delay, wechat_placeholder, overwrite)
    else:
        process_single(input_path, delay, wechat_placeholder, overwrite)


if __name__ == "__main__":
    main()
