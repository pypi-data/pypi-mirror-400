"""
转换相关的辅助函数

提供配置合并、转换执行等功能，简化工作区脚本。
"""

import traceback
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from mark2pdf.core import ConversionOptions, convert_directory, convert_file
from mark2pdf.core.utils import merge_frontmatter, open_with_system
from mark2pdf.helper_markdown import extract_frontmatter

from .config import ConfigManager, load_frontmatter_yaml, resolve_template


def _convert_batch_file(
    file_name: str,
    file_path: str,
    *,
    file_indir: str,
    file_outdir: str,
    options_base_fm: dict,
    default_frontmatter: dict | None,
    template: str | None,
    config_template: str | None,
    config: object | None,
    verbose: bool,
    overwrite: bool,
    tc: bool,
    force_filename: bool,
    processor_names: list[str] | None,
) -> tuple[str, bool, str | None]:
    try:
        file_path_obj = Path(file_path)
        file_fm = extract_frontmatter(file_path_obj) if file_path_obj.exists() else {}
        merged_fm = merge_frontmatter(options_base_fm, file_fm)

        options = ConversionOptions(
            verbose=verbose,
            overwrite=overwrite,
            tc=tc,
            force_filename=force_filename,
        )

        options.template = resolve_template(
            cli_template=template,
            frontmatter_template=merged_fm.get("theme", {}).get("template"),
            config_template=config_template,
        )

        postprocess = None
        if processor_names:
            from mark2pdf.process_builder import build_postprocessor_chain

            postprocess_result = build_postprocessor_chain(processor_names)
            postprocess = postprocess_result.chain

        result = convert_file(
            input_file=file_name,  # 纯文件名
            options=options,
            indir=file_indir,  # 包含子目录的输入路径
            outdir=file_outdir,  # 包含子目录的输出路径
            default_frontmatter=default_frontmatter,
            config=config,
            postprocess=postprocess,
        )
    except Exception as exc:
        # 保留通用捕获防止单文件失败阻塞批处理，但记录完整堆栈
        traceback.print_exc()
        return file_name, False, str(exc)

    return file_name, result is not None, None


@dataclass
class BatchConfig:
    """批量转换的配置数据"""

    config: object  # 工作区配置
    input_dir: Path  # 输入目录
    output_subdir: Path  # 输出目录（用于打印）
    file_indir: str  # convert_file 用的 indir
    file_outdir: str  # convert_file 用的 outdir
    default_frontmatter: dict | None  # 默认 frontmatter
    options_base_fm: dict  # 用于模板解析的合并 frontmatter
    template: str | None  # CLI 模板
    config_template: str | None  # 配置文件默认模板
    verbose: bool
    overwrite: bool  # 已合并 CLI > config
    tc: bool
    force_filename: bool


def _prepare_postprocessors(
    postprocess: Callable[[str], str] | None,
    processor_names: list[str] | None,
    tc: bool,
    jobs: int,
) -> tuple[list[str] | None, Callable[[str], str] | None, int]:
    """
    准备后处理器配置

    Returns:
        (最终 processor_names, 最终 postprocess 函数, 最终 jobs)
    """
    postprocess_names = list(processor_names) if processor_names else None

    # 若 processor_names 存在且 tc=True，追加繁体转换
    if postprocess_names and tc and "to_traditional_chinese" not in postprocess_names:
        postprocess_names.append("to_traditional_chinese")

    # 并发模式下的特殊处理
    if jobs > 1 and postprocess_names is None:
        if postprocess is not None:
            print("警告：并发模式不支持自定义后处理器，已自动切换为单线程")
            jobs = 1
        elif tc:
            postprocess_names = ["to_traditional_chinese"]

    return postprocess_names, postprocess, jobs


