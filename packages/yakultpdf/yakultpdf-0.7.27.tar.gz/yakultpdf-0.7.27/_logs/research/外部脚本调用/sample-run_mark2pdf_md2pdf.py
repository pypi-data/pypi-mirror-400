# /// script
# dependencies = ["click"]
# ///

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import click

VERSION = "最后更新：2025.12.04(v1.2)"

# 目标 md2pdf 仓库与脚本位置
MARK2PDF_DIR = Path("/Users/fangjun/python/mark2pdf")
MARK2PDF_SCRIPT = MARK2PDF_DIR / "scripts/md2pdf.py"
MARK2PDF_WORKING_IN = MARK2PDF_DIR / "_working/in"
MARK2PDF_WORKING_OUT = MARK2PDF_DIR / "_working/out"

# 本地输入/输出目录（可通过 --input-dir 覆盖）
LOCAL_INPUT_DIR = Path("_l2points")


def _format_json_quiz(body: str) -> str | None:
    """
    将 json block 按题干/选项/答案/解析/知识点格式化为带 > 的分段文本。
    返回 None 表示解析失败，调用方可回退为原始逐行引用。
    """
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return None

    question = data.get("question") or data.get("queston") or ""
    options = data.get("options") or []
    answer = data.get("answer")
    explanation = data.get("explanation")
    knowledge_point = data.get("knowledge_point") or data.get("知识点")

    lines: list[str] = []

    if question:
        lines.append(f"> {question}")

    if question and options:
        lines.append(">")

    if options:
        for idx, opt in enumerate(options):
            label = chr(ord("A") + idx)
            opt_lines = str(opt).splitlines() or [""]
            lines.append(f"> - {label}. {opt_lines[0]}")
            for cont in opt_lines[1:]:
                # 续行缩进，维持列表结构
                lines.append(f">   {cont}")

    if answer:
        lines.append(">")
        lines.append(f"> 答案：{answer}")

    if explanation:
        lines.append(">")
        lines.append(f"> 解析：{explanation}")

    if knowledge_point:
        lines.append(">")
        lines.append(f"> 知识点：{knowledge_point}")

    return "\n".join(lines) if lines else None


def convert_json_fences_to_blockquote(content: str) -> str:
    """
    将 ```json fenced block 转成带 > 的普通 Markdown 文本。
    若 json 解析失败，则退回逐行引用。
    """
    pattern = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)

    def _repl(match: re.Match) -> str:
        body = match.group(1)
        formatted = _format_json_quiz(body)
        if formatted:
            return formatted
        # 回退：逐行添加 >
        lines = body.splitlines()
        quoted = [">" if line.strip() == "" else f"> {line}" for line in lines]
        return "\n".join(quoted)

    return pattern.sub(_repl, content)


def ensure_toc_frontmatter(content: str, toc_value: str = "2", header: str = VERSION) -> str:
    """
    确保文档头部包含 toc-depth frontmatter。
    - 已有 frontmatter 且缺少 toc-depth 时，追加该字段
    - 无 frontmatter 时，创建新的 frontmatter
    """
    fm_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    m = fm_pattern.match(content)
    if m:
        fm_body = m.group(1)
        if re.search(r"^toc-depth\s*:", fm_body, re.MULTILINE):
            return content
        new_fm = f"{fm_body}\ntoc-depth: {toc_value}"
        return f"---\n{new_fm}\n---\n" + content[m.end() :]
    else:
        return f"---\ntoc-depth: {toc_value}\ntitle: '{header}'\n---\n\n{content}"


def parse_output_arg(extra_args: list[str]) -> str | None:
    """从透传参数中解析 --output"""
    for idx, arg in enumerate(extra_args):
        if arg == "--output" and idx + 1 < len(extra_args):
            return extra_args[idx + 1]
        if arg.startswith("--output="):
            return arg.split("=", 1)[1]
    return None


def strip_output_arg(extra_args: list[str]) -> list[str]:
    """移除 --output 相关参数，避免重复传递"""
    cleaned: list[str] = []
    skip_next = False
    for arg in extra_args:
        if skip_next:
            skip_next = False
            continue
        if arg == "--output":
            skip_next = True
            continue
        if arg.startswith("--output="):
            continue
        cleaned.append(arg)
    return cleaned


def extract_first_title(content: str) -> str | None:
    """
    获取文档中的第一个一级标题文本（跳过 frontmatter），找不到则返回 None。
    """
    fm_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    m = fm_pattern.match(content)
    search_body = content[m.end() :] if m else content
    title_match = re.search(r"^\s*#\s+(.+?)\s*$", search_body, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    if m:
        try:
            import yaml

            fm_data = yaml.safe_load(m.group(1)) or {}
            fm_title = fm_data.get("title")
            if isinstance(fm_title, str) and fm_title.strip():
                return fm_title.strip()
        except Exception:
            return None
    return None


def sanitize_filename(name: str) -> str:
    """清理非法文件名字符，确保可作为文件名使用"""
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name).strip()
    return cleaned or "output"


