import sys
from pathlib import Path

import click
import pytest

# 让 tests 能定位到 src/mark2pdf/helper_mdimage 包
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from mark2pdf.helper_mdimage.mdimage_migrate import StructureMigrator


def test_migrate_to_folder_moves_and_rewrites(tmp_path: Path) -> None:
    md_path = tmp_path / "note.md"
    content = (
        "![a](images/note/one.png)\n"
        "![b](./images/note/two.jpg)\n"
        "![c](images/other/keep.png)\n"
        "![remote](http://example.com/a.png)\n"
        "![data](data:image/png;base64,AAAA)\n"
    )
    md_path.write_text(content, encoding="utf-8")

    images_src = tmp_path / "images" / "note"
    images_src.mkdir(parents=True)
    (images_src / "one.png").write_text("one", encoding="utf-8")
    (images_src / "two.jpg").write_text("two", encoding="utf-8")

    migrator = StructureMigrator(log=lambda _m: None)
    migrator.migrate_to_folder(md_path)

    target_md = tmp_path / "note" / "index.md"
    assert target_md.exists()
    assert not md_path.exists()

    assert (tmp_path / "note" / "images" / "one.png").exists()
    assert (tmp_path / "note" / "images" / "two.jpg").exists()
    assert not images_src.exists()

    updated = target_md.read_text(encoding="utf-8")
    assert "![a](images/one.png)" in updated
    assert "![b](./images/two.jpg)" in updated
    assert "![c](images/other/keep.png)" in updated
    assert "http://example.com/a.png" in updated
    assert "data:image/png;base64,AAAA" in updated


def test_migrate_to_folder_keep_original(tmp_path: Path) -> None:
    md_path = tmp_path / "note.md"
    content = "![a](images/note/one.png)\n"
    md_path.write_text(content, encoding="utf-8")

    images_src = tmp_path / "images" / "note"
    images_src.mkdir(parents=True)
    (images_src / "one.png").write_text("one", encoding="utf-8")

    migrator = StructureMigrator(log=lambda _m: None)
    migrator.migrate_to_folder(md_path, keep_original=True)

    target_md = tmp_path / "note" / "index.md"
    assert target_md.exists()
    assert md_path.exists()
    assert images_src.exists()
    assert (images_src / "one.png").exists()
    assert (tmp_path / "note" / "images" / "one.png").exists()

    assert md_path.read_text(encoding="utf-8") == content
    assert "![a](images/one.png)" in target_md.read_text(encoding="utf-8")


def test_migrate_to_folder_finds_images_by_reference(tmp_path: Path) -> None:
    md_path = tmp_path / "note.md"
    content = "![a](images/note/one.png)\n"
    md_path.write_text(content, encoding="utf-8")

    images_dir = tmp_path / "images"
    images_dir.mkdir(parents=True)
    (images_dir / "one.png").write_text("one", encoding="utf-8")

    migrator = StructureMigrator(log=lambda _m: None)
    migrator.migrate_to_folder(md_path, keep_original=True)

    target_md = tmp_path / "note" / "index.md"
    assert target_md.exists()
    assert md_path.exists()
    assert (tmp_path / "note" / "images" / "one.png").exists()
    assert (images_dir / "one.png").exists()
    assert "![a](images/one.png)" in target_md.read_text(encoding="utf-8")


def test_migrate_to_folder_handles_escaped_paths(tmp_path: Path) -> None:
    md_path = tmp_path / "note.md"
    content = r"![a](./images/note/a\_b.png)\n"
    md_path.write_text(content, encoding="utf-8")

    images_dir = tmp_path / "images" / "note"
    images_dir.mkdir(parents=True)
    (images_dir / "a_b.png").write_text("one", encoding="utf-8")

    migrator = StructureMigrator(log=lambda _m: None)
    migrator.migrate_to_folder(md_path, keep_original=True)

    target_md = tmp_path / "note" / "index.md"
    assert (tmp_path / "note" / "images" / "a_b.png").exists()
    assert r"![a](./images/a\_b.png)" in target_md.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("input_name", "companion_name", "images_prefix"),
    [
        ("ai-shape_processed", "ai-shape", "ai-shape"),
        ("cc_zh", "cc", "cc"),
    ],
)
def test_migrate_to_folder_moves_companion(
    tmp_path: Path, input_name: str, companion_name: str, images_prefix: str
) -> None:
    input_path = tmp_path / f"{input_name}.md"
    companion_path = tmp_path / f"{companion_name}.md"
    content = f"![a](./images/{images_prefix}/one.png)\n"
    input_path.write_text(content, encoding="utf-8")
    companion_path.write_text(content, encoding="utf-8")

    images_dir = tmp_path / "images" / images_prefix
    images_dir.mkdir(parents=True)
    (images_dir / "one.png").write_text("one", encoding="utf-8")

    migrator = StructureMigrator(log=lambda _m: None)
    migrator.migrate_to_folder(input_path, keep_original=False)

    target_dir = tmp_path / input_name
    assert not input_path.exists()
    assert not companion_path.exists()
    assert (target_dir / "index.md").exists()
    assert (target_dir / f"{companion_name}.md").exists()
    assert (target_dir / "images" / "one.png").exists()
    assert "images/one.png" in (target_dir / f"{companion_name}.md").read_text(encoding="utf-8")


