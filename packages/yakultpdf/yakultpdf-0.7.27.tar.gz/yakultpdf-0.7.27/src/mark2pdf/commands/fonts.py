"""
mark2pdf 字体管理命令

提供字体下载与安装功能。
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

import click

from ..config import ConfigManager

_FONT_EXTENSIONS = (".ttf", ".otf", ".ttc", ".otc")


@dataclass(frozen=True)
class FontSpec:
    key: str
    title: str
    repo: str
    asset_patterns: tuple[str, ...]
    license: str
    note: str = ""


_FONT_CATALOG = {
    "source-han-sans": FontSpec(
        key="source-han-sans",
        title="思源黑体 SC",
        repo="adobe-fonts/source-han-sans",
        asset_patterns=(
            "sourcehansanssc",
            "source-han-sans-sc",
        ),
        license="SIL OFL 1.1",
    ),
    "source-han-serif": FontSpec(
        key="source-han-serif",
        title="思源宋体 SC",
        repo="adobe-fonts/source-han-serif",
        asset_patterns=(
            "sourcehanserifsc",
            "source-han-serif-sc",
        ),
        license="SIL OFL 1.1",
    ),
    "lxgw-wenkai": FontSpec(
        key="lxgw-wenkai",
        title="霞鹜文楷",
        repo="lxgw/LxgwWenKai",
        asset_patterns=(
            "lxgwwenkai-regular",
            "lxgwwenkai",
        ),
        license="SIL OFL 1.1",
    ),
    "yozai": FontSpec(
        key="yozai",
        title="悠哉字体",
        repo="lxgw/yozai-font",
        asset_patterns=(
            "yozai-regular",
            "yozai",
        ),
        license="SIL OFL 1.1",
        note="测试用字体，通常系统未预装",
    ),
}


def _resolve_fonts_dir(target_dir: str | None) -> Path:
    if target_dir:
        return Path(target_dir).expanduser().resolve()

    config = ConfigManager.load()
    try:
        fonts_dir = config.fonts_dir
    except Exception:
        fonts_dir = None

    if fonts_dir is not None:
        return fonts_dir

    data_root = getattr(config, "data_root", None)
    if data_root is not None:
        return Path(data_root) / "fonts"

    return Path.cwd() / "fonts"


def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "mark2pdf-fonts",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _download_headers(url: str) -> dict[str, str]:
    host = urllib.parse.urlsplit(url).netloc.lower()
    if host.endswith("github.com") or host.endswith("githubusercontent.com"):
        return _github_headers()
    return {"User-Agent": "mark2pdf-fonts"}


def _fetch_latest_release(repo: str) -> dict:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    request = urllib.request.Request(url, headers=_github_headers())
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise click.ClickException(f"无法获取发布信息（HTTP {exc.code}）：{repo}") from exc
    except urllib.error.URLError as exc:
        raise click.ClickException(f"无法连接到 GitHub：{exc}") from exc


def _select_asset(release: dict, patterns: tuple[str, ...]) -> dict:
    assets = release.get("assets") or []
    if not assets:
        raise click.ClickException("未找到发布资产，请稍后重试或指定 --url")

    for pattern in patterns:
        pattern_lower = pattern.lower()
        matches = []
        for asset in assets:
            name = str(asset.get("name", ""))
            if pattern_lower in name.lower():
                matches.append(asset)
        if matches:
            ext_priority = (".zip", ".ttf", ".otf", ".ttc", ".otc")

            def _score(a: dict) -> int:
                name = str(a.get("name", "")).lower()
                for idx, ext in enumerate(ext_priority):
                    if name.endswith(ext):
                        return idx
                return len(ext_priority)

            matches.sort(key=_score)
            return matches[0]

    asset_names = ", ".join(str(a.get("name", "")) for a in assets if a.get("name"))
    raise click.ClickException(f"未找到匹配的字体包，候选资产：{asset_names}")


def _download_file(url: str, dest_path: Path) -> None:
    headers = _download_headers(url)
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(response, f)
    except urllib.error.HTTPError as exc:
        raise click.ClickException(f"下载失败（HTTP {exc.code}）：{url}") from exc
    except urllib.error.URLError as exc:
        raise click.ClickException(f"下载失败：{exc}") from exc


def _extract_fonts_from_zip(zip_path: Path, target_dir: Path, force: bool) -> list[Path]:
    extracted: list[Path] = []
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = Path(info.filename).name
            if not name.lower().endswith(_FONT_EXTENSIONS):
                continue
            dest = target_dir / name
            if dest.exists() and not force:
                continue
            with zf.open(info) as src, open(dest, "wb") as dst:
                shutil.copyfileobj(src, dst)
            extracted.append(dest)
    return extracted


def _install_from_url(
    url: str,
    target_dir: Path,
    force: bool,
    keep_archive: bool,
    asset_name: str | None = None,
) -> list[Path]:
    target_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(prefix="mark2pdf-fonts-"))
    parsed = urllib.parse.urlsplit(url)
    filename = asset_name or Path(parsed.path).name or "font_download"
    download_path = tmp_dir / filename

    click.echo(f"下载字体包：{url}")
    _download_file(url, download_path)

    extracted: list[Path] = []
    if zipfile.is_zipfile(download_path):
        extracted = _extract_fonts_from_zip(download_path, target_dir, force)
    else:
        suffix = download_path.suffix.lower()
        if suffix in _FONT_EXTENSIONS:
            dest = target_dir / download_path.name
            if dest.exists() and not force:
                extracted = []
            else:
                shutil.copy2(download_path, dest)
                extracted = [dest]
        else:
            raise click.ClickException(f"不支持的字体包类型：{download_path.name}")

    if keep_archive:
        archive_dir = target_dir / ".archives"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / download_path.name
        if archive_path.exists() and not force:
            click.echo(f"警告：归档已存在，已跳过保存：{archive_path}")
        else:
            shutil.copy2(download_path, archive_path)
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return extracted


@click.group()
def fonts():
    """字体管理（下载/安装/查看）"""


@fonts.command("list")
def list_fonts():
    """列出可安装字体"""
    click.echo("可安装字体：")
    for spec in _FONT_CATALOG.values():
        note = f" ({spec.note})" if spec.note else ""
        click.echo(f"  {spec.key:16s} - {spec.title}{note} [{spec.license}]")


@fonts.command("install")
@click.argument("font_name", required=False)
@click.option("--url", "download_url", help="直接提供字体下载地址")
@click.option("--dir", "target_dir", help="指定安装目录")
@click.option("--force", is_flag=True, help="覆盖同名字体文件")
@click.option("--keep-archive", is_flag=True, help="保留下载的归档文件")
def install_font(
    font_name: str | None,
    download_url: str | None,
    target_dir: str | None,
    force: bool,
    keep_archive: bool,
):
    """下载并安装字体"""
    if not font_name and not download_url:
        raise click.UsageError("请提供字体名称或使用 --url 指定下载地址")

    fonts_dir = _resolve_fonts_dir(target_dir)

    if download_url:
        extracted = _install_from_url(
            download_url, fonts_dir, force=force, keep_archive=keep_archive
        )
        if extracted:
            click.echo(f"已安装 {len(extracted)} 个字体到 {fonts_dir}")
        else:
            click.echo("警告：未安装任何字体文件（可能已存在）")
        return

    spec = _FONT_CATALOG.get(font_name or "")
    if spec is None:
        names = ", ".join(sorted(_FONT_CATALOG.keys()))
        raise click.ClickException(f"未知字体：{font_name}\n可选：{names}")

    release = _fetch_latest_release(spec.repo)
    asset = _select_asset(release, spec.asset_patterns)
    url = asset.get("browser_download_url")
    if not url:
        raise click.ClickException("未获取到下载链接，请稍后重试")

    extracted = _install_from_url(
        url, fonts_dir, force=force, keep_archive=keep_archive, asset_name=asset.get("name")
    )
    if extracted:
        click.echo(f"已安装 {spec.title} 到 {fonts_dir}")
    else:
        click.echo("警告：未安装任何字体文件（可能已存在）")


@fonts.command("status")
@click.option("--dir", "target_dir", help="指定字体目录")
def status_fonts(target_dir: str | None):
    """查看已安装字体"""
    fonts_dir = _resolve_fonts_dir(target_dir)
    click.echo(f"字体目录：{fonts_dir}")
    if not fonts_dir.exists():
        click.echo("警告：字体目录不存在")
        return

    fonts = sorted(
        p.relative_to(fonts_dir)
        for p in fonts_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in _FONT_EXTENSIONS
    )

    if not fonts:
        click.echo("（未找到字体文件）")
        return

    click.echo(f"已安装字体：{len(fonts)} 个")
    for font in fonts:
        click.echo(f"  - {font}")
