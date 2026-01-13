"""
mark2pdf.core 核心 API

提供可编程调用的转换函数，不依赖 CLI。
"""

from collections.abc import Callable
from pathlib import Path

from mark2pdf.helper_interfile.interfile_manager import (
    cleanup_sandbox,
    create_sandbox,
    link_images_dir,
)
from mark2pdf.helper_markdown import extract_frontmatter
from mark2pdf.helper_typst import check_pandoc_typst, run_pandoc_typst
from mark2pdf.helper_workingpath import (
    get_project_root,
    resolve_inout_paths,
    resolve_template_path,
    safesave_path,
)

from .options import ConversionOptions
from .postprocess import ensure_tc_postprocess
from .utils import (
    apply_default_preprocessing,
    get_output_filename,
    inject_default_frontmatter,
)


def _collect_font_paths(config: object | None, template_path: str | None) -> list[str]:
    font_paths: list[Path] = []
    if config is not None:
        try:
            fonts_dir = getattr(config, "fonts_dir", None)
        except Exception:
            fonts_dir = None
        if fonts_dir:
            font_paths.append(Path(fonts_dir))
    else:
        font_paths.append(Path.cwd() / "fonts")

    if template_path:
        font_paths.append(Path(template_path).parent / "fonts")

    return [str(path) for path in font_paths]


_FONT_EXTENSIONS = (".ttf", ".otf", ".ttc", ".otc")
_FONT_NAME_CACHE: dict[str, tuple[float, tuple[str, ...]]] = {}


def _get_cached_font_stems(font_dir: Path) -> tuple[str, ...]:
    try:
        stat = font_dir.stat()
    except FileNotFoundError:
        return ()
    cache_key = str(font_dir.resolve())
    cached = _FONT_NAME_CACHE.get(cache_key)
    if cached and cached[0] == stat.st_mtime:
        return cached[1]

    stems = []
    for font_file in font_dir.rglob("*"):
        if not font_file.is_file():
            continue
        if font_file.suffix.lower() not in _FONT_EXTENSIONS:
            continue
        stems.append(font_file.stem.lower())

    stems_tuple = tuple(stems)
    _FONT_NAME_CACHE[cache_key] = (stat.st_mtime, stems_tuple)
    return stems_tuple


def _font_name_in_dirs(font_name: str, font_paths: list[str]) -> bool:
    needle = font_name.strip().lower()
    if not needle:
        return True
    for font_dir in font_paths:
        dir_path = Path(font_dir)
        if not dir_path.exists() or not dir_path.is_dir():
            continue
        for stem in _get_cached_font_stems(dir_path):
            if needle in stem:
                return True
    return False


def _warn_missing_fonts(
    content: str,
    font_paths: list[str],
    verbose: bool,
    frontmatter: dict | None = None,
) -> None:
    if not verbose:
        return
    if not font_paths:
        return
    if frontmatter is None:
        frontmatter = extract_frontmatter(content)
    if not isinstance(frontmatter, dict):
        frontmatter = {}

    # search in theme group first
    theme = frontmatter.get("theme")
    if isinstance(theme, dict):
        for key in ("font", "titlefont"):
            font_value = theme.get(key)
            if not isinstance(font_value, str):
                continue
            font_name = font_value.strip()
            if not font_name:
                continue
            if _font_name_in_dirs(font_name, font_paths):
                continue
            print(
                f"  ⚠️ 未在字体目录中找到字体 '{font_name}' (theme.{key})，若系统未安装将回退默认字体"
            )


