# /// script
# dependencies = ["click", "pillow"]
# ///

import click
from PIL import Image, ImageDraw, ImageFont


def add_text_to_cover(
    image_path: str,
    output_path: str,
    cn_title: str,
    en_deco: str,
    cn_y: int = 200,
    en_y: int = 500,
    cn_rotation: float = 0,
    en_rotation: float = 5.5,
    cn_font_size: int = 60,
    en_font_size: int = 45,
    en_x: int = 260,
):
    """在封面图片上添加倾斜的文字"""

    # 打开图片
    img = Image.open(image_path)

    # 转换 en_deco 为大写
    en_deco = en_deco.upper()

    # 创建绘图对象
    draw = ImageDraw.Draw(img)

    # 尝试使用系统中文字体 Heavy 变体
    try:
        # SourceHanSans.ttc 中 index 5 通常是 Heavy
        cn_font = ImageFont.truetype(
            "/System/Library/Fonts/SourceHanSans.ttc", cn_font_size, index=6
        )
    except Exception as e:
        try:
            # 如果 index 5 不存在，尝试使用 PingFang Heavy
            cn_font = ImageFont.truetype(
                "/System/Library/Fonts/PingFang.ttc", cn_font_size, index=6
            )
        except Exception:
            cn_font = ImageFont.load_default()
            click.echo(f"警告: 无法加载中文 Heavy 字体，使用默认字体 ({e})")

    # 尝试使用英文 Heavy 字体
    try:
        # Helvetica.ttc 或 HelveticaNeue.ttc 中的 Heavy 变体
        en_font = ImageFont.truetype("/System/Library/Fonts/Arial Black.ttf", en_font_size)
    except Exception as e:
        en_font = ImageFont.load_default()
        click.echo(f"警告: 无法加载英文 Heavy 字体，使用默认字体 ({e})")

    # 绘制中文标题（白色，在上部）
    cn_lines = cn_title.strip().split("\n")
    for i, line in enumerate(cn_lines):
        line = line.strip()
        if line:
            # 创建临时图片用于旋转文字
            # 获取文字尺寸
            bbox = draw.textbbox((0, 0), line, font=cn_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 创建临时图片（给大字体留足够的空间，避免被截断）
            padding = max(100, cn_font_size)  # 根据字体大小动态调整边距
            temp_img = Image.new(
                "RGBA", (text_width + padding * 2, text_height + padding * 2), (255, 255, 255, 0)
            )
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.text((padding, padding), line, font=cn_font, fill=(255, 255, 255, 255))

            # 旋转文字
            rotated = temp_img.rotate(cn_rotation, expand=True, fillcolor=(255, 255, 255, 0))

            # 计算粘贴位置（居中）
            x = (img.width - rotated.width) // 2 + 70
            y = cn_y + i * (cn_font_size + 10)

            # 粘贴到原图
            img.paste(rotated, (x, y), rotated)

    # 绘制英文装饰文字（黑色，在现有文字上）
    en_lines = en_deco.strip().split("\n")
    for i, line in enumerate(en_lines):
        line = line.strip()
        if line:
            # 创建临时图片用于旋转文字
            bbox = draw.textbbox((0, 0), line, font=en_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 创建临时图片（给大字体留足够的空间，避免被截断）
            padding = max(100, en_font_size)  # 根据字体大小动态调整边距
            temp_img = Image.new(
                "RGBA", (text_width + padding * 2, text_height + padding * 2), (255, 255, 255, 0)
            )
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.text((padding, padding), line, font=en_font, fill=(255, 255, 255, 255))

            # 旋转文字
            rotated = temp_img.rotate(en_rotation, expand=True, fillcolor=(255, 255, 255, 0))

            # 计算粘贴位置（左对齐）
            x = en_x  # 左对齐位置
            y = en_y + i * (en_font_size - 20)  # 减小行间距让文字更紧凑

            # 粘贴到原图
            img.paste(rotated, (x, y), rotated)

    # 保存结果
    img.save(output_path)
    click.echo(f"封面已保存到: {output_path}")


@click.command()
@click.option("--input", "-i", default="_working/in/new.png", help="输入图片路径")
@click.option("--output", "-o", default="_working/out/cover_with_text.png", help="输出图片路径")
@click.option("--cn-y", default=200, help="中文标题Y坐标位置")
@click.option("--en-y", default=700, help="英文装饰文字Y坐标位置")
@click.option("--cn-rotation", default=-2.0, help="中文倾斜角度（正数向右上倾斜）")
@click.option("--en-rotation", default=2.5, help="英文倾斜角度（正数向右上倾斜）")
@click.option("--cn-size", default=70, help="中文字体大小")
@click.option("--en-size", default=135, help="英文字体大小")
@click.option("--en-x", default=120, help="英文X坐标位置（左对齐）")
def main(input, output, cn_y, en_y, cn_rotation, en_rotation, cn_size, en_size, en_x):
    """在封面图片上添加倾斜的中英文字"""

    cn_title = """数字资产财库公司
的崛起"""

    en_deco = """
Digital
Asset
Trea
sury"""

    add_text_to_cover(
        image_path=input,
        output_path=output,
        cn_title=cn_title,
        en_deco=en_deco,
        cn_y=cn_y,
        en_y=en_y,
        cn_rotation=cn_rotation,
        en_rotation=en_rotation,
        cn_font_size=cn_size,
        en_font_size=en_size,
        en_x=en_x,
    )


if __name__ == "__main__":
    main()
