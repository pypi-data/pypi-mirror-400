"""
Typst 辅助模块

提供 Typst 相关的处理功能，包括模板依赖解析、路径解析等。
参考 mark2pdf.helper_workingpath 和 mark2pdf.helper_markdown 的设计模式。
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

_TOOL_CHECKED = False
_SKIP_TOOL_CHECK = False

# 已废弃的函数：parse_template_deps, parse_template_assets, copy_template_deps, cleanup_template_deps
# 现在使用目录式模板简化逻辑，直接复制整个目录。


def set_tool_check_skip(skip: bool) -> None:
    global _SKIP_TOOL_CHECK
    _SKIP_TOOL_CHECK = bool(skip)


def run_pandoc_typst(
    input_file: str,
    output_file: str,
    template_path: str,
    pandoc_workdir: str,
    verbose: bool = False,
    to_typst: bool = False,
    font_paths: list[str] | None = None,
    **kwargs,
) -> bool:
    """
    运行 pandoc 命令将 markdown 转换为 PDF 或 typst
    其中关键是模板依赖管理
    通用的 pandoc 执行函数，支持灵活的额外参数

    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        template_path (str): 模板文件路径（原始模板路径，用于解析依赖）
        pandoc_workdir (str): pandoc 工作目录
        verbose (bool): 是否显示详细信息
        to_typst (bool): 是否输出 typst 文件而不是 PDF
        font_paths (list[str] | None): 额外字体目录列表
        **kwargs: 额外的 pandoc 参数，例如：
            - with_pagenumber: bool - 是否显示页码
            - coverimg: str - 封面图片路径
            - 其他任意传递给 pandoc 变量参数

    Returns:
        bool: 转换是否成功

    Raises:
        subprocess.CalledProcessError: 如果 pandoc 执行失败
        FileNotFoundError: 如果输出文件未能生成

    路径使用规范说明：
    ==================
    为了避免 pandoc 工作目录导致的路径解析错误，建议按以下规范传递路径：

    1. input_file: 使用相对路径（相对于 pandoc_workdir）
       - 正确：merged_file.name 或 "input.md"
       - 错误："/absolute/path/to/input.md" 或 "../input.md"

    2. output_file: 使用绝对路径
       - 正确：str(pdf_path.absolute())
       - 错误：相对路径如 "out/output.pdf"

    3. template_path: 原始模板路径（用于解析依赖），实际使用工作目录中的模板
       - 传入：resolve_template_path(template) 返回的绝对路径
       - 实际使用：工作目录中的模板文件名

    4. pandoc_workdir: 使用相对路径
       - 正确：str(input_file.parent) 或 "in/subdir"
       - 错误：绝对路径

    原因：pandoc 在指定的工作目录下执行，模板依赖已经拷贝到工作目录，
    使用相对路径的模板文件名即可。
    """

    # 如果是 typst 输出，修改输出文件扩展名
    if to_typst:
        output_file = Path(output_file).with_suffix(".typ")

    template_file = Path(template_path)
    workdir_path = Path(pandoc_workdir)

    # 判断是否为目录式模板（模板文件在子目录中，如 nb/nb.typ）
    is_dir_template = template_file.parent.name == template_file.stem

    # 记录需要清理的文件/目录列表
    cleanup_items = []

    if is_dir_template:
        # 目录式模板：将目录内容平铺复制到工作目录根目录
        # 这样 #import "./lib.typ" 才能正确找到文件（因为 pandoc 生成的文件在根目录）
        template_dir = template_file.parent
        template_filename = template_file.name  # 使用平铺后的文件名

        if verbose:
            print(f"目录式模板：{template_path}")
            print(f"平铺复制模板目录内容：{template_dir.name}/ -> ./")

        # 复制目录内容到工作目录
        for item in template_dir.iterdir():
            if item.name.startswith("."):  # 跳过隐藏文件
                continue

            src = item
            dst = workdir_path / item.name

            # 如果目标已存在（且不是目录），先清理（或者是覆盖？）
            # 这里简单处理：如果已存在则跳过？或者覆盖？
            # 考虑到沙箱环境，应该可以直接覆盖或复制

            if item.is_dir():
                # 如果是目录，复制目录（如 images/）
                # 注意：如果工作目录已有同名目录，copytree 默认会报错，需要 dirs_exist_ok=True
                if dst.exists() and dst.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                elif not dst.exists():
                    shutil.copytree(src, dst)
                    cleanup_items.append(dst)  # 记录以便清理（仅当这是新创建的）
                else:
                    # 目标存在且是文件，无法覆盖为目录，跳过
                    if verbose:
                        print(f"  ⚠️ 跳过复制目录（目标已存在文件）：{item.name}")
            else:
                # 是文件，直接复制
                shutil.copy2(src, dst)
                if not (workdir_path / item.name).exists():  # 如果之前不存在，记录清理
                    pass  # 难以判断之前是否存在，统统记录？
                cleanup_items.append(dst)

    else:
        # 单文件模板：仅复制模板文件本身

        template_filename = template_file.name
        if verbose:
            print(f"单文件模板：{template_path}")

        target_template = workdir_path / template_filename
        shutil.copy2(template_file, target_template)
        cleanup_items.append(target_template)

    if verbose:
        print(f"使用模板文件：{template_filename}")

    # 构建基础的 pandoc 命令
    cmd = [
        "pandoc",
        input_file,
        f"--template={template_filename}",
        "--pdf-engine=typst",
        "--wrap=none",
        "-o",
        str(output_file),
    ]

    _add_font_paths(cmd, font_paths, pandoc_workdir, verbose)
    _add_pandoc_arguments(cmd, kwargs)

    try:
        # 执行 pandoc 命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=pandoc_workdir,
        )

        # 检查执行结果
        if result.returncode != 0:
            if verbose:
                print(f"pandoc 执行失败：{result.stderr}")
            return False

        # 检查输出文件是否生成
        if not Path(output_file).exists():
            if verbose:
                print(f"输出文件未能生成：{output_file}")
            return False

        # 清理模板文件（仅在成功时清理）
        # 注意：平铺复制很难精确清理（因为可能覆盖了同名文件），
        # 但在沙箱环境中，全部清理沙箱由调用者负责。
        # 这里尝试清理我们复制进去的文件。
        for item in cleanup_items:
            try:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                elif item.exists():
                    item.unlink()
            except Exception:
                pass

        if verbose:
            print("  ✓ 清理临时模板文件")

        try:
            rel_output = os.path.relpath(output_file)
        except ValueError:
            rel_output = output_file
        print(f"⚡️ 转换成功：{rel_output}")

        return True

    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"pandoc 执行失败：{e}")
            if e.stderr:
                print(f"错误信息：{e.stderr}")
        return False
    except Exception as e:
        if verbose:
            print(f"转换过程中出错：{e}")
        return False


def _add_pandoc_arguments(cmd: list, kwargs: dict):
    """
    根据 kwargs 参数添加 pandoc 命令行参数

    Args:
        cmd (list): 要修改的命令列表
        kwargs (dict): 额外的参数
    """
    # 将所有参数转换为 --var=value 格式
    for key, value in kwargs.items():
        if value is not None:
            # 将下划线转换为连字符
            var_name = key.replace("_", "-")
            # 处理布尔值，转换为小写字符串
            if isinstance(value, bool):
                value = str(value).lower()
            cmd.extend(["-V", f"{var_name}={value}"])


def _add_font_paths(
    cmd: list,
    font_paths: list[str] | tuple[str, ...] | str | None,
    base_dir: str | Path,
    verbose: bool = False,
) -> None:
    """
    为 pandoc 命令添加 Typst 字体路径

    Args:
        cmd (list): 要修改的命令列表
        font_paths: 字体路径列表或单个路径
        base_dir: 相对路径的基准目录（pandoc 工作目录）
        verbose (bool): 是否显示详细信息
    """
    if not font_paths:
        return

    if isinstance(font_paths, str | Path):
        font_paths = [str(font_paths)]

    base_path = Path(base_dir)
    seen = set()

    for font_path in font_paths:
        if not font_path:
            continue
        expanded = os.path.expandvars(str(font_path))
        candidate = Path(expanded).expanduser()
        if not candidate.is_absolute():
            candidate = base_path / candidate
        candidate_str = str(candidate)
        if candidate_str in seen:
            continue
        if not candidate.exists():
            if verbose:
                print(f"  ⚠️ 字体目录不存在，已跳过: {candidate_str}")
            continue
        if not candidate.is_dir():
            if verbose:
                print(f"  ⚠️ 字体路径不是目录，已跳过: {candidate_str}")
            continue
        cmd.extend(["--pdf-engine-opt", f"--font-path={candidate_str}"])
        seen.add(candidate_str)


def check_pandoc_typst(skip: bool | None = None):
    """
    检查 pandoc 和 typst 是否已安装

    Raises:
        SystemExit: 如果任一工具未安装
    """
    global _TOOL_CHECKED
    if skip is None:
        skip = _SKIP_TOOL_CHECK
    if skip or _TOOL_CHECKED:
        return

    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        print("错误：pandoc 未安装或不在 PATH 中，请先安装 pandoc")
        sys.exit(1)

    try:
        subprocess.run(["typst", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        print("错误：typst 未安装或不在 PATH 中，请先安装 typst")
        sys.exit(1)

    _TOOL_CHECKED = True