def find_output_file(
    ext: str, start_ts: float, input_stem: str, content: str, extra_args: list[str]
) -> Path | None:
    """
    根据输入文件与参数推测输出，并兜底用时间戳查找最新生成的文件
    ext: pdf 或 typ（不带点）
    """
    output_arg = parse_output_arg(extra_args)
    tc_enabled = "--tc" in extra_args

    # 从 frontmatter 里尝试读取 exportFilename
    export_name = None
    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n"
    fm_match = re.match(frontmatter_pattern, content, re.DOTALL)
    if fm_match:
        try:
            import yaml

            frontmatter = yaml.safe_load(fm_match.group(1)) or {}
            export_name = frontmatter.get("exportFilename")
        except Exception:
            export_name = None

    # 构建候选文件名（有前者优先）
    candidate_names = []
    if export_name:
        candidate_names.append(export_name)
        # 如果 tc 开启，尝试追加繁体版本（忽略失败）
        if tc_enabled:
            try:
                from opencc import OpenCC

                cc = OpenCC("s2t")
                tc_name = cc.convert(export_name)
                if tc_name != export_name:
                    candidate_names.insert(0, tc_name)
            except Exception:
                pass
    if output_arg:
        candidate_names.append(output_arg)
    candidate_names.append(input_stem)

    for name in candidate_names:
        path = MARK2PDF_WORKING_OUT / f"{name}.{ext}"
        if path.exists() and path.stat().st_mtime >= start_ts:
            return path

    # 兜底：找运行后生成/更新的最新同扩展名文件
    candidates = [p for p in MARK2PDF_WORKING_OUT.glob(f"*.{ext}") if p.stat().st_mtime >= start_ts]
    if candidates:
        return max(candidates, key=lambda p: p.stat().st_mtime)
    return None


@click.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument("files", nargs=-1)
@click.option(
    "--input-dir",
    default=str(LOCAL_INPUT_DIR),
    show_default=True,
    help="包含原始 md 的目录（默认处理其中全部 .md）",
)
@click.option(
    "--header",
    default=VERSION,
    show_default=True,
    help="创建缺省 frontmatter 时使用的标题",
)
@click.option(
    "--zhname", is_flag=True, help="使用 md 的第一个标题作为输出名（传递给 mark2pdf 的 --output）"
)
@click.option("--no-cleanup", is_flag=True, help="保留 mark2pdf/_working 下的输入/输出文件")
@click.option("--verbose", is_flag=True, help="显示详细信息")
@click.pass_context
def cli(
    ctx,
    files: tuple[str],
    input_dir: str,
    header: str,
    zhname: bool,
    no_cleanup: bool,
    verbose: bool,
):
    """
    预处理 _logs/考题考点分析 下的 Markdown，将 ```json code block 转成带 > 的文本，
    再调用 /Users/fangjun/python/mark2pdf/scripts/md2pdf.py 生成 pdf。
    """
    if not MARK2PDF_SCRIPT.exists():
        click.echo(f"错误：找不到目标脚本 {MARK2PDF_SCRIPT}", err=True)
        raise SystemExit(1)

    src_dir = Path(input_dir)
    if not src_dir.exists():
        click.echo(f"错误：输入目录不存在：{src_dir}", err=True)
        raise SystemExit(1)

    tmp_dir = src_dir / "tmp"
    pdf_dir = src_dir / "pdf"

    tmp_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    MARK2PDF_WORKING_IN.mkdir(parents=True, exist_ok=True)
    MARK2PDF_WORKING_OUT.mkdir(parents=True, exist_ok=True)

    # 需要处理的文件列表
    if files:
        targets = []
        for f in files:
            p = Path(f)
            if not p.is_absolute():
                p = src_dir / f
            targets.append(p)
    else:
        targets = sorted(src_dir.glob("*.md"))

    if not targets:
        click.echo("未找到需要处理的 Markdown 文件", err=True)
        raise SystemExit(1)

    extra_args = list(ctx.args)
    ext = "typ" if "--to-typst" in extra_args else "pdf"
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)

    for md_file in targets:
        if not md_file.exists() or not md_file.is_file():
            click.echo(f"跳过：未找到文件 {md_file}", err=True)
            continue

        if verbose:
            click.echo(f"\n处理 {md_file} ...")

        content = md_file.read_text(encoding="utf-8")
        zh_output = None
        if zhname:
            first_title = extract_first_title(content)
            if not first_title and verbose:
                click.echo("未找到标题，回退使用文件名作为输出名")
            output_candidate = first_title or md_file.stem
            zh_output = sanitize_filename(output_candidate)

        processed = convert_json_fences_to_blockquote(content)
        processed = ensure_toc_frontmatter(processed, header=header)

        tmp_path = tmp_dir / md_file.name
        tmp_path.write_text(processed, encoding="utf-8")
        if verbose:
            click.echo(f"已写入预处理文件：{tmp_path}")

        target_in = MARK2PDF_WORKING_IN / md_file.name
        shutil.copy2(tmp_path, target_in)
        if verbose:
            click.echo(f"复制到 mark2pdf/_working/in：{target_in}")

        cmd_extra_args = extra_args.copy()
        if zh_output:
            cmd_extra_args = strip_output_arg(cmd_extra_args)
            cmd_extra_args = ["--output", zh_output] + cmd_extra_args

        cmd = ["uv", "run", "scripts/md2pdf.py", md_file.name] + cmd_extra_args
        if verbose:
            click.echo(f"执行命令: {' '.join(cmd)}")

        start_ts = time.time()
        result = subprocess.run(cmd, cwd=MARK2PDF_DIR, env=env, check=False)
        if result.returncode != 0:
            click.echo(f"转换失败（返回码 {result.returncode}）：{md_file.name}", err=True)
            if not no_cleanup and target_in.exists():
                target_in.unlink()
            continue

        out_file = find_output_file(ext, start_ts, md_file.stem, processed, cmd_extra_args)
        if not out_file:
            click.echo("警告：未找到输出文件", err=True)
        else:
            dest = pdf_dir / out_file.name
            shutil.copy2(out_file, dest)
            click.echo(f"输出已保存：{dest}")

        if not no_cleanup:
            if target_in.exists():
                target_in.unlink()
            if out_file and out_file.exists():
                out_file.unlink()


if __name__ == "__main__":
    cli()
