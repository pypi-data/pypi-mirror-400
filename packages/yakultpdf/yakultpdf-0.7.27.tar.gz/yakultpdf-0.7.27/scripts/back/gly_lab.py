# /// script
# dependencies = [
#     "click>=8.0.0",
# ]
# ///

"""
Gly - Glossary Processing Script

处理 glossary-example.md 文件，添加 oneliner 标签并生成 PDF
"""

import shutil
from pathlib import Path

import click

# 导入 md2pdf 相关函数
from md2pdf import (
    check_pandoc_typst,
    run_pandoc_typst,
)

# 导入 markdown 预处理模块
from helper_markdown import pre_add_line_breaks
from helper_workingpath import get_project_root

# 配置设置
DEFAULT_TEMPLATE = "letter-oneliner.typ"


def add_oneliner_tags(content: str, verbose: bool = False) -> str:
    """
    为每个一级标题后的 oneliner 添加标签

    处理规则：
    1. 找到一级标题行（以 # 开头，后面跟着空格）
    2. 找到标题后的第一个非空行（oneliner）
    3. 为 oneliner 添加 :::{#oneliner} 标签

    Args:
        content: 原始内容
        verbose: 是否显示详细信息

    Returns:
        处理后的内容
    """
    lines = content.split("\n")
    processed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        processed_lines.append(line)

        # 检查是否是一级标题行（以 # 开头，后面跟着空格）
        stripped_line = line.strip()
        if stripped_line.startswith("# ") and not stripped_line.startswith("##"):
            # 跳过空行，找到第一个非空行（oneliner）
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                processed_lines.append(lines[j])
                j += 1

            # 如果找到非空行，且不是下一个标题
            if j < len(lines) and not lines[j].strip().startswith("#"):
                oneliner_line = lines[j]

                # 添加 oneliner 标签
                processed_lines.append(":::{#oneliner}")
                processed_lines.append(oneliner_line)
                processed_lines.append(":::")

                if verbose:
                    click.echo(f"  ✓ 为一级标题 '{stripped_line}' 添加 oneliner 标签")

                # 跳过已处理的 oneliner 行
                i = j
            else:
                # 没有找到 oneliner，继续正常处理
                pass

        i += 1

    return "\n".join(processed_lines)


def add_termpage_containers(content: str, verbose: bool = False) -> str:
    """
    为每个一级标题及其 oneliner 添加 termpage 容器

    处理规则：
    1. 找到每个一级标题（以 # 开头，后面跟着空格）
    2. 找到该一级标题对应的 oneliner 部分（直到 oneliner 容器结束）
    3. 用 ::::::{#termpage}...:::::: 包裹标题和 oneliner 部分

    Args:
        content: 原始内容
        verbose: 是否显示详细信息

    Returns:
        处理后的内容
    """
    lines = content.split("\n")
    processed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # 检查是否是一级标题行
        stripped_line = line.strip()
        if stripped_line.startswith("# ") and not stripped_line.startswith("##"):
            if verbose:
                click.echo(f"  ✓ 发现一级标题：'{stripped_line}'")

            # 添加 termpage 容器开始标记
            processed_lines.append("::::::{#termpage}")

            # 添加当前标题行
            processed_lines.append(line)

            # 收集该标题下的 oneliner 部分（直到 oneliner 容器结束）
            j = i + 1
            found_oneliner = False
            while j < len(lines):
                next_line = lines[j]
                next_stripped = next_line.strip()

                # 如果遇到下一个一级标题，停止收集
                if next_stripped.startswith("# ") and not next_stripped.startswith("##"):
                    break

                # 添加当前行
                processed_lines.append(next_line)

                # 检查是否是 oneliner 容器结束标记
                if next_stripped == ":::":
                    # 检查前一行是否是 oneliner 内容
                    if j > 0 and lines[j - 1].strip() != ":::{#oneliner}":
                        found_oneliner = True
                        j += 1
                        break

                j += 1

            # 如果找到了 oneliner，添加 termpage 容器结束标记
            if found_oneliner:
                processed_lines.append("::::::")
                processed_lines.append("")  # 添加空行分隔
            else:
                # 如果没有找到 oneliner，移除已添加的 termpage 开始标记和标题行
                processed_lines = processed_lines[: -(j - i)]
                # 重新添加原始内容
                for k in range(i, j):
                    processed_lines.append(lines[k])

            # 更新索引到下一个标题的开始位置
            i = j - 1  # -1 因为循环末尾会 i += 1
        else:
            # 如果不是一级标题，直接添加（处理文件开头可能有的内容）
            processed_lines.append(line)

        i += 1

    return "\n".join(processed_lines)


def preprocess_glossary_content(content: str, verbose: bool = False) -> str:
    """
    预处理 glossary 内容

    处理步骤：
    1. 使用 pre_add_line_breaks 进行基础清洁
    2. 添加 oneliner 标签
    3. 添加 termpage 容器

    Args:
        content: 原始内容
        verbose: 是否显示详细信息

    Returns:
        预处理后的内容
    """
    if verbose:
        click.echo("开始预处理 glossary 内容...")

    # 第一步：使用 pre_add_line_breaks 进行基础清洁
    processed = pre_add_line_breaks(content, verbose)

    # 第二步：添加 oneliner 标签
    processed = add_oneliner_tags(processed, verbose)

    # 第三步：添加 termpage 容器
    processed = add_termpage_containers(processed, verbose)

    if verbose:
        click.echo("✓ 预处理完成")

    return processed


