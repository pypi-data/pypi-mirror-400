from __future__ import annotations

import base64
import hashlib
import io
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


# 简单的默认日志函数，便于在测试时替换
def _noop_logger(message: str) -> None:
    return None


def clear_copy_image(content: str) -> str:
    """移除尾随 `Copy Image` 的图片标记。"""
    pattern = r"!\[([^\]]*)\]\(([^\)]+)\)\s*Copy\s+Image\s*\n?"
    return re.sub(pattern, "", content, flags=re.IGNORECASE)


def sanitize_filename(url: str) -> str:
    """基于 URL 生成稳定文件名，追加短哈希并清理非法字符。"""
    parsed = urllib.parse.urlparse(url)
    name = Path(parsed.path).name
    url_hash = hashlib.md5(url.encode()).hexdigest()[:6]

    if not name or "." not in name:
        filename = f"{url_hash}.png"
    else:
        stem = Path(name).stem
        suffix = Path(name).suffix

        # 检查是否为“奇怪”的文件名
        # 1. 长度超过 50
        # 2. 包含 _3A (:) 或 _2F (/) 这种 URL 转义痕迹
        is_strange = len(stem) > 50 or "_3A" in stem or "_2F" in stem

        if is_strange:
            filename = f"img_{url_hash}{suffix}"
        else:
            filename = f"{stem}_{url_hash}{suffix}"

    return re.sub(r"[^\w\-_\.]", "_", filename)


def escape_markdown_path(path: str) -> str:
    """仅转义 Markdown 路径中的下划线。"""
    return path.replace("_", r"\_")


def encode_url_properly(url: str, log: Callable[[str], None] = _noop_logger) -> str:
    """重新编码 URL 的 path/query，保留已有的 %。"""
    try:
        parsed = urllib.parse.urlsplit(url)
        encoded_path = urllib.parse.quote(parsed.path, safe="/%:@-._~!$,")

        encoded_query = ""
        if parsed.query:
            pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
            encoded_query = "&".join(
                f"{urllib.parse.quote(k, safe='-_.~%!$,')}={urllib.parse.quote(v, safe='-_.~%!$,')}"
                for k, v in pairs
            )

        encoded_url = urllib.parse.urlunsplit(
            (parsed.scheme, parsed.netloc, encoded_path, encoded_query, parsed.fragment)
        )
        if encoded_url != url:
            log(f"   🔧 URL编码：{url[:60]}... -> {encoded_url[:60]}...")
        return encoded_url
    except Exception as exc:  # pragma: no cover - 防御性日志
        log(f"   ⚠️  URL编码失败，使用原始URL：{exc}")
        return url


def is_wechat_image(url: str) -> bool:
    return "mmbiz.qpic.cn" in url.lower() or "mp.weixin.qq.com" in url.lower()


def clean_wechat_image_url(url: str) -> str:
    params_to_remove = {"wxfrom", "wx_lazy", "tp"}
    parsed = urllib.parse.urlsplit(url)
    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    filtered = [(k, v) for k, v in query_pairs if k not in params_to_remove]
    if not any(k == "wx_fmt" for k, _ in filtered):
        filtered.append(("wx_fmt", "jpeg"))
    new_query = urllib.parse.urlencode(filtered, doseq=True)
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment)
    )


def get_wechat_headers(url: str) -> dict[str, str]:
    referer = "https://mp.weixin.qq.com/"
    match = re.search(r"mp\.weixin\.qq\.com/s/([a-zA-Z0-9_-]+)", url)
    if match:
        referer = f"https://mp.weixin.qq.com/s/{match.group(1)}"
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": referer,
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }


def detect_image_format(data: bytes) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "gif"
    if data.startswith(b"RIFF") and len(data) > 12 and data[8:12] == b"WEBP":
        return "webp"
    if data.startswith(b"BM"):
        return "bmp"
    if data.startswith(b"\x00\x00\x01\x00"):
        return "ico"
    if b"<svg" in data[:1024] or data.startswith(b"<?xml"):
        return "svg"
    return "png"


def is_data_uri(url: str) -> bool:
    return url.strip().lower().startswith("data:image/")


def find_existing_image(base_path: Path) -> Path | None:
    for ext in ["png", "jpeg", "jpg", "gif", "webp", "bmp", "ico", "svg"]:
        candidate = Path(f"{base_path}.{ext}")
        if candidate.exists():
            return candidate
    return None


def _default_downloader(url: str, headers: dict[str, str]) -> bytes:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def _convert_webp_to_png(data: bytes, log: Callable[[str], None]) -> bytes | None:
    try:
        image = Image.open(io.BytesIO(data))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
    except Exception as exc:
        log(f"   ⚠️  WebP 转换失败，保留原格式：{exc}")
        return None


