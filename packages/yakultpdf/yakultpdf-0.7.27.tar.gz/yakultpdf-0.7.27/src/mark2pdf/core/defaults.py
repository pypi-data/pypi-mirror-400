"""
mark2pdf.core 默认配置常量
"""

from mark2pdf.defaults import DEFAULT_TEMPLATE  # noqa: F401


def get_default_dirs() -> tuple[str, str]:
    """
    获取默认输入/输出目录

    从 ConfigManager 读取配置。

    Returns:
        (indir, outdir) 元组

    Raises:
        RuntimeError: ConfigManager 不可用或配置文件不存在
    """
    try:
        from mark2pdf import ConfigManager

        config = ConfigManager.load()
        return config.paths.input, config.paths.output
    except ImportError as e:
        raise RuntimeError("mark2pdf 模块不可用") from e
    except FileNotFoundError as e:
        raise RuntimeError("未找到配置文件，请运行 mark2pdf init 初始化工作区") from e
    except ValueError as e:
        raise RuntimeError(f"配置错误: {e}") from e


def get_build_defaults() -> dict:
    """
    获取选项配置默认值 (overwrite 等)

    Returns:
        允许直接解包到 ConversionOptions 的字典，例如: {'overwrite': False}
    """
    try:
        from mark2pdf import ConfigManager

        config = ConfigManager.load()
        return {
            "overwrite": config.options.overwrite,
            "template": config.options.default_template,
        }
    except Exception:
        # 如果加载失败（例如不在工作区），返回空字典，让 ConversionOptions 使用其自身的默认值
        # 注意：get_default_dirs 比较严格，这里我们可以宽容一些，或者保持一致？
        # given that cli.py calls get_default_dirs which crashes, strict is fine?
        # But let's be safe.
        return {}
