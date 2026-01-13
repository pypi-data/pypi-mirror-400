from pathlib import Path

import tomllib


def _find_repo_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise AssertionError("pyproject.toml not found")


def test_lockfile_version_matches_pyproject():
    repo_root = _find_repo_root(Path(__file__).resolve())
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    uv_lock = tomllib.loads((repo_root / "uv.lock").read_text(encoding="utf-8"))

    project_version = pyproject["project"]["version"]
    packages = uv_lock.get("package", [])
    lock_pkg = next((pkg for pkg in packages if pkg.get("name") == "yakultpdf"), None)

    assert lock_pkg is not None, "yakultpdf not found in uv.lock"
    assert lock_pkg.get("version") == project_version