@dataclass
class DownloadResult:
    ok: bool
    path: Path | None
    fmt: str = ""
    error: str | None = None
    is_wechat: bool = False


def save_image_bytes(
    data: bytes, base_path: Path, log: Callable[[str], None] = _noop_logger
) -> tuple[Path, str]:
    fmt = detect_image_format(data)
    if fmt == "webp":
        converted = _convert_webp_to_png(data, log)
        if converted is not None:
            data = converted
            fmt = "png"
    save_path = Path(f"{base_path}.{fmt}")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "wb") as fh:
        fh.write(data)
    return save_path, fmt


def save_data_uri_image(
    data_uri: str, base_path: Path, log: Callable[[str], None] = _noop_logger
) -> DownloadResult:
    try:
        match = re.match(r"data:image/([^;]+);base64,(.+)", data_uri.strip(), re.DOTALL)
        if not match:
            return DownloadResult(False, None, error="data uri parse failed")
        encoded = match.group(2)
        try:
            data = base64.b64decode(encoded)
        except Exception as exc:
            log(f"   ⚠️  Base64 解码失败：{exc}")
            return DownloadResult(False, None, error="base64 decode failed")
        path, fmt = save_image_bytes(data, base_path, log=log)
        return DownloadResult(True, path, fmt=fmt)
    except Exception as exc:  # pragma: no cover - 防御性
        log(f"   ❌ 保存 data URI 图片失败：{exc}")
        return DownloadResult(False, None, error=str(exc))


def download_image(
    url: str,
    base_path: Path,
    *,
    downloader: Callable[[str, dict[str, str]], bytes] | None = None,
    max_retries: int = 3,
    retry_delay: float = 2.0,
    log: Callable[[str], None] = _noop_logger,
) -> DownloadResult:
    downloader_func = downloader or _default_downloader
    encoded_url = encode_url_properly(url, log=log)
    is_wechat = is_wechat_image(encoded_url)

    if is_wechat:
        download_url = clean_wechat_image_url(encoded_url)
        headers = get_wechat_headers(encoded_url)
        log(f"   🔧 微信图片特殊处理：{download_url[:50]}...")
    else:
        download_url = encoded_url
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        }

    last_error: str | None = None

    for attempt in range(max_retries):
        try:
            data = downloader_func(download_url, headers)
            path, fmt = save_image_bytes(data, base_path, log=log)
            return DownloadResult(True, path, fmt=fmt, is_wechat=is_wechat)
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            log(f"   🔍 HTTP错误详情：状态码={exc.code}, 原因={getattr(exc, 'reason', 'unknown')}")
            if exc.code == 429 and attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)
                log(
                    f"⚠️  请求过于频繁 (429)，等待 {wait_time:.1f} 秒后重试... (尝试 {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
                continue
            if exc.code == 403 and is_wechat and attempt < max_retries - 1:
                log("⚠️  微信图片访问被拒绝 (403)，尝试移除 wxfrom 参数重试...")
                stripped = (
                    download_url.replace("&wxfrom=5", "")
                    .replace("wxfrom=5&", "")
                    .replace("?wxfrom=5", "")
                )
                download_url = stripped
                time.sleep(retry_delay)
                continue
            return DownloadResult(False, None, fmt="", error=last_error, is_wechat=is_wechat)
        except Exception as exc:
            last_error = str(exc)
            if attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)
                log(
                    f"⚠️  下载出错，等待 {wait_time:.1f} 秒后重试... (尝试 {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
                continue
            return DownloadResult(False, None, fmt="", error=last_error, is_wechat=is_wechat)

    return DownloadResult(False, None, fmt="", error=last_error, is_wechat=is_wechat)


def create_wechat_placeholder(alt_text: str, img_url: str) -> str:
    img_index_match = re.search(r"#imgIndex=(\d+)", img_url)
    img_index = img_index_match.group(1) if img_index_match else "?"
    label = alt_text if alt_text and alt_text != "图片" else "图片内容"
    return f"""
<div class="wechat-image-placeholder" style="
    border: 2px dashed #ccc; 
    padding: 20px; 
    margin: 10px 0; 
    text-align: center; 
    background-color: #f9f9f9;
    border-radius: 8px;
">
    <p style="color: #666; margin: 0;">📷 微信图片 #{img_index}</p>
    <p style="color: #999; font-size: 12px; margin: 5px 0 0 0;">
        原始链接: <a href="{img_url}" target="_blank">点击查看</a>
    </p>
    <p style="color: #999; font-size: 12px; margin: 0;">
        {label}
    </p>
</div>
"""
