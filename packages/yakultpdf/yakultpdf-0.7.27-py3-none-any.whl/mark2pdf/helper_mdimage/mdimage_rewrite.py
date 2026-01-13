from __future__ import annotations

import hashlib
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .mdimage_assets import (
    DownloadResult,
    clear_copy_image,
    create_wechat_placeholder,
    download_image,
    escape_markdown_path,
    find_existing_image,
    is_data_uri,
    sanitize_filename,
    save_data_uri_image,
)


def _default_logger(message: str) -> None:
    print(message)


@dataclass
class RewriteResult:
    content: str
    skipped: int
    downloaded: int
    data_uri_skipped: int
    failures: list[str]


def remove_image_links_wrapping_images(content: str) -> str:
    """
    Remove outer links if they wrap an image and point to an image-like resource (e.g. Substack).
    Example: [ ![alt](src) ](href) -> ![alt](src)
    Does NOT remove profile links (e.g. substack.com/@...).
    """
    pattern = re.compile(
        r"\[\s*(?P<image>!\[[^\]]*\]\([^\)]+\)(?:\{[^\}]*\})?)\s*\]\((?P<href>[^\)]+)\)",
        re.MULTILINE | re.DOTALL,
    )

    def replacement(match: re.Match[str]) -> str:
        image_tag = match.group("image")
        href = match.group("href").strip()

        # Keep profile links (e.g. substack.com/@...)
        if "substack.com/@" in href:
            return match.group(0)

        # Image extensions to check
        image_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif", ".bmp")

        # Remove wrapper if href looks like an image resource
        # Case 1: href contains Substack image fetch URL
        if "substackcdn.com/image/fetch" in href:
            return image_tag

        # Case 1.5: X/Twitter media links
        if ("/media/" in href or "/photo/" in href) and ("x.com" in href or "twitter.com" in href):
            return image_tag

        # Case 2: href ends with image extension
        href_lower = href.lower()
        for ext in image_exts:
            if ext in href_lower:
                return image_tag

        # Default: keep the wrapper link for non-image hrefs
        return match.group(0)

    return pattern.sub(replacement, content)


def rewrite_markdown_images(
    content: str,
    images_dir: Path,
    rel_dir: str,
    *,
    delay: float = 1.0,
    wechat_placeholder: bool = True,
    downloader: Callable[[str, dict[str, str]], bytes] | None = None,
    log: Callable[[str], None] = _default_logger,
) -> RewriteResult:
    """
    重写 Markdown 图片链接，下载 HTTP 图片并保存 data URI。
    rel_dir: Markdown 中使用的相对目录（不含前导 ./），例如 images/foo。
    """
    images_dir = Path(images_dir)
    rel_dir = rel_dir.lstrip("./")
    log = log or _default_logger

    cleaned_content = clear_copy_image(content)
    cleaned_content = remove_image_links_wrapping_images(cleaned_content)

    data_uri_pattern = re.compile(
        r"!\[(?P<alt>[^\]]*)\]\((?P<url>data:image/[^\)]+)\)(?P<tail>\{[^\}]*\})?",
        re.MULTILINE | re.DOTALL,
    )
    http_pattern = re.compile(
        r"!\[(?P<alt>[^\]]*)\]\((?P<url>[^\s\)]+)(?:\s+(?P<title>(\"[^\"]*\")|('[^']*')|(\([^\)]*\))))?\)(?P<tail>\{[^\}]*\})?"
    )

    download_count = 0
    skip_count = 0
    data_uri_skip = 0
    failures: list[str] = []

    def _build_markdown_path(target: Path) -> str:
        relative = f"./{rel_dir}/{target.name}"
        return escape_markdown_path(relative)

    def _handle_data_uri(match: re.Match[str]) -> str:
        nonlocal data_uri_skip
        alt_text = match.group("alt")
        url = match.group("url")
        tail = match.group("tail") or ""
        if not is_data_uri(url):
            return match.group(0)

        hash_val = hashlib.md5(url.encode()).hexdigest()[:12]
        base_name = f"embedded_{hash_val}"
        base_path = images_dir / base_name
        existing = find_existing_image(base_path)
        if existing:
            data_uri_skip += 1
            log(f"⊙ 已存在，跳过：{existing.name}")
            return f"![{alt_text}]({_build_markdown_path(existing)}){tail}"

        log("📦 处理内嵌图片（base64）...")
        result = save_data_uri_image(url, base_path, log=log)
        if result.ok and result.path:
            log(f"✓ 已保存内嵌图片：{result.path.name}")
            return f"![{alt_text}]({_build_markdown_path(result.path)}){tail}"

        log("   ⚠️  内嵌图片保存失败，保留原内容")
        failures.append(url)
        return match.group(0)

    intermediate = data_uri_pattern.sub(_handle_data_uri, cleaned_content)

    def _handle_http_image(match: re.Match[str]) -> str:
        nonlocal download_count, skip_count
        alt_text = match.group("alt")
        url = match.group("url")
        title = match.groupdict().get("title") or ""
        tail = match.group("tail") or ""

        if title:
            title = f" {title}"

        if is_data_uri(url) or not url.startswith("http"):
            return match.group(0)

        filename = sanitize_filename(url)
        base_name = Path(filename).stem
        base_path = images_dir / base_name

        existing = find_existing_image(base_path)
        if existing:
            skip_count += 1
            log(f"⊙ 已存在，跳过：{existing.name}")
            return f"![{alt_text}]({_build_markdown_path(existing)}{title}){tail}"

        if download_count > 0 and delay > 0:
            time.sleep(delay)

        result: DownloadResult = download_image(url, base_path, downloader=downloader, log=log)
        download_count += 1

        if result.ok and result.path:
            log(f"✓ 已下载：{result.path.name}")
            return f"![{alt_text}]({_build_markdown_path(result.path)}{title}){tail}"

        failures.append(url)
        if result.is_wechat and wechat_placeholder:
            log("   📝 微信图片下载失败，创建占位符...")
            return create_wechat_placeholder(alt_text, url) + tail

        log("   ⚠️  下载失败，保留原链接")
        return match.group(0)

    final_content = http_pattern.sub(_handle_http_image, intermediate)
    skipped_total = skip_count + data_uri_skip
    if skipped_total > 0 or download_count > 0:
        log(
            f"\n📊 统计：跳过 {skipped_total} 个已存在的图片（其中 {data_uri_skip} 个内嵌图片），下载 {download_count} 个新图片"
        )

    return RewriteResult(
        content=final_content,
        skipped=skipped_total,
        downloaded=download_count,
        data_uri_skipped=data_uri_skip,
        failures=failures,
    )