def _prepare_batch_config(
    directory: str,
    workspace_dir: Path,
    config: object,
    *,
    template: str | None,
    overwrite: bool,
    tc: bool,
    force_filename: bool,
    verbose: bool,
) -> BatchConfig | None:
    """
    准备批量转换的配置

    Returns:
        BatchConfig 或 None（输入目录不存在时）
    """
    final_overwrite = overwrite or config.options.overwrite

    # 确定输入输出目录
    if directory == ".":
        input_dir = config.input_dir
        output_subdir = config.output_dir
        file_indir = config.paths.input
        file_outdir = config.paths.output
    else:
        input_dir = config.input_dir / directory
        output_subdir = config.output_dir / directory
        file_indir = f"{config.paths.input}/{directory}"
        file_outdir = f"{config.paths.output}/{directory}"

    if not input_dir.exists():
        print(f"错误：目录不存在：{input_dir}")
        return None

    # 加载工作区默认 frontmatter
    workspace_fm = load_frontmatter_yaml(workspace_dir)
    if config.frontmatter:
        workspace_fm = merge_frontmatter(config.frontmatter, workspace_fm)

    # 读取目录中 index.md 的 frontmatter（作为目录级默认值）
    index_path = input_dir / "index.md"
    index_fm = extract_frontmatter(index_path) if index_path.exists() else {}

    # 合并目录级 frontmatter（index.md 覆盖工作区默认值）
    # 注意：排除 title 和 exportFilename，这些应该是每个文件特有的
    default_fm = workspace_fm
    if index_fm:
        index_fm_for_default = {
            k: v for k, v in index_fm.items() if k not in ("title", "exportFilename")
        }
        default_fm = merge_frontmatter(workspace_fm, index_fm_for_default)

    options_base_fm = merge_frontmatter(workspace_fm, index_fm)

    return BatchConfig(
        config=config,
        input_dir=input_dir,
        output_subdir=output_subdir,
        file_indir=file_indir,
        file_outdir=file_outdir,
        default_frontmatter=default_fm if default_fm else None,
        options_base_fm=options_base_fm,
        template=template,
        config_template=config.options.default_template,
        verbose=verbose,
        overwrite=final_overwrite,
        tc=tc,
        force_filename=force_filename,
    )


def _discover_batch_files(input_dir: Path) -> list[Path]:
    """获取并排序待处理文件列表（排除 index.md）"""
    md_files = [f for f in input_dir.glob("*.md") if f.name != "index.md"]
    return sorted(md_files)


def _run_sequential(
    files: list[Path],
    batch_config: BatchConfig,
    postprocess_fn: Callable[[str], str] | None,
) -> tuple[int, int]:
    """
    顺序执行所有文件转换

    Returns:
        (成功数, 失败数)
    """
    success_count = 0
    fail_count = 0

    for md_file in files:
        print(f"处理：{md_file.name}")

        file_fm = extract_frontmatter(md_file) if md_file.exists() else {}
        merged_fm = merge_frontmatter(batch_config.options_base_fm, file_fm)

        options = ConversionOptions(
            verbose=batch_config.verbose,
            overwrite=batch_config.overwrite,
            tc=batch_config.tc,
            force_filename=batch_config.force_filename,
        )

        options.template = resolve_template(
            cli_template=batch_config.template,
            frontmatter_template=merged_fm.get("theme", {}).get("template"),
            config_template=batch_config.config_template,
        )

        result = convert_file(
            input_file=md_file.name,
            options=options,
            indir=batch_config.file_indir,
            outdir=batch_config.file_outdir,
            default_frontmatter=batch_config.default_frontmatter,
            config=batch_config.config,
            postprocess=postprocess_fn,
        )

        if result:
            success_count += 1
        else:
            fail_count += 1

    return success_count, fail_count


