import os
import time
from importlib import resources
from pathlib import Path


def get_project_root() -> Path:
    """
    通过查找项目根目录标识文件获取项目根目录

    优先级顺序：
    1. pyproject.toml（Python 项目）
    2. package.json（Node.js 项目）

    Returns:
        Path: 项目根目录路径

    Raises:
        FileNotFoundError: 如果找不到任何项目根目录标识文件
    """
    current = Path(__file__).resolve()

    # 从当前文件所在目录开始，向上遍历所有父目录
    for parent in current.parents:
        # Python 项目
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            return parent

        # Node.js 项目
        package_json = parent / "package.json"
        if package_json.exists():
            return parent

    raise FileNotFoundError("找不到项目根目录标识文件 (pyproject.toml 或 package.json)")


def create_working_dirs():
    """
    创建标准的工作目录结构

    目录结构：
    - in/     # 输入文件目录
    - out/    # 输出文件目录
    - tmp/    # 临时文件目录

    Returns:
        dict: 包含所有创建目录路径的字典

    Raises:
        FileExistsError: 如果任何目录已存在
    """
    root = None
    in_dir = None
    out_dir = None
    tmp_dir = None

    try:
        from mark2pdf import ConfigManager

        config = ConfigManager.load()
        if config.data_root is not None and not config.standalone:
            root = config.data_root
            in_dir = Path(config.paths.input)
            if not in_dir.is_absolute():
                in_dir = root / in_dir
            out_dir = Path(config.paths.output)
            if not out_dir.is_absolute():
                out_dir = root / out_dir
            tmp_dir = Path(config.paths.tmp)
            if not tmp_dir.is_absolute():
                tmp_dir = root / tmp_dir
    except ImportError:
        pass

    if root is None:
        try:
            root = get_project_root()
        except FileNotFoundError:
            root = Path.cwd()
        in_dir = root / "in"
        out_dir = root / "out"
        tmp_dir = root / "tmp"

    # 检查目录是否已存在
    existing_dirs = []
    for directory in [in_dir, out_dir, tmp_dir]:
        if directory.exists():
            existing_dirs.append(str(directory))

    if existing_dirs:
        raise FileExistsError(f"目录已存在：{', '.join(existing_dirs)}")

    # 安全创建目录（确保父目录存在，如果目录已存在则抛出异常）
    for directory in [in_dir, out_dir, tmp_dir]:
        directory.mkdir(parents=True, exist_ok=False)

    return {"working": root, "in": in_dir, "out": out_dir, "tmp": tmp_dir}


def safesave_path(filename):
    """
    安全保存路径，如果文件已存在则添加时间戳

    避免覆盖已存在的文件，通过添加时间戳来创建唯一的文件名

    Args:
        filename (str): 原始文件名

    Returns:
        str: 安全保存的文件路径（如果文件不存在则返回原路径，存在则添加时间戳）
    """
    save_path = Path(filename)
    if not save_path.exists():
        return str(save_path)

    # 文件已存在，添加时间戳
    stem = save_path.stem
    timestamp = time.strftime("%m-%d-%H%M")
    return str(save_path.with_stem(f"{stem}_{timestamp}"))


