"""
mark2pdf 工作区管理器

负责工作区的初始化、检测与模板安装。
"""

import shutil
from contextlib import nullcontext
from importlib import resources
from pathlib import Path

from .defaults import CONFIG_FILENAME, DEFAULT_CONFIG_CONTENT
from .loader import ConfigManager, get_code_root

_IGNORE_TEMPLATE_NAMES = {".DS_Store", "__pycache__", "__init__.py"}


def _has_bundled_templates(root) -> bool:
    for item in root.iterdir():
        if item.name in _IGNORE_TEMPLATE_NAMES:
            continue
        return True
    return False


def _get_template_source_context():
    try:
        bundled_root = resources.files("mark2pdf.templates")
    except (ModuleNotFoundError, AttributeError):
        bundled_root = None

    if bundled_root is not None and _has_bundled_templates(bundled_root):
        return resources.as_file(bundled_root)

    try:
        code_root = get_code_root()
    except FileNotFoundError:
        return nullcontext(None)

    template_root = code_root / "src" / "mark2pdf" / "templates"
    if not template_root.exists():
        return nullcontext(None)
    return nullcontext(template_root)


def _copy_all_templates(source_root: Path, target_root: Path) -> None:
    target_root.mkdir(parents=True, exist_ok=True)
    ignore = shutil.ignore_patterns(*_IGNORE_TEMPLATE_NAMES)
    for item in source_root.iterdir():
        if item.name in _IGNORE_TEMPLATE_NAMES:
            continue
        target_path = target_root / item.name
        if item.is_dir():
            shutil.copytree(item, target_path, dirs_exist_ok=True, ignore=ignore)
        else:
            shutil.copy2(item, target_path)


def _copy_single_template(source_root: Path, target_root: Path, template_name: str) -> None:
    if "/" in template_name or "\\" in template_name:
        raise ValueError(f"模板文件名 '{template_name}' 包含目录路径，请输入纯文件名")

    template_path = source_root / template_name

    # 目录式模板：复制整个目录
    if template_path.exists() and template_path.is_dir():
        target_root.mkdir(parents=True, exist_ok=True)
        target_dir = target_root / template_path.name
        ignore = shutil.ignore_patterns(*_IGNORE_TEMPLATE_NAMES)
        shutil.copytree(template_path, target_dir, dirs_exist_ok=True, ignore=ignore)
        return

    # 检查是否有同名目录（不带扩展名）
    # 例如：template_name = "nb.typ"，检查是否存在 source_root/nb/ 目录
    if template_name.endswith(".typ"):
        dir_name = template_name[:-4]
        dir_path = source_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            target_root.mkdir(parents=True, exist_ok=True)
            target_dir = target_root / dir_name
            ignore = shutil.ignore_patterns(*_IGNORE_TEMPLATE_NAMES)
            shutil.copytree(dir_path, target_dir, dirs_exist_ok=True, ignore=ignore)
            return

    # 单文件模板：直接复制
    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在：{template_path}")

    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template_path, target_root / template_path.name)


def detect_workspace() -> Path | None:
    """
    检测当前目录是否为工作区

    返回工作区目录，若不是工作区则返回 None
    """
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / CONFIG_FILENAME).exists():
            return parent
    return None


