"""
mark2pdf.core 内部工具函数

提供包内共享的辅助函数。
"""

import re
import subprocess
from pathlib import Path

import yaml

from mark2pdf.helper_markdown import (
    extract_frontmatter,
    pre_add_line_breaks,
    pre_for_typst,
    pre_remove_links,
)
from mark2pdf.helper_utils import convert_to_traditional


def merge_frontmatter(base: dict | None, override: dict | None) -> dict:
    """
    深度合并 frontmatter 字典，override 覆盖 base。

    仅对 dict 类型的值递归合并，其余类型直接覆盖。
    """
    if not base and not override:
        return {}
    if not base:
        return dict(override or {})
    if not override:
        return dict(base or {})

    merged = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_frontmatter(merged[key], value)
        else:
            merged[key] = value
    return merged


def inject_default_frontmatter(content: str, default_fm: dict, verbose: bool = False) -> str:
    """
    注入默认 frontmatter，不覆盖已有字段

    参数：
        content: markdown 文件内容
        default_fm: 默认 frontmatter 字典
        verbose: 是否显示详细信息

    返回：
        注入后的内容
    """
    if not default_fm:
        return content

    # 解析现有 frontmatter
    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if match:
        existing_fm_str = match.group(1)
        try:
            existing_fm = yaml.safe_load(existing_fm_str) or {}
        except yaml.YAMLError:
            existing_fm = {}
        body = content[match.end() :]
    else:
        existing_fm = {}
        body = content

    # 合并：默认值 + 现有值（现有值优先），支持嵌套字典
    merged_fm = merge_frontmatter(default_fm, existing_fm)
    new_fm_str = yaml.dump(merged_fm, allow_unicode=True, default_flow_style=False)

    if verbose:
        print(f"注入默认 frontmatter: {list(default_fm.keys())}")

    return f"---\n{new_fm_str}---\n\n{body}"


def get_output_filename(
    content: str,
    default_output_path: Path,
    tc: bool,
    verbose: bool,
    force_filename: bool = False,
    frontmatter: dict | None = None,
) -> Path:
    """
    从 frontmatter 中提取输出文件名：exportFilename > title > 默认值

    参数:
        content: markdown 文件内容
        default_output_path: 默认输出路径
        tc: 是否转换为繁体中文
        verbose: 是否显示详细信息
        force_filename: 是否强制使用默认文件名（忽略 exportFilename）
        frontmatter: 预先解析的 frontmatter（可选，用于复用解析结果）

    返回:
        最终的输出路径
    """
    if frontmatter is None:
        frontmatter = extract_frontmatter(content)

    if force_filename:
        if verbose and (frontmatter.get("exportFilename") or frontmatter.get("title")):
            print("  ⚠️ 已启用强制文件名，忽略 exportFilename 和 title 配置")
        return default_output_path

    if frontmatter.get("exportFilename"):
        original_filename = frontmatter["exportFilename"]

        # 安全性检查：防止路径穿越攻击
        # 1. 先检查原始输入是否包含可疑内容
        if ".." in original_filename or original_filename.startswith(("/", "\\")):
            if verbose:
                print(
                    f"警告：exportFilename 包含不安全字符，已忽略: {original_filename}"
                )
            return default_output_path

        # 2. 只保留文件名部分（去除路径）
        export_filename = Path(original_filename).name

        # 3. 验证提取后的文件名有效
        if not export_filename or export_filename in (".", ".."):
            if verbose:
                print(f"警告：exportFilename 无效，已忽略: {original_filename}")
            return default_output_path

        if tc:
            export_filename = convert_to_traditional(export_filename)

        export_path = Path(export_filename)
        if not export_path.suffix:
            default_suffix = default_output_path.suffix or ".pdf"
            base_name = export_path.name.rstrip(".")
            if not base_name:
                base_name = export_path.name
            export_filename = f"{base_name}{default_suffix}"

        output_path = Path(default_output_path).parent / export_filename

        if verbose:
            print(f"使用 frontmatter 中的输出文件名：{export_filename}")

        return output_path

    title = frontmatter.get("title")
    if title:
        title_text = str(title).strip()
        if tc:
            title_text = convert_to_traditional(title_text)
        safe_title = re.sub(r"[^\w]", "", title_text)
        if safe_title:
            output_path = default_output_path.parent / f"{safe_title}{default_output_path.suffix}"
            if verbose:
                print(f"使用 frontmatter title 作为输出文件名：{safe_title}")
            return output_path

    return default_output_path


def apply_default_preprocessing(
    content: str,
    removelink: bool = False,
    verbose: bool = False,
) -> str:
    """
    应用默认预处理链

    执行顺序：
    1. pre_remove_links（可选，当 removelink=True）
    2. pre_add_line_breaks
    3. pre_for_typst

    参数：
        content: Markdown 内容
        removelink: 是否移除链接（保留图片）
        verbose: 是否显示详细信息

    返回：
        预处理后的内容
    """
    if removelink:
        content = pre_remove_links(content, verbose=verbose)

    content = pre_add_line_breaks(content, verbose=verbose)
    content = pre_for_typst(content, verbose=verbose)

    return content


def open_with_system(filepath: Path, verbose: bool = False) -> bool:
    """
    使用系统默认程序打开文件

    参数：
        filepath: 文件路径
        verbose: 是否显示详细信息

    返回：
        成功返回 True，失败返回 False
    """
    if not filepath.exists():
        print(f"文件不存在：{filepath}")
        return False

    try:
        # macOS 使用 open 命令
        subprocess.run(["open", str(filepath)], check=True)
        if verbose:
            print(f"已打开文件：{filepath}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打开文件失败：{e}")
        return False
