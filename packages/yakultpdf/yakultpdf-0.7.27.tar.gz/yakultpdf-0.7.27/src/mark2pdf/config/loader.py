"""
mark2pdf 配置加载器

负责加载和解析配置，支持多种配置来源。
"""

from pathlib import Path

import tomllib

from .defaults import CONFIG_FILENAME, DEFAULT_TEMPLATE
from .types import OptionsConfig, PathsConfig, PdfworkConfig


def get_code_root() -> Path:
    """
    获取代码项目根目录

    通过查找项目标识文件向上遍历。

    Returns:
        Path: 代码项目根目录

    Raises:
        FileNotFoundError: 找不到项目根目录
    """
    current = Path(__file__).resolve()

    for parent in current.parents:
        # Python 项目
        if (parent / "pyproject.toml").exists():
            return parent

        # Node.js 项目
        if (parent / "package.json").exists():
            return parent

    raise FileNotFoundError("找不到代码项目根目录 (pyproject.toml 或 package.json)")


def load_frontmatter_yaml(data_root: Path) -> dict:
    """
    从工作区的 frontmatter.yaml 加载默认 frontmatter

    Args:
        data_root: 工作区根目录

    Returns:
        frontmatter 字典，如果文件不存在则返回空字典
    """
    import yaml

    fm_file = Path(data_root) / "frontmatter.yaml"
    if fm_file.exists():
        with open(fm_file, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def resolve_template(
    cli_template: str | None = None,
    frontmatter_template: str | None = None,
    config_template: str | None = None,
    default: str = DEFAULT_TEMPLATE,
) -> str | None:
    """
    解析模板优先级链

    优先级：CLI参数 > frontmatter > 配置文件 > 默认值

    Args:
        cli_template: 命令行指定的模板
        frontmatter_template: 文件 frontmatter 中的 theme.template 字段
        config_template: 配置文件中的 default_template
        default: 默认模板，如果为 None 则不设置默认值

    Returns:
        解析后的模板路径，如果都未指定且 default 为 None 则返回 None
    """
    return cli_template or frontmatter_template or config_template or default


class ConfigManager:
    """
    配置管理器

    负责加载配置，支持以下配置来源：
    1. 当前目录或父目录中的 mark2pdf.config.toml
    2. 未找到配置文件时使用独立模式
    """

    @classmethod
    def load(cls, start_dir: Path | str | None = None) -> PdfworkConfig:
        """
        加载配置

        Args:
            start_dir: 配置查找起点目录（可选）

        Returns:
            PdfworkConfig: 加载的配置对象
        """
        start_path = cls._normalize_start_dir(start_dir)
        data_root = cls._resolve_data_root(start_path)
        if data_root is None:
            config = cls._create_standalone_config(start_path)
        else:
            config = cls._load_toml(data_root)
            config.data_root = data_root
        try:
            config.code_root = get_code_root()
        except FileNotFoundError:
            config.code_root = None
        return config

    @classmethod
    def _resolve_data_root(cls, start_dir: Path | None = None) -> Path | None:
        """
        解析数据根目录

        优先级：当前目录 > 向上查找
        """
        return cls._find_config_root(start_dir)

    @classmethod
    def _find_config_root(cls, start: Path | None = None) -> Path | None:
        """
        从起始目录向上查找配置文件
        """
        start_path = start or Path.cwd()
        for parent in [start_path] + list(start_path.parents):
            if (parent / CONFIG_FILENAME).exists():
                return parent
        return None

    @classmethod
    def _create_standalone_config(cls, data_root: Path | None = None) -> PdfworkConfig:
        """
        创建独立运行模式的默认配置
        """
        config = PdfworkConfig(
            paths=PathsConfig(input=".", output=".", tmp=".mark2pdf_tmp"),
        )
        config.data_root = data_root or Path.cwd()
        config.standalone = True
        return config

    @staticmethod
    def _normalize_start_dir(start_dir: Path | str | None) -> Path | None:
        if start_dir is None:
            return None
        start_path = Path(start_dir)
        if start_path.is_file():
            return start_path.parent
        return start_path

    @classmethod
    def _load_toml(cls, data_root: Path) -> PdfworkConfig:
        """
        从 TOML 文件加载配置

        如果配置文件不存在，返回默认配置。
        """
        config_file = data_root / CONFIG_FILENAME

        if not config_file.exists():
            # 使用默认配置
            return PdfworkConfig()

        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        # 解析 paths 配置
        paths_data = data.get("paths", {})
        paths = PathsConfig(
            input=paths_data.get("in", "in"),
            output=paths_data.get("out", "out"),
            tmp=paths_data.get("tmp", "tmp"),
            template=paths_data.get("template", "template"),
            fonts=paths_data.get("fonts", "fonts"),
        )

        # 解析 options 配置（兼容旧 build 节）
        options_data = data.get("options")
        if options_data is None:
            options_data = data.get("build", {})
        options = OptionsConfig(
            default_template=options_data.get("default_template", DEFAULT_TEMPLATE),
            overwrite=options_data.get("overwrite", False),
        )

        # 构建完整配置
        return PdfworkConfig(
            project_name=data.get("project", {}).get("name", ""),
            paths=paths,
            options=options,
            frontmatter=data.get("frontmatter", {}),
        )