def resolve_inout_paths(infile, outfile=None, indir=None, outdir=None, ext="md", config=None):
    """
    准备输入和输出文件路径

    处理流程：
    1. 验证输入文件名格式
    2. 确保文件扩展名
    3. 构建完整的输入输出路径
    4. 验证输入文件存在
    5. 生成安全的输出路径

    Args:
        infile (str):  输入文件名（纯文件名，不能包含目录路径）
        outfile (str, optional): 输出文件名，默认为 None
        indir (str | None):   输入目录，默认从配置或使用 'in'
        outdir (str | None):  输出目录，默认从配置或使用 'out'
        ext (str):     输出文件扩展名，默认为 "md" （注意：不含 '.'）
        config: PdfworkConfig 对象，可选。如果提供则使用 data_root

    Returns:
        tuple: (输入文件完整路径，输出文件完整路径) 或 (None, None) 如果出错
    """
    # 检查输入文件名是否包含目录路径：防止用户输入类似 "subdir/file.md" 或 "../file.md" 的路径
    infile_str = str(infile)
    if "/" in infile_str or "\\" in infile_str:
        raise ValueError(f"输入文件名 '{infile_str}' 包含目录路径，请输入纯文件名")

    # 确保输入文件有正确的扩展名
    infile_path = Path(infile)
    infile = infile_path.with_suffix(infile_path.suffix or ".md")

    # 尝试使用 ConfigManager（如果可用）
    if config is None:
        try:
            from mark2pdf import ConfigManager

            config = ConfigManager.load()
        except ImportError:
            config = None

    # 确定根目录：优先使用 data_root，回退到项目根目录
    if config is not None and config.data_root is not None:
        if indir is None:
            indir_path = config.input_dir
        else:
            indir_path = Path(indir)
            if not indir_path.is_absolute():
                indir_path = config.data_root / indir_path

        if outdir is None:
            outdir_path = config.output_dir
        else:
            outdir_path = Path(outdir)
            if not outdir_path.is_absolute():
                outdir_path = config.data_root / outdir_path
    else:
        root_dir = get_project_root()
        indir_path = Path(indir or "in")
        if not indir_path.is_absolute():
            indir_path = root_dir / indir_path
        outdir_path = Path(outdir or "out")
        if not outdir_path.is_absolute():
            outdir_path = root_dir / outdir_path

    # 构建完整的输入文件路径
    in_path = indir_path / infile

    # 验证输入文件是否存在
    if not in_path.exists():
        raise FileNotFoundError(f"找不到输入文件 '{in_path}'")

    # 生成安全的输出文件路径（避免覆盖已存在文件）
    out_path = _get_output_path(infile, outfile, outdir_path, ext)

    return str(in_path), str(out_path)


def _get_output_path(infile, outfile, outdir, ext):
    """
    内部函数：生成输出文件路径

    Args:
        infile (Path): 输入文件路径对象
        outfile (str): 输出文件名（可选）
        outdir (Path): 输出目录路径
        ext (str): 输出文件扩展名

    Returns:
        str: 安全的输出文件路径
    """
    if outfile is None:
        # 使用输入文件名作为输出文件名，保持目录结构
        return safesave_path(outdir / infile.parent / f"{infile.stem}.{ext}")

    outfile = Path(outfile)
    if outfile.suffix:
        # 输出文件名已包含扩展名，直接使用
        return safesave_path(outdir / outfile)

    # 输出文件名不包含扩展名，添加指定的扩展名
    return safesave_path(outdir / outfile.with_suffix(f".{ext}"))


def _resolve_template_dir(template_dir: str | None, data_root: Path | None) -> Path | None:
    if not template_dir:
        return None
    expanded = Path(os.path.expandvars(template_dir)).expanduser()
    if expanded.is_absolute() or data_root is None:
        return expanded
    return data_root / expanded


def _get_global_template_dir() -> Path:
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return config_home / "mark2pdf" / "templates"


def _resolve_template_variants(base_dir: Path, template_name: str) -> Path | None:
    """
    按优先级查找模板文件

    查找顺序:
    1. <template_name>.typ - 直接模板文件
    2. <template_name>/<template_name>.typ - 目录下同名文件
    3. <template_name>/index.typ - 目录下 index 文件

    Args:
        base_dir: 模板基础目录
        template_name: 模板名称（可带或不带 .typ 后缀）

    Returns:
        找到的模板路径，未找到返回 None
    """
    # 确保 template_name 不带 .typ 后缀
    if template_name.endswith(".typ"):
        name = template_name[:-4]
    else:
        name = template_name

    # 1. 直接文件: nb.typ
    direct = base_dir / f"{name}.typ"
    if direct.is_file():
        return direct

    # 2. 目录同名文件: nb/nb.typ
    dir_same = base_dir / name / f"{name}.typ"
    if dir_same.is_file():
        return dir_same

    # 3. 目录 index: nb/index.typ
    dir_index = base_dir / name / "index.typ"
    if dir_index.is_file():
        return dir_index

    return None


