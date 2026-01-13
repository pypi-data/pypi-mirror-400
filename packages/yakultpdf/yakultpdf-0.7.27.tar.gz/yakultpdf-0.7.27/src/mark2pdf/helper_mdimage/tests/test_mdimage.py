import base64
import hashlib
import sys
import urllib.error
from pathlib import Path
from types import SimpleNamespace

from click.testing import CliRunner
from PIL import Image

# 让 tests 能定位到 src/mark2pdf/helper_mdimage 包
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from mark2pdf.helper_mdimage.mdimage_assets import (
    detect_image_format,
    encode_url_properly,
    escape_markdown_path,
    find_existing_image,
    sanitize_filename,
    save_data_uri_image,
)
from mark2pdf.helper_mdimage.mdimage_cli import main as cli_main
from mark2pdf.helper_mdimage.mdimage_rewrite import DownloadResult, rewrite_markdown_images


def test_data_uri_saved_and_reused(tmp_path: Path) -> None:
    png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/xcAAwMB/6Xn0qsAAAAASUVORK5CYII="
    data_uri = f"data:image/png;base64,{png_b64}"
    content = f"![logo]({data_uri})"
    images_dir = tmp_path / "images" / "sample"

    first = rewrite_markdown_images(
        content,
        images_dir,
        "images/sample",
        delay=0,
        wechat_placeholder=True,
        log=lambda _m: None,
    )
    # 保存了内嵌图片
    assert first.downloaded == 0
    assert first.data_uri_skipped == 0
    hash_val = "embedded_" + __import__("hashlib").md5(data_uri.encode()).hexdigest()[:12]
    saved_path = images_dir / f"{hash_val}.png"
    assert saved_path.exists()
    expected_path = escape_markdown_path(f"./images/sample/{saved_path.name}")
    assert expected_path in first.content

    # 再次运行应走已存在分支
    second = rewrite_markdown_images(
        content,
        images_dir,
        "images/sample",
        delay=0,
        wechat_placeholder=True,
        log=lambda _m: None,
    )
    assert second.data_uri_skipped == 1
    assert second.downloaded == 0
    assert expected_path in second.content


def test_http_download_and_skip(tmp_path: Path) -> None:
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10
    calls = []

    def fake_downloader(url: str, headers: dict) -> bytes:  # type: ignore[override]
        calls.append(url)
        return png_bytes

    urls = [
        "http://example.com/a.png?x=1",
        "http://example.com/long/name.jpg",
    ]
    content = "\n".join(f"![img]({u})" for u in urls)
    images_dir = tmp_path / "images" / "batch"

    first = rewrite_markdown_images(
        content,
        images_dir,
        "images/batch",
        delay=0,
        wechat_placeholder=True,
        downloader=fake_downloader,
        log=lambda _m: None,
    )
    assert first.downloaded == 2
    assert first.skipped == 0
    for url in urls:
        fname = Path(sanitize_filename(url)).stem + ".png"
        assert (images_dir / fname).exists()

    # 二次运行应跳过（无新下载）
    second = rewrite_markdown_images(
        content,
        images_dir,
        "images/batch",
        delay=0,
        wechat_placeholder=True,
        downloader=fake_downloader,
        log=lambda _m: None,
    )
    assert second.downloaded == 0
    assert second.skipped == 2
    # downloader 未被调用再次
    assert len(calls) == 2


def test_wechat_placeholder_on_failure(monkeypatch, tmp_path: Path) -> None:
    def fake_download_image(url: str, base_path: Path, **_: object) -> DownloadResult:
        return DownloadResult(ok=False, path=None, fmt="", error="fail", is_wechat=True)

    from mark2pdf.helper_mdimage import mdimage_rewrite

    monkeypatch.setattr(mdimage_rewrite, "download_image", fake_download_image)

    content = "![wx](https://mmbiz.qpic.cn/abc)"
    images_dir = tmp_path / "images" / "wx"

    result = mdimage_rewrite.rewrite_markdown_images(
        content,
        images_dir,
        "images/wx",
        delay=0,
        wechat_placeholder=True,
        log=lambda _m: None,
    )

    assert result.downloaded == 1  # 尝试过下载
    assert result.skipped == 0
    assert result.failures == ["https://mmbiz.qpic.cn/abc"]
    assert '<div class="wechat-image-placeholder"' in result.content


