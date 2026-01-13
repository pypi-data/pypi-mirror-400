"""
Chinese conversion utilities.
"""

from functools import lru_cache


@lru_cache(maxsize=1)
def _get_opencc_s2t():
    from opencc import OpenCC

    return OpenCC("s2t")


def convert_to_traditional(text: str) -> str:
    return _get_opencc_s2t().convert(text)