def execute_in_sandbox(
    content: str,
    temp_filename: str,
    output_path: Path,
    images_source_dir: Path,
    tmp_dir: Path,
    sandbox_prefix: str,
    options: ConversionOptions,
    config: object | None = None,
    frontmatter: dict | None = None,
) -> Path | None:
    """
    在沙箱中执行 Pandoc 转换

    流程：
    1. 创建沙箱目录
    2. 链接 images 目录
    3. 写入临时 MD 文件
    4. 调用 Pandoc 转换
    5. 清理沙箱（除非 savemd=True）

    参数：
        content: 预处理后的 Markdown 内容
        temp_filename: 临时文件名（如 "test.md"）
        output_path: 输出文件路径
        images_source_dir: images 目录的来源目录
        tmp_dir: 临时目录路径
        sandbox_prefix: 沙箱目录前缀
        options: 转换配置选项
        config: PdfworkConfig 配置对象（可选）
        frontmatter: 预先解析的 frontmatter（可选，用于复用解析结果）

    返回：
        成功返回输出文件路径 Path，失败返回 None
    """
    sandbox = create_sandbox(tmp_dir, prefix=sandbox_prefix, verbose=options.verbose)

    # 链接 images 目录
    link_images_dir(sandbox, images_source_dir, verbose=options.verbose)

    # 写入临时文件
    temp_path = sandbox / temp_filename
    temp_path.write_text(content, encoding="utf-8")
    if options.verbose:
        print(f"  ✓ 创建临时文件：{temp_path}")

    # 解析模板路径
    template_path = resolve_template_path(options.template, config=config)
    font_paths = _collect_font_paths(config, template_path)
    _warn_missing_fonts(content, font_paths, options.verbose, frontmatter=frontmatter)

    # Pandoc 参数
    pandoc_args = {}
    if options.coverimg:
        pandoc_args["coverimg"] = options.coverimg

    success = False  # 在 try 块之前初始化，防止异常时 finally 中 UnboundLocalError
    try:
        success = run_pandoc_typst(
            input_file=temp_filename,
            output_file=output_path,
            template_path=template_path,
            pandoc_workdir=sandbox,
            verbose=options.verbose,
            to_typst=options.to_typst,
            font_paths=font_paths,
            **pandoc_args,
        )
    finally:
        if options.savemd:
            if options.verbose or success:
                print(f"预处理后的 Markdown 已保存至：{temp_path}")
        else:
            cleanup_sandbox(sandbox, verbose=options.verbose)

    if not success:
        print("转换失败")
        return None

    return output_path


def convert_file(
    input_file: str,
    output_file: str | None = None,
    options: ConversionOptions = ConversionOptions(),
    indir: str | None = None,
    outdir: str | None = None,
    default_frontmatter: dict | None = None,
    postprocess: Callable[[str], str] | None = None,
    config: object | None = None,
) -> Path | None:
    """
    转换单个 Markdown 文件为 PDF

    参数：
        input_file: 输入 Markdown 文件名（相对于 indir）
        output_file: 输出文件名（可选，不含路径）
        options: 转换配置选项
        indir: 输入目录（默认从配置读取）
        outdir: 输出目录（默认从配置读取）
        default_frontmatter: 默认 frontmatter 字典，用于注入缺失的字段
        postprocess: 后处理函数，接收内容返回处理后内容。在内置预处理之后追加执行
        config: PdfworkConfig 配置对象（可选）

    返回：
        成功返回输出文件路径 Path，失败返回 None
    """
    check_pandoc_typst()

    ext = "typ" if options.to_typst else "pdf"

    if config is None:
        try:
            from mark2pdf import ConfigManager

            config = ConfigManager.load()
        except ImportError:
            config = None

    # 获取输入路径
    input_path, output_path = resolve_inout_paths(
        infile=input_file,
        outfile=output_file,
        indir=indir,
        outdir=outdir,
        ext=ext,
        config=config,
    )

    # 如果 overwrite 为 True，重新计算输出路径（不添加时间戳）
    if options.overwrite:
        outdir_path = Path(output_path).parent
        input_path_obj = Path(input_file)
        if output_file:
            output_path = outdir_path / f"{Path(output_file).stem}.{ext}"
        else:
            output_path = outdir_path / f"{input_path_obj.stem}.{ext}"
    else:
        # 确保 output_path 为 Path 类型
        output_path = Path(output_path)

    input_path = Path(input_path)

    with open(input_path, encoding="utf-8") as f:
        content = f.read()

    # 系统级：注入默认 frontmatter（在所有预处理之前）
    if default_frontmatter:
        content = inject_default_frontmatter(content, default_frontmatter, verbose=options.verbose)

    frontmatter = extract_frontmatter(content)

    # 获取最终输出文件名（可能从 exportFilename/title 覆盖）
    output_path = get_output_filename(
        content,
        output_path,
        options.tc,
        options.verbose,
        options.force_filename,
        frontmatter=frontmatter,
    )

    # 预处理（链式执行：默认预处理 + 自定义后处理）
    if options.verbose:
        print("应用 Markdown 预处理...")

    # 1. 默认预处理（始终执行）
    content = apply_default_preprocessing(
        content, removelink=options.removelink, verbose=options.verbose
    )

    # 2. 后处理（如果有，在内置预处理之后追加执行）
    if options.tc:
        postprocess = ensure_tc_postprocess(postprocess)

    if postprocess:
        content = postprocess(content)

    # 创建沙箱并执行转换
    # 获取 tmp_dir 和 images_source_dir
    if config is not None and config.data_root is not None:
        tmp_dir = config.tmp_dir
    else:
        root_dir = get_project_root()
        tmp_dir = root_dir / "tmp"
    indir_path = input_path.parent

    return execute_in_sandbox(
        content=content,
        temp_filename=input_path.name,
        output_path=output_path,
        images_source_dir=indir_path,
        tmp_dir=tmp_dir,
        sandbox_prefix="md2pdf_",
        options=options,
        config=config,
        frontmatter=frontmatter,
    )