def test_sanitize_and_encode_rules() -> None:
    url_no_ext = "http://example.com/图像"
    fn = sanitize_filename(url_no_ext)
    expected_hash = hashlib.md5(url_no_ext.encode()).hexdigest()[:6]
    assert fn == f"{expected_hash}.png"

    url_multi_dot = "http://example.com/a.b.c.png?x=1"
    fn2 = sanitize_filename(url_multi_dot)
    assert fn2.startswith("a.b.c_") and fn2.endswith(".png")

    encoded = encode_url_properly("http://example.com/路径/图%20片.png?x=1&y=汉字")
    assert "%E8%B7%AF%E5%BE%84" in encoded
    assert "%20" in encoded and "汉字" not in encoded


def test_sanitize_strange_filenames() -> None:
    # 1. Very long filename
    long_name = "a" * 60 + ".png"
    url_long = f"http://example.com/{long_name}"
    fn_long = sanitize_filename(url_long)
    # Should use hash format because it's too long
    assert fn_long.startswith("img_")
    assert len(fn_long) < 50
    assert fn_long.endswith(".png")

    # 2. Strange characters (URL encoded in filename)
    strange_url = "http://example.com/ai-shape/https_3A_2F_2Fsubstack-post-media.jpeg"
    fn_strange = sanitize_filename(strange_url)
    assert fn_strange.startswith("img_")
    assert "_3A_" not in fn_strange
    assert fn_strange.endswith(".jpeg")

    # 3. Normal filename should keep original stem
    normal_url = "http://example.com/simple.png"
    fn_normal = sanitize_filename(normal_url)
    # Expect: simple_{hash}.png
    assert fn_normal.startswith("simple_")
    assert fn_normal.endswith(".png")


def test_detect_and_existing(tmp_path: Path) -> None:
    png_bytes = b"\x89PNG\r\n\x1a\nxxxx"
    webp_bytes = b"RIFFxxxxWEBPmore"
    assert detect_image_format(png_bytes) == "png"
    assert detect_image_format(webp_bytes) == "webp"

    base = tmp_path / "img"
    (base.with_suffix(".jpeg")).write_bytes(b"abc")
    found = find_existing_image(base)
    assert found and found.suffix == ".jpeg"


def test_save_data_uri_webp_converted(tmp_path: Path) -> None:
    buf = Path(tmp_path / "tmp.webp")
    img = Image.new("RGB", (1, 1), color="red")
    img.save(buf, format="WEBP")
    webp_b64 = base64.b64encode(buf.read_bytes()).decode()
    data_uri = f"data:image/webp;base64,{webp_b64}"

    result = save_data_uri_image(data_uri, tmp_path / "pic", log=lambda _m: None)
    assert result.ok and result.path
    # WebP 会尝试转换为 PNG，允许失败时保留 webp，这里小图应成功
    assert result.path.suffix in {".png", ".webp"}
    assert result.path.exists()


def test_rewrite_skips_local_and_failure_keeps_url(monkeypatch, tmp_path: Path) -> None:
    calls = []

    def fake_download(url: str, base_path: Path, **_: object) -> DownloadResult:
        calls.append(url)
        return DownloadResult(ok=False, path=None, fmt="", error="fail", is_wechat=False)

    from mark2pdf.helper_mdimage import mdimage_rewrite

    monkeypatch.setattr(mdimage_rewrite, "download_image", fake_download)

    content = "\n".join(
        [
            "![local](./local.png)",
            "![http](http://example.com/x.png)",
        ]
    )
    result = mdimage_rewrite.rewrite_markdown_images(
        content,
        tmp_path / "images" / "mix",
        "images/mix",
        delay=0,
        wechat_placeholder=False,
        log=lambda _m: None,
    )
    assert "local.png" in result.content
    assert "http://example.com/x.png" in result.content
    assert result.downloaded == 1
    assert result.failures == ["http://example.com/x.png"]
    assert calls == ["http://example.com/x.png"]


