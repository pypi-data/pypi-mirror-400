"""
mark2pdf 配置数据类

定义配置结构，使用 dataclass 提供类型安全和默认值。
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from .defaults import DEFAULT_TEMPLATE


@dataclass
class PathsConfig:
    """路径配置"""

    input: str = "in"
    output: str = "out"
    tmp: str = "tmp"
    template: str = "template"
    fonts: str = "fonts"


@dataclass
class OptionsConfig:
    """选项配置"""

    default_template: str = DEFAULT_TEMPLATE
    overwrite: bool = False


@dataclass
class PdfworkConfig:
    """mark2pdf 主配置类"""

    project_name: str = ""
    paths: PathsConfig = field(default_factory=PathsConfig)
    options: OptionsConfig = field(default_factory=OptionsConfig)
    frontmatter: dict = field(default_factory=dict)

    # 运行时计算的路径（由 ConfigManager 设置）
    data_root: Path | None = field(default=None)
    code_root: Path | None = field(default=None)
    standalone: bool = field(default=False)

    @property
    def input_dir(self) -> Path:
        """输入目录完整路径"""
        if self.data_root is None:
            raise ValueError("data_root 未设置")
        return self.data_root / self.paths.input

    @property
    def output_dir(self) -> Path:
        """输出目录完整路径"""
        if self.data_root is None:
            raise ValueError("data_root 未设置")
        return self.data_root / self.paths.output

    @property
    def tmp_dir(self) -> Path:
        """临时目录完整路径"""
        if self.data_root is None:
            raise ValueError("data_root 未设置")
        return self.data_root / self.paths.tmp

    @property
    def template_dir(self) -> Path:
        """本地模板目录完整路径"""
        if self.data_root is None:
            raise ValueError("data_root 未设置")
        template_value = self.paths.template or "template"
        template_path = Path(os.path.expandvars(template_value)).expanduser()
        if template_path.is_absolute():
            return template_path
        return self.data_root / template_path

    @property
    def fonts_dir(self) -> Path | None:
        """字体目录完整路径（可选）"""
        if self.data_root is None:
            raise ValueError("data_root 未设置")
        fonts_value = self.paths.fonts
        if not fonts_value:
            return None
        fonts_path = Path(os.path.expandvars(fonts_value)).expanduser()
        if fonts_path.is_absolute():
            return fonts_path
        return self.data_root / fonts_path