def test_migrate_to_file_moves_and_rewrites(tmp_path: Path) -> None:
    folder = tmp_path / "note"
    folder.mkdir()
    md_path = folder / "index.md"
    content = "![a](images/one.png)\n![b](./images/two.jpg)\n![c](images/note/already.png)\n"
    md_path.write_text(content, encoding="utf-8")

    images_src = folder / "images"
    images_src.mkdir()
    (images_src / "one.png").write_text("one", encoding="utf-8")
    (images_src / "two.jpg").write_text("two", encoding="utf-8")
    (images_src / "already.png").write_text("three", encoding="utf-8")

    migrator = StructureMigrator(log=lambda _m: None)
    migrator.migrate_to_file(folder)

    target_md = tmp_path / "note.md"
    assert target_md.exists()
    assert not md_path.exists()

    images_dest = tmp_path / "images" / "note"
    assert (images_dest / "one.png").exists()
    assert (images_dest / "two.jpg").exists()
    assert (images_dest / "already.png").exists()
    assert not folder.exists()

    updated = target_md.read_text(encoding="utf-8")
    assert "![a](images/note/one.png)" in updated
    assert "![b](./images/note/two.jpg)" in updated
    assert "![c](images/note/already.png)" in updated


def test_migrate_to_file_finds_images_by_reference(tmp_path: Path) -> None:
    folder = tmp_path / "note"
    folder.mkdir()
    md_path = folder / "index.md"
    content = "![a](images/note/one.png)\n"
    md_path.write_text(content, encoding="utf-8")

    images_dir = tmp_path / "images"
    images_dir.mkdir(parents=True)
    (images_dir / "one.png").write_text("one", encoding="utf-8")

    migrator = StructureMigrator(log=lambda _m: None)
    migrator.migrate_to_file(folder, keep_original=True)

    target_md = tmp_path / "note.md"
    assert target_md.exists()
    assert folder.exists()
    assert md_path.exists()
    assert (images_dir / "one.png").exists()
    assert (tmp_path / "images" / "note" / "one.png").exists()
    assert "![a](images/note/one.png)" in target_md.read_text(encoding="utf-8")


def test_migrate_to_file_keep_original(tmp_path: Path) -> None:
    folder = tmp_path / "note"
    folder.mkdir()
    md_path = folder / "index.md"
    content = "![a](images/one.png)\n"
    md_path.write_text(content, encoding="utf-8")

    images_src = folder / "images"
    images_src.mkdir()
    (images_src / "one.png").write_text("one", encoding="utf-8")

    migrator = StructureMigrator(log=lambda _m: None)
    migrator.migrate_to_file(folder, keep_original=True)

    target_md = tmp_path / "note.md"
    assert target_md.exists()
    assert folder.exists()
    assert md_path.exists()
    assert images_src.exists()
    assert (images_src / "one.png").exists()

    images_dest = tmp_path / "images" / "note"
    assert (images_dest / "one.png").exists()
    assert md_path.read_text(encoding="utf-8") == content
    assert "![a](images/note/one.png)" in target_md.read_text(encoding="utf-8")


def test_migrate_to_file_requires_single_markdown(tmp_path: Path) -> None:
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "a.md").write_text("a", encoding="utf-8")
    (folder / "b.md").write_text("b", encoding="utf-8")

    migrator = StructureMigrator(log=lambda _m: None)
    with pytest.raises(click.ClickException):
        migrator.migrate_to_file(folder)


def test_migrate_to_folder_rejects_non_md(tmp_path: Path) -> None:
    md_path = tmp_path / "note.markdown"
    md_path.write_text("content", encoding="utf-8")

    migrator = StructureMigrator(log=lambda _m: None)
    with pytest.raises(click.ClickException):
        migrator.migrate_to_folder(md_path)