def init_workspace(
    target_dir: Path | str | None = None,
    copy_templates: bool = False,
    template_name: str | None = None,
    simple: bool = False,
) -> Path:
    """
    初始化工作区

    创建标准目录结构、配置文件、帮助脚本和示例文件。
    simple 模式仅创建配置文件与 frontmatter 示例。

    Args:
        target_dir: 目标目录，默认为 CWD
        copy_templates: 是否复制系统模板到本地
        template_name: 仅复制指定模板文件（文件名）
        simple: 仅创建配置与 frontmatter，允许非空目录

    Returns:
        Path: 工作区根目录

    Raises:
        FileExistsError: 目录不为空
    """
    target = Path(target_dir).resolve() if target_dir else Path.cwd()

    if target.exists() and not target.is_dir():
        raise ValueError(f"目标不是目录: {target}")

    if copy_templates and template_name:
        raise ValueError("copy_templates 与 template_name 不能同时使用")

    if simple and (copy_templates or template_name):
        raise ValueError("simple 模式不支持复制模板")

    # 检查非空目录
    if not simple and target.exists() and target.is_dir():
        has_files = False
        for child in target.iterdir():
            if child.name == ".DS_Store":
                continue
            has_files = True
            break

        if has_files:
            raise FileExistsError(
                f"目录不为空: {target}\n为了安全起见，禁止在非空目录初始化。请选择空目录。"
            )
    templates_dir = Path(__file__).resolve().parents[1] / "resources"

    if simple:
        target.mkdir(parents=True, exist_ok=True)

        # 生成配置文件
        config_path = target / CONFIG_FILENAME
        if not config_path.exists():
            config_path.write_text(DEFAULT_CONFIG_CONTENT, encoding="utf-8")
            print(f"  已创建配置: {CONFIG_FILENAME}")
        else:
            print(f"  配置文件已存在: {CONFIG_FILENAME}")

        # 复制 frontmatter.yaml 示例
        fm_src = templates_dir / "frontmatter.yaml"
        fm_dst = target / "frontmatter.yaml"
        if not fm_dst.exists():
            shutil.copy(fm_src, fm_dst)
            print("  已创建配置: frontmatter.yaml")
        else:
            print("  配置已存在: frontmatter.yaml")

        print(f"\n工作区配置已初始化: {target}")
        return target

    # 创建标准目录
    for d in ["in", "out", "tmp", "template", "fonts"]:
        dir_path = target / d
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  已创建目录: {d}/")

    # 生成配置文件
    config_path = target / CONFIG_FILENAME
    if not config_path.exists():
        config_path.write_text(DEFAULT_CONFIG_CONTENT, encoding="utf-8")
        print(f"  已创建配置: {CONFIG_FILENAME}")
    else:
        print(f"  配置文件已存在: {CONFIG_FILENAME}")

    # 复制帮助脚本
    script_src = templates_dir / "createpdf.py"
    script_dst = target / "createpdf.py"
    if not script_dst.exists():
        shutil.copy(script_src, script_dst)
        # 添加执行权限
        script_dst.chmod(script_dst.stat().st_mode | 0o755)
        print("  已创建脚本: createpdf.py")
    else:
        print("  脚本已存在: createpdf.py")

    # 复制示例 index.md
    index_src = templates_dir / "index.md"
    index_dst = target / "in" / "index.md"
    if not index_dst.exists():
        shutil.copy(index_src, index_dst)
        print("  已创建样例: in/index.md")
    else:
        print("  样例已存在: in/index.md")

    # 复制 frontmatter.yaml 示例
    fm_src = templates_dir / "frontmatter.yaml"
    fm_dst = target / "frontmatter.yaml"
    if not fm_dst.exists():
        shutil.copy(fm_src, fm_dst)
        print("  已创建配置: frontmatter.yaml")
    else:
        print("  配置已存在: frontmatter.yaml")

    if copy_templates or template_name:
        with _get_template_source_context() as source_root:
            if source_root is None or not source_root.exists():
                raise FileNotFoundError("未找到可用的模板资源")

            target_templates = target / "template"
            if template_name:
                _copy_single_template(source_root, target_templates, template_name)
                print(f"  已复制模板: {template_name}")
            else:
                _copy_all_templates(source_root, target_templates)
                print("  已复制模板: template/")

    print(f"\n工作区已初始化: {target}")
    print("\n使用方法:")
    print(f"  uv run --directory <mark2pdf代码目录> python {target}/createpdf.py")
    return target


def install_template(template_name: str, target_dir: Path | str | None = None) -> Path:
    """
    将指定模板复制到工作区的模板目录

    Args:
        template_name: 模板文件名（如 nb.typ）
        target_dir: 目标工作区目录（可选）

    Returns:
        Path: 模板目录路径

    Raises:
        FileNotFoundError: 未找到工作区或模板资源
        ValueError: 模板文件名不合法
    """
    config = ConfigManager.load(target_dir)
    if config.standalone or config.data_root is None:
        raise FileNotFoundError("未检测到工作区配置，请先使用 'mark2pdf init <dir>' 初始化。")

    target_templates = config.template_dir
    with _get_template_source_context() as source_root:
        if source_root is None or not source_root.exists():
            raise FileNotFoundError("未找到可用的模板资源")

        _copy_single_template(source_root, target_templates, template_name)

    return target_templates