def _run_parallel(
    files: list[Path],
    batch_config: BatchConfig,
    jobs: int,
    processor_names: list[str] | None,
) -> tuple[int, int]:
    """
    并发执行所有文件转换

    Returns:
        (成功数, 失败数)
    """
    success_count = 0
    fail_count = 0

    print(f"并发数：{jobs}")

    max_workers = min(jobs, len(files))
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _convert_batch_file,
                md_file.name,
                str(md_file),
                file_indir=batch_config.file_indir,
                file_outdir=batch_config.file_outdir,
                options_base_fm=batch_config.options_base_fm,
                default_frontmatter=batch_config.default_frontmatter,
                template=batch_config.template,
                config_template=batch_config.config_template,
                config=batch_config.config,
                verbose=batch_config.verbose,
                overwrite=batch_config.overwrite,
                tc=batch_config.tc,
                force_filename=batch_config.force_filename,
                processor_names=processor_names,
            ): md_file.name
            for md_file in files
        }

        for future in as_completed(futures):
            file_name = futures[future]
            try:
                _, ok, error = future.result()
            except Exception as exc:
                ok = False
                error = str(exc)

            if ok:
                success_count += 1
                if batch_config.verbose:
                    print(f"完成：{file_name}")
            else:
                fail_count += 1
                print(f"失败：{file_name}")
                if error and batch_config.verbose:
                    print(f"  ⚠️ {error}")

    return success_count, fail_count

def run_conversion(
    filename: str,
    workspace_dir: Path,
    postprocess: Callable[[str], str] | None = None,
    *,
    verbose: bool = False,
    overwrite: bool = False,
    template: str | None = None,
    tc: bool = False,
    open_file: bool = False,
    force_filename: bool = False,
) -> bool:
    """
    执行 Markdown 到 PDF 的转换

    这是工作区脚本使用的主入口函数，封装了全部转换逻辑。

    Args:
        filename: 输入文件名
        workspace_dir: 工作区目录
        postprocess: 后处理函数（可选）
        verbose: 显示详细信息
        overwrite: 覆盖输出文件
        template: 指定模板（CLI 优先级最高）
        tc: 转换为繁体中文
        open_file: 转换完成后打开文件

    Returns:
        转换是否成功
    """
    # 加载配置
    config = ConfigManager.load(start_dir=workspace_dir)

    # 合并 overwrite：CLI > config
    final_overwrite = overwrite or config.options.overwrite

    # 加载默认 frontmatter
    default_fm = load_frontmatter_yaml(workspace_dir)
    if config.frontmatter:
        default_fm = merge_frontmatter(config.frontmatter, default_fm)

    # 读取文件 frontmatter（用于 template）
    input_path = config.input_dir / filename
    file_fm = extract_frontmatter(input_path) if input_path.exists() else {}

    merged_fm = merge_frontmatter(default_fm, file_fm)

    # 构建 options
    options = ConversionOptions(
        verbose=verbose,
        overwrite=final_overwrite,
        tc=tc,
        force_filename=force_filename,
    )

    options.template = resolve_template(
        cli_template=template,
        frontmatter_template=merged_fm.get("theme", {}).get("template"),
        config_template=config.options.default_template,
    )

    # 执行转换
    result = convert_file(
        input_file=filename,
        options=options,
        indir=config.paths.input,
        outdir=config.paths.output,
        default_frontmatter=default_fm if default_fm else None,
        postprocess=postprocess,
        config=config,
    )

    if result and open_file:
        open_with_system(result, verbose=verbose)

    return result is not None


def run_directory_conversion(
    directory: str,
    workspace_dir: Path,
    postprocess: Callable[[str], str] | None = None,
    *,
    verbose: bool = False,
    overwrite: bool = False,
    template: str | None = None,
    tc: bool = False,
    open_file: bool = False,
    force_filename: bool = False,
) -> bool:
    """
    执行目录到 PDF 的转换（合并目录中所有 Markdown 文件）

    Args:
        directory: 目录名（相对于 input 路径）
        workspace_dir: 工作区目录
        postprocess: 后处理函数（可选）
        verbose: 显示详细信息
        overwrite: 覆盖输出文件
        template: 指定模板（CLI 优先级最高）
        tc: 转换为繁体中文
        open_file: 转换完成后打开文件

    Returns:
        转换是否成功
    """
    # 加载配置
    config = ConfigManager.load(start_dir=workspace_dir)

    # 合并 overwrite：CLI > config
    final_overwrite = overwrite or config.options.overwrite

    # 加载默认 frontmatter（与 run_conversion 一致）
    default_fm = load_frontmatter_yaml(workspace_dir)
    if config.frontmatter:
        default_fm = merge_frontmatter(config.frontmatter, default_fm)

    # 读取目录中 index.mdx/index.md 的 frontmatter（用于 template）
    dir_path = config.input_dir / directory
    index_path = dir_path / "index.mdx"
    if not index_path.exists():
        index_path = dir_path / "index.md"
    file_fm = extract_frontmatter(index_path) if index_path.exists() else {}

    merged_fm = merge_frontmatter(default_fm, file_fm)

    # 构建 options
    options = ConversionOptions(
        verbose=verbose,
        overwrite=final_overwrite,
        tc=tc,
        force_filename=force_filename,
    )

    options.template = resolve_template(
        cli_template=template,
        frontmatter_template=merged_fm.get("theme", {}).get("template"),
        config_template=config.options.default_template,
    )

    # 执行目录转换
    result = convert_directory(
        directory=directory,
        options=options,
        indir=config.paths.input,
        outdir=config.paths.output,
        default_frontmatter=default_fm if default_fm else None,
        config=config,
        postprocess=postprocess,
    )

    if result and open_file:
        open_with_system(result, verbose=verbose)

    return result is not None