def _get_bundled_template_path(template: str) -> Path | None:
    try:
        package_root = resources.files("mark2pdf.templates")
    except (ModuleNotFoundError, AttributeError):
        return None

    # 确保 template_name 不带 .typ 后缀
    if template.endswith(".typ"):
        name = template[:-4]
    else:
        name = template

    # 按优先级查找
    variants = [
        f"{name}.typ",  # 直接文件
        f"{name}/{name}.typ",  # 目录同名
        f"{name}/index.typ",  # 目录 index
    ]

    for variant in variants:
        resource = package_root.joinpath(variant)
        if resource.is_file():
            try:
                return Path(os.fspath(resource))
            except TypeError:
                continue

    # 回退：原有逻辑（兼容完整路径如 "nb/nb.typ"）
    resource = package_root.joinpath(template)
    if resource.is_file():
        try:
            return Path(os.fspath(resource))
        except TypeError:
            pass

    return None


def resolve_template_path(template: str, template_dir: str = "template", config=None) -> str:
    """
    解析模板文件路径（多层查找）

    查找顺序:
    1. config.paths.template/<template>  (配置指定)
    2. data_root/template/<template>     (工作区默认)
    3. ~/.config/mark2pdf/templates/<template> (全局模板)
    4. 包内置模板                         (importlib.resources)
    5. code_root/src/mark2pdf/templates/<template>     (开发回退)

    Args:
        template (str): 模板文件名
        template_dir (str): 模板目录，默认为 "template"
        config: PdfworkConfig 对象，可选。如果提供则启用本地模板查找

    Returns:
        str: 模板文件完整路径

    Raises:
        FileNotFoundError: 如果模板文件不存在
        ValueError: 如果模板文件名包含目录路径
    """
    # 模板文件名可以包含子目录路径，如 "nb/nb.typ"

    # 尝试使用 ConfigManager（如果可用）
    if config is None:
        try:
            from mark2pdf import ConfigManager

            config = ConfigManager.load()
        except ImportError:
            config = None

    searched: list[Path] = []

    def _check(candidate_dir: Path | None) -> str | None:
        if candidate_dir is None:
            return None

        # 新逻辑：按优先级查找模板变体
        found = _resolve_template_variants(candidate_dir, template)
        if found:
            return str(found)

        # 回退：保持原有逻辑，直接拼接路径（兼容完整路径如 "nb/nb.typ"）
        candidate_path = candidate_dir / template
        searched.append(candidate_path)
        if candidate_path.exists():
            return str(candidate_path)
        return None

    data_root = getattr(config, "data_root", None)
    if data_root is not None:
        config_paths = getattr(config, "paths", None)
        template_value = getattr(config_paths, "template", template_dir)
        config_template_dir = _resolve_template_dir(template_value, data_root)
        found = _check(config_template_dir)
        if found:
            return found

        default_template_dir = data_root / template_dir
        if config_template_dir is None or default_template_dir != config_template_dir:
            found = _check(default_template_dir)
            if found:
                return found

    found = _check(_get_global_template_dir())
    if found:
        return found

    bundled_path = _get_bundled_template_path(template)
    if bundled_path is not None:
        return str(bundled_path)

    root_dir = getattr(config, "code_root", None)
    if root_dir is None:
        try:
            root_dir = get_project_root()
        except FileNotFoundError:
            root_dir = None
    found = _check(root_dir / "src" / "mark2pdf" / "templates" if root_dir is not None else None)
    if found:
        return found

    if searched:
        searched_list = ", ".join(str(path) for path in searched)
        raise FileNotFoundError(f"找不到模板文件 '{template}'，已检查: {searched_list}")
    raise FileNotFoundError(f"找不到模板文件 '{template}'")