def convert_from_string(
    content: str,
    output_path: Path | str,
    options: ConversionOptions = ConversionOptions(),
    default_frontmatter: dict | None = None,
    postprocess: Callable[[str], str] | None = None,
    images_dir: Path | str | None = None,
    config: object | None = None,
) -> Path | None:
    """
    从内存字符串转换为 PDF/Typst 文件

    参数：
        content: Markdown 内容
        output_path: 输出文件路径（可为 PDF 或 Typst）
        options: 转换配置选项
        default_frontmatter: 默认 frontmatter 字典，用于注入缺失的字段
        postprocess: 后处理函数，接收内容返回处理后内容。在内置预处理之后追加执行
        images_dir: 图片目录（可选，images/ 的父目录或 images/ 本身）
        config: PdfworkConfig 配置对象（可选）

    返回：
        成功返回输出文件路径 Path，失败返回 None
    """
    check_pandoc_typst()

    ext = "typ" if options.to_typst else "pdf"

    if config is None:
        try:
            from mark2pdf import ConfigManager

            config = ConfigManager.load()
        except ImportError:
            config = None

    output_path = Path(output_path).expanduser()
    if not output_path.suffix:
        output_path = output_path.with_suffix(f".{ext}")
    if not output_path.is_absolute():
        output_path = output_path.absolute()

    if not options.overwrite:
        output_path = Path(safesave_path(output_path))

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 系统级：注入默认 frontmatter（在所有预处理之前）
    if default_frontmatter:
        content = inject_default_frontmatter(content, default_frontmatter, verbose=options.verbose)

    frontmatter = extract_frontmatter(content)

    # 获取最终输出文件名（可能从 exportFilename/title 覆盖）
    output_path = get_output_filename(
        content,
        output_path,
        options.tc,
        options.verbose,
        options.force_filename,
        frontmatter=frontmatter,
    )

    # 预处理（链式执行：默认预处理 + 自定义后处理）
    if options.verbose:
        print("应用 Markdown 预处理...")

    # 1. 默认预处理（始终执行）
    content = apply_default_preprocessing(
        content, removelink=options.removelink, verbose=options.verbose
    )

    # 2. 后处理（如果有，在内置预处理之后追加执行）
    if options.tc:
        postprocess = ensure_tc_postprocess(postprocess)

    if postprocess:
        content = postprocess(content)

    # 获取 tmp_dir
    if config is not None and config.data_root is not None:
        tmp_dir = config.tmp_dir
    else:
        root_dir = get_project_root()
        tmp_dir = root_dir / "tmp"

    if images_dir:
        images_path = Path(images_dir)
        images_source_dir = images_path.parent if images_path.name == "images" else images_path
    else:
        images_source_dir = tmp_dir

    return execute_in_sandbox(
        content=content,
        temp_filename="input.md",
        output_path=output_path,
        images_source_dir=images_source_dir,
        tmp_dir=tmp_dir,
        sandbox_prefix="str_",
        options=options,
        config=config,
        frontmatter=frontmatter,
    )