def run_batch_conversion(
    directory: str,
    workspace_dir: Path,
    postprocess: Callable[[str], str] | None = None,
    *,
    processor_names: list[str] | None = None,
    verbose: bool = False,
    overwrite: bool = False,
    template: str | None = None,
    tc: bool = False,
    open_file: bool = False,  # noqa: ARG001 - 批量模式不支持
    force_filename: bool = False,
    jobs: int = 4,
) -> bool:
    """
    执行批量转换（逐一转换目录中每个 Markdown 文件）

    与 run_directory_conversion 不同，不会合并文件，而是逐一生成 PDF。

    Args:
        directory: 目录名（相对于 input 路径），使用 "." 表示当前目录
        workspace_dir: 工作区目录
        postprocess: 后处理函数（可选）
        processor_names: 后处理器名称列表（可选，用于并发场景）
        verbose: 显示详细信息
        overwrite: 覆盖输出文件
        template: 指定模板（CLI 优先级最高）
        tc: 转换为繁体中文
        open_file: 转换完成后打开文件（批量模式不支持）
        jobs: 并发处理数量（默认 1）

    Returns:
        全部转换成功返回 True，任一失败返回 False
    """
    # 规范化 jobs
    if jobs < 1:
        jobs = 1

    # 准备后处理器配置
    postprocess_names, postprocess_fn, jobs = _prepare_postprocessors(
        postprocess, processor_names, tc, jobs
    )

    # 加载配置
    config = ConfigManager.load(start_dir=workspace_dir)

    # 准备批量配置
    batch_config = _prepare_batch_config(
        directory,
        workspace_dir,
        config,
        template=template,
        overwrite=overwrite,
        tc=tc,
        force_filename=force_filename,
        verbose=verbose,
    )
    if batch_config is None:
        return False

    # 发现待处理文件
    sorted_files = _discover_batch_files(batch_config.input_dir)
    if not sorted_files:
        print(
            f"警告：目录中没有 Markdown 文件（除 index.md 外）：{batch_config.input_dir}"
        )
        return True

    # 打印进度信息
    print(f"批量转换：{len(sorted_files)} 个文件")
    print(f"输入目录：{batch_config.input_dir}")
    print(f"输出目录：{batch_config.output_subdir}")
    print("-" * 40)

    # 执行转换
    if jobs == 1:
        # 单线程模式：构建后处理函数
        if postprocess_names:
            from mark2pdf.process_builder import build_postprocessor_chain

            postprocess_result = build_postprocessor_chain(postprocess_names)
            postprocess_fn = postprocess_result.chain

        success_count, fail_count = _run_sequential(
            sorted_files, batch_config, postprocess_fn
        )
    else:
        success_count, fail_count = _run_parallel(
            sorted_files, batch_config, jobs, postprocess_names
        )

    # 汇报结果
    print("-" * 40)
    print(f"完成：成功 {success_count}，失败 {fail_count}")

    return fail_count == 0