def process_glossary_file(
    input_file: str,
    output_file: str = None,
    template: str = DEFAULT_TEMPLATE,
    verbose: bool = False,
    only_pre_md: bool = False,
    to_typ: bool = False,
) -> None:
    """
    处理 glossary 文件并生成 PDF 或 typst 文件

    Args:
        input_file: 输入文件名（在 _working/in 目录中）
        output_file: 输出文件名（可选）
        template: 模板文件名
        verbose: 是否显示详细信息
        only_pre_md: 是否只进行 markdown 预处理
        to_typ: 是否输出 typst 文件而不是 PDF
    """
    try:
        # 获取项目根目录
        root_dir = get_project_root()

        # 构建输入文件路径
        in_dir = root_dir / "_working" / "in"
        in_path = in_dir / input_file

        # 验证输入文件是否存在
        if not in_path.exists():
            raise FileNotFoundError(f"找不到输入文件 '{in_path}'")

        if verbose:
            click.echo(f"输入文件：{in_path}")

        # 读取输入文件
        with open(in_path, encoding="utf-8") as f:
            content = f.read()

        if verbose:
            click.echo(f"读取文件成功，内容长度：{len(content)} 字符")

        # 预处理内容
        processed_content = preprocess_glossary_content(content, verbose)

        # 准备预处理文件路径（在 _working/in 目录中）
        if output_file:
            # 使用自定义输出文件名
            processed_filename = Path(output_file).stem + "_processed.md"
        else:
            # 使用输入文件名 + _processed
            processed_filename = Path(input_file).stem + "_processed.md"

        processed_path = in_dir / processed_filename

        # 写入预处理后的文件
        with open(processed_path, "w", encoding="utf-8") as f:
            f.write(processed_content)

        if verbose:
            click.echo(f"✓ 预处理文件已保存：{processed_path}")

        # 如果只进行 markdown 预处理，则直接结束
        if only_pre_md:
            click.echo("✅ Markdown 预处理完成！")
            click.echo(f"预处理文件：{processed_path}")
            return

        # 检查 pandoc 和 typst 是否安装
        check_pandoc_typst()

        # 解析模板路径
        template_dir = root_dir / "template"
        template_path = str(template_dir / template)

        # 验证模板文件是否存在
        if not Path(template_path).exists():
            raise FileNotFoundError(f"模板文件不存在：{template_path}")

        if verbose:
            click.echo(f"使用模板：{template_path}")

        # 准备输出路径（在 _working/out 目录中）
        out_dir = root_dir / "_working" / "out"
        out_dir.mkdir(parents=True, exist_ok=True)

        # 根据输出类型确定文件扩展名
        if to_typ:
            file_extension = ".typ"
        else:
            file_extension = ".pdf"

        if output_file:
            # 使用自定义输出文件名
            output_filename = output_file + file_extension
        else:
            # 使用输入文件名
            output_filename = Path(input_file).stem + file_extension

        output_path = out_dir / output_filename

        # 运行 pandoc 转换（使用 _working/in 作为工作目录）
        # 注意：run_pandoc_typst 会在工作目录中生成文件
        # 我们需要将文件移动到正确的输出目录

        # 先在工作目录中生成文件
        temp_output_path = in_dir / output_filename

        run_pandoc_typst(
            filename=str(processed_path.name),  # 相对于工作目录的文件名
            output_path=str(output_filename),  # 相对于工作目录的输出文件名
            template_path=template_path,
            pandoc_workdir=str(in_dir),  # 工作目录为 _working/in
            verbose=verbose,
        )

        # 将文件移动到输出目录
        if temp_output_path.exists():
            shutil.move(str(temp_output_path), str(output_path))
            if verbose:
                click.echo(f"✓ 输出文件已移动到：{output_path}")
        else:
            raise FileNotFoundError(f"输出文件未生成：{temp_output_path}")

        click.echo("✅ 处理完成！")
        click.echo(f"预处理文件：{processed_path}")
        click.echo(f"输出文件：{output_path}")

    except FileNotFoundError as e:
        click.echo(f"❌ 文件未找到：{e}", err=True)
        raise click.Abort()
    except ValueError as e:
        click.echo(f"❌ 参数错误：{e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ 处理失败：{e}", err=True)
        raise click.Abort()


@click.command()
@click.argument("input_file", required=True)
@click.option(
    "--output",
    "-o",
    help="输出文件名（可选，默认使用输入文件名，预处理文件会添加 _processed 后缀）",
)
@click.option(
    "--template",
    "-t",
    default=DEFAULT_TEMPLATE,
    help=f"模板文件名（默认：{DEFAULT_TEMPLATE}）",
)
@click.option("--verbose", "-v", is_flag=True, help="显示详细的操作信息")
@click.option("--only-pre-md", is_flag=True, help="只进行 markdown 预处理，完成后结束")
@click.option("--to-typ", is_flag=True, help="输出 typst 文件而不是 PDF")
def cli(
    input_file: str,
    output: str,
    template: str,
    verbose: bool,
    only_pre_md: bool,
    to_typ: bool,
) -> None:
    """
    Gly - Glossary Processing Script

    处理指定的 Markdown 文件，添加 oneliner 标签并生成 PDF 或 typst 文件

    INPUT_FILE: 要处理的 Markdown 文件名（位于 _working/in 目录中）
    """
    if verbose:
        click.echo("=== Gly Glossary Processor ===")
        click.echo(f"项目根目录：{get_project_root()}")

    process_glossary_file(input_file, output, template, verbose, only_pre_md, to_typ)


if __name__ == "__main__":
    cli()
