from __future__ import annotations

import re
import shutil
from collections.abc import Callable
from pathlib import Path

import click

MARKDOWN_SUFFIXES = {".md"}
IMAGE_FILE_GLOB = "*.*"

IMAGE_LINK_PATTERN = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^\s\)]+)"
    r"(?:\s+(?P<title>(\"[^\"]*\"|'[^']*'|\([^\)]*\))))?\)"
    r"(?P<tail>\{[^\}]*\})?"
)


class StructureMigrator:
    COMPANION_MAP = {
        "ai-shape": "ai-shape_processed",
        "ai-shape_processed": "ai-shape",
        "cc": "cc_zh",
        "cc_zh": "cc",
    }

    def __init__(self, log: Callable[[str], None] | None = None) -> None:
        self.log = log or (lambda _m: None)

    def migrate_to_folder(self, md_path: Path, *, keep_original: bool = False) -> None:
        if not md_path.exists():
            raise click.ClickException(f"路径不存在: {md_path}")
        if md_path.is_dir():
            raise click.ClickException("单文件模式迁移需要传入 Markdown 文件路径")
        if md_path.suffix.lower() != ".md":
            raise click.ClickException("仅支持 .md 文件")

        base_name = md_path.stem
        target_dir = md_path.parent / base_name
        target_md = target_dir / "index.md"
        images_src = md_path.parent / "images" / base_name
        images_dest = target_dir / "images"

        if target_md.exists():
            raise click.ClickException(f"目标文件已存在: {target_md}")
        if target_dir.exists() and any(target_dir.iterdir()):
            raise click.ClickException(f"目标目录非空，无法迁移: {target_dir}")

        target_dir.mkdir(parents=True, exist_ok=True)
        images_dest.mkdir(parents=True, exist_ok=True)

        content = md_path.read_text(encoding="utf-8")
        if keep_original:
            self.log(f"📄 复制文件：{md_path} -> {target_md}")
            shutil.copy2(str(md_path), str(target_md))
        else:
            self.log(f"📄 移动文件：{md_path} -> {target_md}")
            shutil.move(str(md_path), str(target_md))

        primary_prefix = self._detect_primary_images_prefix(content)

        def rewrite_path(p: str) -> str:
            return self._rewrite_to_folder_path(p, primary_prefix)

        moved = self._transfer_image_files(images_src, images_dest, move=not keep_original)
        referenced = self._transfer_referenced_images(
            content,
            base_name,
            search_dirs=[md_path.parent, md_path.parent / base_name],
            target_root=target_md.parent,
            rewrite_path=rewrite_path,
            move=not keep_original,
        )
        if images_src.exists() and not keep_original:
            self._remove_empty_dir(images_src)
            self._remove_empty_dir(images_src.parent)

        self._rewrite_image_links(target_md, rewrite_path=rewrite_path)
        companion_transferred = self._handle_companion_file(
            md_path,
            target_dir,
            keep_original=keep_original,
            search_dirs=[md_path.parent, md_path.parent / base_name],
        )
        total = moved + referenced + companion_transferred
        self.log(f"✅ 完成迁移，处理图片 {total} 个")

    def migrate_to_file(self, folder_path: Path, *, keep_original: bool = False) -> None:
        if not folder_path.exists():
            raise click.ClickException(f"路径不存在: {folder_path}")
        if not folder_path.is_dir():
            raise click.ClickException("文件夹模式迁移需要传入目录路径")

        md_file = self._find_markdown_file(folder_path)
        target_md = folder_path.parent / f"{folder_path.name}.md"
        images_src = folder_path / "images"
        images_dest = folder_path.parent / "images" / folder_path.name

        if target_md.exists():
            raise click.ClickException(f"目标文件已存在: {target_md}")

        images_dest.mkdir(parents=True, exist_ok=True)

        content = md_file.read_text(encoding="utf-8")
        if keep_original:
            self.log(f"📄 复制文件：{md_file} -> {target_md}")
            shutil.copy2(str(md_file), str(target_md))
        else:
            self.log(f"📄 移动文件：{md_file} -> {target_md}")
            shutil.move(str(md_file), str(target_md))

        moved = self._transfer_image_files(images_src, images_dest, move=not keep_original)
        referenced = self._transfer_referenced_images(
            content,
            folder_path.name,
            search_dirs=[md_file.parent, md_file.parent.parent],
            target_root=target_md.parent,
            rewrite_path=lambda p: self._rewrite_to_file_path(p, folder_path.name),
            move=not keep_original,
        )
        if images_src.exists() and not keep_original:
            self._remove_empty_dir(images_src)

        self._rewrite_image_links(
            target_md, rewrite_path=lambda p: self._rewrite_to_file_path(p, folder_path.name)
        )
        if not keep_original:
            self._remove_empty_dir(folder_path)
        total = moved + referenced
        self.log(f"✅ 完成迁移，处理图片 {total} 个")

    def _find_markdown_file(self, folder_path: Path) -> Path:
        for name in ("index.md", f"{folder_path.name}.md"):
            candidate = folder_path / name
            if candidate.exists():
                return candidate

        candidates = sorted(
            p
            for p in folder_path.iterdir()
            if p.is_file() and p.suffix.lower() in MARKDOWN_SUFFIXES
        )
        if len(candidates) == 1:
            return candidates[0]

        names = ", ".join(p.name for p in candidates) if candidates else "无"
        raise click.ClickException(f"无法确定 Markdown 文件，候选: {names}")

    def _transfer_image_files(self, src: Path, dest: Path, *, move: bool) -> int:
        if not src.exists():
            self.log(f"⚠️ 图片目录不存在，跳过移动：{src}")
            return 0
        if not src.is_dir():
            raise click.ClickException(f"图片目录不是文件夹: {src}")

        moved = 0
        for item in src.glob(IMAGE_FILE_GLOB):
            if item.is_file():
                target = dest / item.name
                if move:
                    shutil.move(str(item), str(target))
                else:
                    shutil.copy2(str(item), str(target))
                moved += 1
        return moved

    def _transfer_referenced_images(
        self,
        content: str,
        base_name: str,
        *,
        search_dirs: list[Path],
        target_root: Path,
        rewrite_path: Callable[[str], str],
        move: bool,
    ) -> int:
        referenced = self._collect_local_image_paths(content)
        if not referenced:
            return 0

        transferred = 0
        seen_dest: set[Path] = set()
        for path in referenced:
            dest_rel = rewrite_path(path)
            if dest_rel.startswith(("http://", "https://", "data:image/")):
                continue
            if not self._is_images_path(dest_rel):
                continue
            dest_path = target_root / dest_rel.lstrip("./")
            dest_path = Path(self._unescape_markdown_path(str(dest_path)))
            if dest_path.exists() or dest_path in seen_dest:
                continue

            src = self._resolve_image_source(path, base_name, search_dirs)
            if src is None:
                continue

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            if move:
                shutil.move(str(src), str(dest_path))
            else:
                shutil.copy2(str(src), str(dest_path))
            seen_dest.add(dest_path)
            transferred += 1

        return transferred

    def _handle_companion_file(
        self,
        md_path: Path,
        target_dir: Path,
        *,
        keep_original: bool,
        search_dirs: list[Path],
    ) -> int:
        companion_name = self.COMPANION_MAP.get(md_path.stem)
        if not companion_name:
            return 0
        companion_path = md_path.with_name(f"{companion_name}.md")
        if not companion_path.exists():
            return 0

        dest_path = target_dir / companion_path.name
        if dest_path.exists():
            self.log(f"⚠️  目标文件已存在，跳过：{dest_path}")
            return 0

        companion_content = companion_path.read_text(encoding="utf-8")
        if keep_original:
            self.log(f"📄 复制文件：{companion_path} -> {dest_path}")
            shutil.copy2(str(companion_path), str(dest_path))
        else:
            self.log(f"📄 移动文件：{companion_path} -> {dest_path}")
            shutil.move(str(companion_path), str(dest_path))

        companion_prefix = self._detect_primary_images_prefix(companion_content)

        def companion_rewrite(p: str) -> str:
            return self._rewrite_to_folder_path(p, companion_prefix)

        self._rewrite_image_links(dest_path, rewrite_path=companion_rewrite)

        companion_search_dirs = list(search_dirs) + [companion_path.parent / companion_path.stem]
        companion_images = self._transfer_referenced_images(
            companion_content,
            companion_path.stem,
            search_dirs=companion_search_dirs,
            target_root=target_dir,
            rewrite_path=companion_rewrite,
            move=not keep_original,
        )
        return companion_images

    @staticmethod
    def _collect_local_image_paths(content: str) -> list[str]:
        paths: list[str] = []
        for match in IMAGE_LINK_PATTERN.finditer(content):
            path = match.group("path").strip()
            if path.startswith(("http://", "https://", "data:image/")):
                continue
            paths.append(path)
        return paths

    @staticmethod
    def _detect_primary_images_prefix(content: str) -> str | None:
        counts: dict[str, int] = {}
        for path in StructureMigrator._collect_local_image_paths(content):
            normalized = StructureMigrator._unescape_markdown_path(path.lstrip("./"))
            if not normalized.startswith("images/"):
                continue
            rest = normalized[len("images/") :]
            if "/" not in rest:
                continue
            prefix = rest.split("/", 1)[0]
            counts[prefix] = counts.get(prefix, 0) + 1
        if not counts:
            return None
        return max(counts, key=counts.get)

    @staticmethod
    def _resolve_image_source(path: str, base_name: str, search_dirs: list[Path]) -> Path | None:
        if path.startswith(("http://", "https://", "data:image/")):
            return None

        normalized = StructureMigrator._unescape_markdown_path(path.lstrip("./"))
        candidates = [normalized]
        base_prefix = f"images/{base_name}/"
        images_prefix = "images/"

        if normalized.startswith(base_prefix):
            candidates.append(images_prefix + normalized[len(base_prefix) :])
        if normalized.startswith(images_prefix):
            candidates.append(base_prefix + normalized[len(images_prefix) :])
            remainder = normalized[len(images_prefix) :]
            if "/" in remainder:
                candidates.append(images_prefix + remainder.split("/", 1)[1])

        seen: set[tuple[Path, str]] = set()
        for base in search_dirs:
            for rel in candidates:
                key = (base, rel)
                if key in seen:
                    continue
                seen.add(key)
                candidate = base / rel
                if candidate.exists() and candidate.is_file():
                    return candidate
        return None

    @staticmethod
    def _rewrite_to_folder_path(path: str, primary_prefix: str | None) -> str:
        if path.startswith(("http://", "https://", "data:image/")):
            return path
        leading = "./" if path.startswith("./") else ""
        normalized = path[2:] if leading else path
        if not normalized.startswith("images/"):
            return path
        if not primary_prefix:
            return path
        prefix = f"images/{primary_prefix}/"
        if not normalized.startswith(prefix):
            return path
        rest = normalized[len(prefix) :]
        return f"{leading}images/{rest}"

    @staticmethod
    def _rewrite_to_file_path(path: str, folder_name: str) -> str:
        if path.startswith(("http://", "https://", "data:image/")):
            return path
        leading = "./" if path.startswith("./") else ""
        normalized = path[2:] if leading else path
        if not normalized.startswith("images/"):
            return path
        rest = normalized[len("images/") :]
        if rest.startswith(f"{folder_name}/"):
            return path
        return f"{leading}images/{folder_name}/{rest}"

    @staticmethod
    def _unescape_markdown_path(path: str) -> str:
        return re.sub(r"\\(.)", r"\1", path)

    @staticmethod
    def _is_images_path(path: str) -> bool:
        normalized = path.lstrip("./")
        return normalized.startswith("images/")

    def _rewrite_image_links(self, md_path: Path, *, rewrite_path: Callable[[str], str]) -> None:
        content = md_path.read_text(encoding="utf-8")
        updated = self._replace_image_paths(content, rewrite_path=rewrite_path)
        md_path.write_text(updated, encoding="utf-8")

    @staticmethod
    def _replace_image_paths(content: str, *, rewrite_path: Callable[[str], str]) -> str:
        def replace(match: re.Match[str]) -> str:
            path = match.group("path")
            if path.startswith(("http://", "https://", "data:image/")):
                return match.group(0)

            updated = rewrite_path(path)
            if updated == path:
                return match.group(0)

            title = match.group("title") or ""
            tail = match.group("tail") or ""
            title = f" {title}" if title else ""
            return f"![{match.group('alt')}]({updated}{title}){tail}"

        return IMAGE_LINK_PATTERN.sub(replace, content)

    def _remove_empty_dir(self, path: Path) -> None:
        try:
            path.rmdir()
        except OSError:
            return
