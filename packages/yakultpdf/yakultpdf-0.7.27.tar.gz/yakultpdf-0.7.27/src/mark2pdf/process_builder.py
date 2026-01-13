"""
mark2pdf 后处理器构建器

负责动态加载和组装后处理器链。
"""

from collections.abc import Callable
from dataclasses import dataclass

from mark2pdf.core.postprocess import load_postprocessor


@dataclass(frozen=True)
class PostprocessBuildResult:
    chain: Callable[[str], str] | None
    loaded: list[str]
    missing: list[str]


def build_postprocessor_chain(
    processor_names: list[str],
) -> PostprocessBuildResult:
    """
    构建后处理器链

    根据处理器名称列表动态加载并组装成一个组合函数。

    Args:
        processor_names: 处理器名称列表，如 ["remove_links", "to_traditional_chinese"]

    Returns:
        PostprocessBuildResult（包含处理链、已加载列表和缺失列表）
    """
    if not processor_names:
        return PostprocessBuildResult(chain=None, loaded=[], missing=[])

    resolved = [(p, load_postprocessor(p)) for p in processor_names]
    funcs = [f for _, f in resolved if f]  # 过滤 None

    # 检查未找到的处理器
    loaded = [p for p, f in resolved if f]
    missing = [p for p, f in resolved if f is None]

    if not funcs:
        return PostprocessBuildResult(chain=None, loaded=loaded, missing=missing)

    def combined(content: str) -> str:
        for fn in funcs:
            content = fn(content)
        return content

    if any(p == "to_traditional_chinese" and f for p, f in resolved):
        combined._mark2pdf_handles_tc = True  # type: ignore[attr-defined]

    return PostprocessBuildResult(chain=combined, loaded=loaded, missing=missing)