def test_multiple_images_same_line_and_tail_attrs(monkeypatch, tmp_path: Path) -> None:
    png_bytes = b"\x89PNG\r\n\x1a\nxxxx"
    urls = [
        "http://host/_next/image?url=https%3A%2F%2Fcdn.com%2Fa.png&w=1080&q=75",
        "http://cdn.com/b.avif",
        "http://cdn.com/c.png",
    ]

    downloaded = []

    def fake_downloader(url: str, headers: dict) -> bytes:  # type: ignore[override]
        downloaded.append(url)
        return png_bytes

    content = f"![one]({urls[0]}){{.width40}} ![two]({urls[1]}) ![three]({urls[2]}) text"
    result = rewrite_markdown_images(
        content,
        tmp_path / "images" / "line",
        "images/line",
        delay=0,
        wechat_placeholder=False,
        downloader=fake_downloader,
        log=lambda _m: None,
    )
    assert result.downloaded == 3
    assert result.content.count("./images/line/") == 3
    assert "{.width40}" in result.content  # 属性保留
    # _next/image 无扩展，文件名应为 hash.png（转换后 .png）
    filenames = list((tmp_path / "images" / "line").iterdir())
    assert any(f.name.endswith(".png") for f in filenames)


def test_contentful_and_devto_queries_preserved(monkeypatch, tmp_path: Path) -> None:
    png_bytes = b"\x89PNG\r\n\x1a\nxxxx"
    calls = []

    def fake_downloader(url: str, headers: dict) -> bytes:  # type: ignore[override]
        calls.append(url)
        return png_bytes

    contentful = "https://images.ctfassets.net/path/img.png?fm=png&q=80"
    devto = "https://dev.to/_next/image?url=https%253A%252F%252Fcdn.dev.to%252Fimg.png&w=750&h=420&fit=crop&auto=format%2Ccompress&q=75"
    content = f"![c]({contentful})\n![d]({devto})"

    result = rewrite_markdown_images(
        content,
        tmp_path / "images" / "queries",
        "images/queries",
        delay=0,
        wechat_placeholder=False,
        downloader=fake_downloader,
        log=lambda _m: None,
    )
    assert result.downloaded == 2
    assert any("ctfassets" in u and "fm=png" in u and "q=80" in u for u in calls)
    assert any("_next/image" in u and "auto=format,compress" in u for u in calls)


def test_local_path_with_space_skipped(tmp_path: Path) -> None:
    content = "![local](./images/justification finalization.png)"
    result = rewrite_markdown_images(
        content,
        tmp_path / "images" / "space",
        "images/space",
        delay=0,
        wechat_placeholder=False,
        log=lambda _m: None,
    )
    assert "justification finalization.png" in result.content
    assert result.downloaded == 0
    assert result.skipped == 0


def test_download_image_retry(monkeypatch, tmp_path: Path) -> None:
    png_bytes = b"\x89PNG\r\n\x1a\nxxxx"
    attempts = {"count": 0}

    def fake_downloader(url: str, headers: dict) -> bytes:  # type: ignore[override]
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise urllib.error.HTTPError(url, 429, "rate", {}, None)
        return png_bytes

    # 跳过实际 sleep
    import mark2pdf.helper_mdimage.mdimage_assets as assets

    monkeypatch.setattr(assets.time, "sleep", lambda _s: None)
    result = assets.download_image(
        "http://example.com/a.png",
        tmp_path / "images" / "retry" / "a",
        downloader=fake_downloader,
        retry_delay=0.01,
        log=lambda _m: None,
    )
    assert result.ok
    assert attempts["count"] == 2
    assert result.path and result.path.exists()


