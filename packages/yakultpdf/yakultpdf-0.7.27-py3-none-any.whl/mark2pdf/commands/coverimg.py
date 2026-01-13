"""
mark2pdf 图片尺寸检查命令

Ported from scripts/checkimagesize.py
"""

import sys
from pathlib import Path

import click
from PIL import Image, ImageOps

# 常用纸型尺寸 @ 300dpi (宽 × 高，竖版)
PAPER_SIZES = {
    "a4": (2480, 3508),  # 210 × 297 mm
    "a5": (1748, 2480),  # 148 × 210 mm
    "letter": (2550, 3300),  # 8.5 × 11 in
    "legal": (2550, 4200),  # 8.5 × 14 in
    "b5": (2079, 2953),  # 176 × 250 mm
    "16:9": (1920, 1080),  # 横版 16:9
    "4:3": (1600, 1200),  # 横版 4:3
}


def get_image_size(image_path: Path) -> tuple[int, int] | None:
    """使用 Pillow 获取图片尺寸"""
    try:
        with Image.open(image_path) as img:
            return img.size  # (width, height)
    except OSError as e:
        click.echo(f"❌ 无法读取图片: {e}", err=True)
        return None


def check_fullpage(width: int, height: int, paper_width: int, paper_height: int) -> dict:
    """检查图片是否适合全页（基于比例）"""
    ratio = width / height if height else 0
    paper_ratio = paper_width / paper_height

    result = {
        "exact_match": width == paper_width and height == paper_height,
        "ratio_match": abs(ratio - paper_ratio) < 0.02,  # 允许 2% 误差
        "ratio": ratio,
        "paper_ratio": paper_ratio,
        "orientation": "portrait" if height > width else "landscape",
    }
    result["suitable"] = result["ratio_match"]
    return result


def crop_image(
    image_path: Path, paper_width: int, paper_height: int, output_suffix: str = "_fullpage"
) -> Path | None:
    """裁切转换图片为指定纸型尺寸（保持比例，超出部分裁切）"""
    output_path = image_path.parent / f"{image_path.stem}{output_suffix}{image_path.suffix}"
    target_size = (paper_width, paper_height)

    try:
        with Image.open(image_path) as img:
            # 转为 RGB（处理 RGBA 或其他模式）
            if img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # 裁切：保持比例放大，裁切超出部分
            result = ImageOps.fit(img, target_size, method=Image.Resampling.LANCZOS)

            result.save(output_path, quality=95)
            click.echo(f"✅ 已生成: {output_path}")
            click.echo(f"   尺寸: {result.size[0]} × {result.size[1]}")
            return output_path

    except OSError as e:
        click.echo(f"❌ 转换失败: {e}", err=True)
        return None


class DefaultGroup(click.Group):
    """自定义 Group：未匹配子命令时自动使用默认命令"""

    def __init__(self, *args, default_cmd: str = "check", **kwargs):
        super().__init__(*args, **kwargs)
        self.default_cmd = default_cmd

    def parse_args(self, ctx, args):
        # 如果有参数且第一个参数不是已知子命令，插入默认命令
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            args = [self.default_cmd] + list(args)
        return super().parse_args(ctx, args)


@click.group(cls=DefaultGroup, name="coverimg")
def coverimg():
    """封面图片工具 (尺寸检查与转换)"""
    pass


@coverimg.command()
@click.argument("image", type=click.Path(exists=True))
@click.option(
    "--paper",
    "-p",
    type=click.Choice(list(PAPER_SIZES.keys())),
    default="a4",
    help="纸型 (默认: a4)",
)
@click.option("--crop", is_flag=True, help="裁切转换为指定纸型尺寸")
def check(image: str, paper: str, crop: bool):
    """检查图片是否适合全页显示"""
    image_path = Path(image)
    paper_width, paper_height = PAPER_SIZES[paper]
    paper_ratio = paper_width / paper_height

    # 获取尺寸
    size = get_image_size(image_path)
    if not size:
        sys.exit(1)

    width, height = size
    ratio = width / height if height else 0

    click.echo(f"\n📷 {image_path.name}")
    click.echo(f"   尺寸: {width} × {height}")
    click.echo(f"   比例: {ratio:.3f}")
    click.echo(f"   目标: {paper.upper()} ({paper_width} × {paper_height}, 比例 {paper_ratio:.3f})")

    # 检查结果
    result = check_fullpage(width, height, paper_width, paper_height)

    if result["exact_match"]:
        click.echo(f"   ✅ 完全匹配 {paper.upper()} 全页!")
    elif result["suitable"]:
        click.echo("   ✅ 比例匹配，适合全页")
    else:
        diff = abs(result["ratio"] - result["paper_ratio"])
        click.echo(f"   ⚠️  比例不匹配 (差异: {diff:.3f})")

    # 裁切转换
    if crop:
        click.echo(f"\n🔄 裁切转换中... (纸型: {paper.upper()})")
        crop_image(image_path, paper_width, paper_height)


@coverimg.command("list")
def list_papers():
    """列出所有支持的纸型"""
    click.echo("\n支持的纸型 (@ 300dpi):")
    for name, (w, h) in PAPER_SIZES.items():
        click.echo(f"  {name:8s} : {w} × {h}")
