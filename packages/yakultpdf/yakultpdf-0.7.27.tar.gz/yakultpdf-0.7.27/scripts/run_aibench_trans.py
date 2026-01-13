# /// script
# dependencies = ["click"]
# ///

import os
import shutil
import subprocess
import sys
from pathlib import Path

import click

# ========== 常量定义 ==========
AIBENCH_DIR = Path("/Users/fangjun/aibench")
AIBENCH_SCRIPT = AIBENCH_DIR / "scripts/trans.py"
AIBENCH_WORKING_IN = AIBENCH_DIR / "_working/in"
AIBENCH_WORKING_OUT = AIBENCH_DIR / "_working/out"

# 本地工作目录
LOCAL_WORKING_IN = Path("_working/in")


def copy_to_working_in(local_input: Path) -> Path:
    """将本地输入文件复制到 aibench/_working/in/ 目录"""
    AIBENCH_WORKING_IN.mkdir(parents=True, exist_ok=True)
    aibench_input = AIBENCH_WORKING_IN / local_input.name

    click.echo(f"复制输入文件: {local_input} -> {aibench_input}")
    shutil.copy2(local_input, aibench_input)

    return aibench_input


def copy_from_working_out(local_input: Path) -> Path:
    """从 aibench/_working/out/ 目录复制输出文件回本地的 _working/in，文件名为 {原文件名}_zh.md"""
    input_stem = local_input.stem
    aibench_output = AIBENCH_WORKING_OUT / local_input.name

    # 确保本地 _working/in 目录存在
    LOCAL_WORKING_IN.mkdir(parents=True, exist_ok=True)

    # 本地输出文件名：{原文件名}_zh.md
    local_output = LOCAL_WORKING_IN / f"{input_stem}_zh.md"

    # 复制输出文件回本地
    if aibench_output.exists():
        click.echo(f"\n复制输出文件: {aibench_output} -> {local_output}")
        shutil.copy2(aibench_output, local_output)
        click.echo(f"✓ 完成！输出文件: {local_output}")
        return local_output
    else:
        click.echo(f"\n警告：未找到输出文件 {local_input.name}", err=True)
        click.echo(f"请检查 {AIBENCH_WORKING_OUT} 目录", err=True)
        return None


def cleanup_working_dirs(input_filename: str):
    """清理 _working/in 和 _working/out 目录中的文件"""
    # 清理 _working/in 中的输入文件
    input_file = AIBENCH_WORKING_IN / input_filename
    if input_file.exists():
        input_file.unlink()
        click.echo(f"清理输入文件: {input_file}")

    # 清理 _working/out 中的输出文件
    output_file = AIBENCH_WORKING_OUT / input_filename
    if output_file.exists():
        output_file.unlink()
        click.echo(f"清理输出文件: {output_file}")


# 允许传递未知选项和额外参数，以便将这些参数转发给底层的 trans.py 脚本
@click.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.option("--no-cleanup", is_flag=True, help="不清理 _working 目录中的临时文件")
@click.pass_context
def cli(ctx, no_cleanup):
    """
    在 aibench 目录中运行 trans.py 脚本的包装器

    自动处理文件复制：
    1. 将本地输入文件复制到 aibench/_working/in/
    2. 在 aibench 运行 trans.py
    3. 将输出文件从 aibench/_working/out/ 复制回本地的 _working/in，命名为 {原文件名}_zh.md
    4. 默认清理 _working 目录中的临时文件（使用 --no-cleanup 禁用）

    示例：
        uv run run_aibench_trans.py input.md
        uv run run_aibench_trans.py input.md --no-cleanup
        uv run run_aibench_trans.py input.md --extra-arg1 --extra-arg2
    """
    if not ctx.args:
        click.echo("错误：需要提供输入文件名作为第一个参数", err=True)
        sys.exit(1)

    # 获取输入文件名（第一个参数）
    input_filename = ctx.args[0]
    local_input = Path(input_filename)

    # 如果输入的文件不存在，尝试在 _working/in/ 目录下查找
    if not local_input.exists():
        # 移除可能存在的 _working/in/ 前缀，然后从 _working/in/ 查找
        if input_filename.startswith("_working/in/"):
            search_path = Path(input_filename)
        else:
            search_path = LOCAL_WORKING_IN / input_filename

        if search_path.exists():
            local_input = search_path
            click.echo(f"在 _working/in/ 目录找到文件: {local_input}")
        else:
            click.echo(f"错误：本地文件 {local_input} 不存在", err=True)
            click.echo(f"在 {LOCAL_WORKING_IN} 目录也未找到该文件", err=True)
            sys.exit(1)

    if not AIBENCH_DIR.exists():
        click.echo(f"错误：目录 {AIBENCH_DIR} 不存在", err=True)
        sys.exit(1)

    if not AIBENCH_SCRIPT.exists():
        click.echo(f"错误：脚本 {AIBENCH_SCRIPT} 不存在", err=True)
        sys.exit(1)

    # 创建 _working/out 目录
    AIBENCH_WORKING_OUT.mkdir(parents=True, exist_ok=True)

    # 复制输入文件到 aibench/_working/in/
    copy_to_working_in(local_input)

    # 构建命令，将文件名作为第一个参数，其余参数原样传递
    cmd = ["uv", "run", "scripts/trans.py", local_input.name] + ctx.args[1:]

    # 复制当前环境变量，并移除 VIRTUAL_ENV 以避免冲突
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)

    try:
        # 在 aibench 目录中执行命令
        click.echo(f"\n执行命令: {' '.join(cmd)}")
        click.echo(f"工作目录: {AIBENCH_DIR}\n")

        result = subprocess.run(cmd, cwd=str(AIBENCH_DIR), env=env, check=False)

        if result.returncode != 0:
            click.echo(f"\n命令执行失败，返回码: {result.returncode}", err=True)
            sys.exit(result.returncode)

        # 复制输出文件回本地
        local_output = copy_from_working_out(local_input)

        # 默认清理临时文件，除非指定了 --no-cleanup
        if not no_cleanup:
            click.echo("\n清理临时文件...")
            cleanup_working_dirs(local_input.name)

        sys.exit(0 if local_output else 1)

    except Exception as e:
        click.echo(f"执行错误：{e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
