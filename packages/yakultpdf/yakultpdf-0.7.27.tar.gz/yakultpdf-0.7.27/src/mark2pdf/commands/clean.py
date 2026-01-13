"""
mark2pdf 清理命令

清理工作区输出目录。
"""

import sys

import click

from ..config import ConfigManager


@click.command()
@click.option("--dry-run", is_flag=True, help="试运行模式，仅列出将要删除的文件")
@click.option("--force", "-f", is_flag=True, help="强制删除，不进行确认")
def clean(dry_run: bool, force: bool):
    """清理输出目录中的文件

    警告：此操作将删除输出目录下的所有文件和子目录！
    建议先使用 --dry-run 查看将要删除的内容。
    """
    config = ConfigManager.load()
    if config.standalone:
        click.echo(
            "错误：未检测到 mark2pdf.config.toml，clean 仅支持工作区模式。",
            err=True,
        )
        sys.exit(1)
    output_dir = config.output_dir

    if not output_dir.exists():
        click.echo(f"⚠️  输出目录不存在: {output_dir}")
        return

    # 获取所有 PDF 文件
    contents = [item for item in output_dir.glob("**/*.pdf") if item.is_file()]

    if not contents:
        click.echo(f"✨ 输出目录中没有 PDF 文件: {output_dir}")
        return

    click.echo(f"📁 输出目录: {output_dir}")
    click.echo(f"📦 发现 {len(contents)} 个 PDF 文件")

    # Dry Run 模式
    if dry_run:
        click.echo("\n🔍 [Dry Run] 将要删除以下文件:")
        for item in contents:
            click.echo(f"   - {item.relative_to(output_dir)}")
        click.echo("\n✅ Dry Run 完成，未执行删除操作。")
        return

    # 确认
    if not force:
        click.confirm(
            f"⚠️  确定要删除 {output_dir} 中的 {len(contents)} 个 PDF 文件吗？此操作不可恢复！",
            abort=True,
        )

    # 执行删除
    click.echo("\n🗑️  正在清理 PDF 文件...")
    for item in contents:
        try:
            item.unlink()
            click.echo(f"   已删除: {item.relative_to(output_dir)}")
        except Exception as e:
            click.echo(f"   ❌ 删除失败 {item.name}: {e}", err=True)

    click.echo("\n✨ 清理完成！")