def test_download_image_wechat_403_retry(monkeypatch, tmp_path: Path) -> None:
    png_bytes = b"\x89PNG\r\n\x1a\nxxxx"
    attempts = {"count": 0}

    def fake_downloader(url: str, headers: dict) -> bytes:  # type: ignore[override]
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise urllib.error.HTTPError(url, 403, "forbidden", {}, None)
        return png_bytes

    import mark2pdf.helper_mdimage.mdimage_assets as assets

    monkeypatch.setattr(assets.time, "sleep", lambda _s: None)
    result = assets.download_image(
        "https://mmbiz.qpic.cn/abc?wxfrom=5",
        tmp_path / "images" / "wx403" / "img",
        downloader=fake_downloader,
        retry_delay=0.01,
        log=lambda _m: None,
    )
    assert attempts["count"] == 2
    assert result.ok and result.is_wechat
    assert result.path and result.path.exists()


def test_cli_resolves_config_input_dir(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "mark2pdf.config.toml"
    config_path.write_text('[paths]\nin = "in"\n', encoding="utf-8")
    input_dir = tmp_path / "in"
    input_dir.mkdir(parents=True)
    md_file = input_dir / "demo.md"
    md_file.write_text("hello", encoding="utf-8")

    captured = {}

    def fake_rewrite(content: str, images_dir: Path, rel_dir: str, **kwargs) -> SimpleNamespace:
        captured["content"] = content
        captured["images_dir"] = images_dir
        captured["rel_dir"] = rel_dir
        return SimpleNamespace(content="processed", skipped=0, downloaded=0)

    monkeypatch.chdir(tmp_path)
    import mark2pdf.helper_mdimage.mdimage_cli as cli

    monkeypatch.setattr(cli, "rewrite_markdown_images", fake_rewrite)

    runner = CliRunner()
    result = runner.invoke(cli_main, ["demo.md", "--delay", "0"])
    assert result.exit_code == 0
    # 应当写入 *_processed.md
    out_path = input_dir / "demo_processed.md"
    assert out_path.read_text(encoding="utf-8") == "processed"
    assert captured["rel_dir"] == "images/demo"


def test_cli_directory_mode(monkeypatch, tmp_path: Path) -> None:
    md_dir = tmp_path / "docs"
    md_dir.mkdir()
    (md_dir / "a.md").write_text("a", encoding="utf-8")
    (md_dir / "b.md").write_text("b", encoding="utf-8")

    calls = []

    def fake_rewrite(content: str, images_dir: Path, rel_dir: str, **kwargs) -> SimpleNamespace:
        calls.append((content, images_dir, rel_dir))
        return SimpleNamespace(content="processed_" + rel_dir, skipped=0, downloaded=0)

    import mark2pdf.helper_mdimage.mdimage_cli as cli

    monkeypatch.setattr(cli, "rewrite_markdown_images", fake_rewrite)

    runner = CliRunner()
    result = runner.invoke(cli_main, [str(md_dir), "--delay", "0"])
    assert result.exit_code == 0
    assert len(calls) == 2
    # 输出文件存在且内容来自 fake_rewrite
    assert (
        (md_dir / "a_processed.md").read_text(encoding="utf-8").startswith("processed_images/docs")
    )
    assert (
        (md_dir / "b_processed.md").read_text(encoding="utf-8").startswith("processed_images/docs")
    )


def test_resolve_image_mode_defaults_to_folder(tmp_path: Path) -> None:
    md_file = tmp_path / "demo.md"
    md_file.write_text("content", encoding="utf-8")

    import mark2pdf.helper_mdimage.mdimage_cli as cli

    mode = cli.resolve_image_mode(md_file)
    assert mode.name == "folder"
    assert mode.images_dir == tmp_path / "images"
    assert mode.rel_dir == "images"


def test_process_path_auto_single_file_defaults_to_folder(monkeypatch, tmp_path: Path) -> None:
    md_file = tmp_path / "demo.md"
    md_file.write_text("content", encoding="utf-8")

    captured = {}

    def fake_rewrite(content: str, images_dir: Path, rel_dir: str, **kwargs) -> SimpleNamespace:
        captured["images_dir"] = images_dir
        captured["rel_dir"] = rel_dir
        return SimpleNamespace(content="processed", skipped=0, downloaded=0)

    import mark2pdf.helper_mdimage.mdimage_cli as cli

    monkeypatch.setattr(cli, "rewrite_markdown_images", fake_rewrite)

    cli.process_path_auto(
        md_file,
        delay=0,
        wechat_placeholder=True,
        overwrite=False,
        log=lambda _m: None,
    )

    assert captured["images_dir"] == tmp_path / "images"
    assert captured["rel_dir"] == "images"
    assert (tmp_path / "demo_processed.md").read_text(encoding="utf-8") == "processed"


def test_process_path_auto_directory_defaults_to_folder(monkeypatch, tmp_path: Path) -> None:
    md_dir = tmp_path / "docs"
    md_dir.mkdir()
    (md_dir / "a.md").write_text("a", encoding="utf-8")
    (md_dir / "b.md").write_text("b", encoding="utf-8")

    calls = []

    def fake_rewrite(content: str, images_dir: Path, rel_dir: str, **kwargs) -> SimpleNamespace:
        calls.append((images_dir, rel_dir))
        return SimpleNamespace(content="processed", skipped=0, downloaded=0)

    import mark2pdf.helper_mdimage.mdimage_cli as cli

    monkeypatch.setattr(cli, "rewrite_markdown_images", fake_rewrite)

    cli.process_path_auto(
        md_dir,
        delay=0,
        wechat_placeholder=True,
        overwrite=False,
        log=lambda _m: None,
    )

    assert len(calls) == 2
    for images_dir, rel_dir in calls:
        assert images_dir == md_dir / "images"
        assert rel_dir == "images"


def test_cli_rejects_non_md_file(tmp_path: Path) -> None:
    md_file = tmp_path / "note.markdown"
    md_file.write_text("content", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli_main, [str(md_file)])
    assert result.exit_code != 0
    assert "仅支持 .md 文件" in result.output


def test_remove_image_links_wrapping_images() -> None:
    from mark2pdf.helper_mdimage.mdimage_rewrite import remove_image_links_wrapping_images

    # Case 1: Simple wrap -> unwrap
    content = "[![img](http://example.com/a.png)](http://example.com/a.png)"
    assert remove_image_links_wrapping_images(content) == "![img](http://example.com/a.png)"

    # Case 2: Wrap with title -> unwrap
    content = '[![img](http://example.com/a.png "Title")](http://example.com/a.png)'
    assert remove_image_links_wrapping_images(content) == '![img](http://example.com/a.png "Title")'

    # Case 3: Substack fetch URL -> unwrap
    content = "[![a](https://substackcdn.com/image/fetch/w_1456/url.jpg)](https://substackcdn.com/image/fetch/url.jpg)"
    assert (
        remove_image_links_wrapping_images(content)
        == "![a](https://substackcdn.com/image/fetch/w_1456/url.jpg)"
    )

    # Case 4: Profile link -> keep
    content = "[![avatar](http://example.com/a.png)](https://substack.com/@user)"
    assert remove_image_links_wrapping_images(content).strip() == content.strip()

    # Case 5: Non-image, non-profile link -> keep (heuristic default)
    content = "[![img](http://example.com/a.png)](http://example.com/page)"
    assert remove_image_links_wrapping_images(content).strip() == content.strip()

    # Case 6: Twitter/X media link -> unwrap
    content = "[![Image](https://pbs.twimg.com/media.png)](https://x.com/user/status/123/media/456)"
    assert (
        remove_image_links_wrapping_images(content).strip()
        == "![Image](https://pbs.twimg.com/media.png)"
    )
