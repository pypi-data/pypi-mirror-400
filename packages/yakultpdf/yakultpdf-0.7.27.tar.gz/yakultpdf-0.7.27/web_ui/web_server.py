from __future__ import annotations

import html
import io
import os
import sys
from collections.abc import Iterable
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import fields
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

from mark2pdf.core import ConversionOptions, convert_from_string  # noqa: E402
from mark2pdf.core.defaults import DEFAULT_TEMPLATE, get_build_defaults  # noqa: E402
from mark2pdf.helper_workingpath import resolve_template_path  # noqa: E402

try:  # noqa: E402
    from mark2pdf import ConfigManager
except Exception:  # noqa: E402
    ConfigManager = None


_output_dir = os.getenv("MARK2PDF_OUTPUT_DIR") or os.getenv("PDFWORK_OUTPUT_DIR")
OUTPUT_DIR = Path(_output_dir or str(PROJECT_ROOT / "output")).expanduser()
MAX_MARKDOWN_CHARS = int(
    os.getenv("MARK2PDF_MAX_MARKDOWN_CHARS") or os.getenv("PDFWORK_MAX_MARKDOWN_CHARS") or "50000"
)


def _load_config():
    if ConfigManager is None:
        return None
    try:
        return ConfigManager.load()
    except Exception:
        return None


CONFIG = _load_config()

_LOG_LIMIT = 8000


def _normalize_template_name(name: str | None) -> str | None:
    if not name:
        return None
    cleaned = name.strip()
    if not cleaned:
        return None
    if not cleaned.endswith(".typ"):
        cleaned = f"{cleaned}.typ"
    return cleaned


_WEB_ALLOWED_TEMPLATES = [
    item
    for item in (
        _normalize_template_name(name)
        for name in (
            os.getenv("MARK2PDF_WEB_TEMPLATES") or os.getenv("PDFWORK_WEB_TEMPLATES") or "nb,gaozhi"
        ).split(",")
    )
    if item
]


class _TeeIO:
    def __init__(self, *streams):
        self._streams = [stream for stream in streams if stream is not None]

    def write(self, data):
        for stream in self._streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self._streams:
            stream.flush()


def _format_log(log: str | None) -> str:
    if not log:
        return ""
    log = log.strip()
    if len(log) <= _LOG_LIMIT:
        return log
    return f"{log[-_LOG_LIMIT:]}\n\n[log truncated]"


# ... code omitted ...


def _iter_template_dirs(config) -> Iterable[Path]:
    seen: set[Path] = set()
    if config is not None:
        template_dir = getattr(config, "template_dir", None)
        if template_dir:
            template_path = Path(template_dir)
            if template_path not in seen:
                seen.add(template_path)
                yield template_path

    fallback = PROJECT_ROOT / "src" / "mark2pdf" / "templates"
    if fallback not in seen:
        yield fallback


def _iter_resource_templates() -> Iterable[str]:
    try:
        from importlib import resources

        root = resources.files("mark2pdf.templates")
    except Exception:
        return []
    if root is None:
        return []
    return [item.name for item in root.iterdir() if item.is_file() and item.suffix == ".typ"]


def _list_templates(config) -> list[str]:
    if _WEB_ALLOWED_TEMPLATES:
        seen: set[str] = set()
        ordered: list[str] = []
        for name in _WEB_ALLOWED_TEMPLATES:
            if name in seen:
                continue
            seen.add(name)
            ordered.append(name)
        return ordered

    templates: set[str] = set()
    for template_dir in _iter_template_dirs(config):
        if not template_dir.exists():
            continue
        for item in template_dir.iterdir():
            if not item.is_file() or item.suffix != ".typ":
                continue
            if item.name.endswith("-lib.typ"):
                continue
            templates.add(item.name)

    for name in _iter_resource_templates():
        if name.endswith("-lib.typ"):
            continue
        templates.add(name)

    if not templates:
        return [DEFAULT_TEMPLATE]

    return sorted(templates)


TEMPLATES = _list_templates(CONFIG)

DEFAULT_TEMPLATE_NAME = DEFAULT_TEMPLATE
if CONFIG is not None:
    default_template = getattr(getattr(CONFIG, "build", None), "default_template", None)
    if default_template:
        DEFAULT_TEMPLATE_NAME = default_template
if _WEB_ALLOWED_TEMPLATES:
    DEFAULT_TEMPLATE_NAME = _WEB_ALLOWED_TEMPLATES[0]


class ConvertOptions(BaseModel):
    coverimg: str | None = None
    to_typst: bool | None = None
    savemd: bool | None = None
    removelink: bool | None = None
    tc: bool | None = None
    overwrite: bool | None = None
    filename_with_title: bool | None = None
    verbose: bool | None = None


class ConvertRequest(BaseModel):
    markdown: str = Field(..., min_length=1)
    template: str | None = None
    options: ConvertOptions | None = None


app = FastAPI(title="mark2pdf")


def _build_options(payload: ConvertRequest) -> ConversionOptions:
    build_defaults = get_build_defaults()
    options = ConversionOptions(**build_defaults) if build_defaults else ConversionOptions()

    if payload.template:
        options.template = payload.template
    else:
        options.template = options.template or DEFAULT_TEMPLATE_NAME

    if payload.options is None:
        return options

    overrides = payload.options.model_dump(exclude_none=True)
    allowed = {field.name for field in fields(ConversionOptions)}
    for key, value in overrides.items():
        if key not in allowed:
            raise HTTPException(status_code=400, detail=f"Unknown option: {key}")
        setattr(options, key, value)
    return options


def _validate_template(template_name: str) -> None:
    if "/" in template_name or "\\" in template_name:
        raise HTTPException(status_code=400, detail="Template must be a file name.")
    if _WEB_ALLOWED_TEMPLATES and template_name not in _WEB_ALLOWED_TEMPLATES:
        allowed = ", ".join(_WEB_ALLOWED_TEMPLATES)
        raise HTTPException(
            status_code=400,
            detail=f"Template not allowed. Allowed: {allowed}",
        )
    try:
        resolve_template_path(template_name, config=CONFIG)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Template not found: {template_name}") from exc


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    options_html = "\n".join(
        f'<option value="{html.escape(name)}">{html.escape(name)}</option>' for name in TEMPLATES
    )

    html_path = ROOT_DIR / "web_home.html"
    if not html_path.exists():
        return HTMLResponse("<h1>Error: web_home.html not found</h1>", status_code=500)

    page = html_path.read_text(encoding="utf-8")

    # Replace placeholders
    page = page.replace("__OPTIONS_HTML_PLACEHOLDER__", options_html)
    page = page.replace("__MAX_MARKDOWN_CHARS_PLACEHOLDER__", str(MAX_MARKDOWN_CHARS))
    page = page.replace("__DEFAULT_TEMPLATE_NAME_PLACEHOLDER__", html.escape(DEFAULT_TEMPLATE_NAME))

    return HTMLResponse(page)


@app.post("/convert")
def convert(payload: ConvertRequest) -> FileResponse:
    if len(payload.markdown) > MAX_MARKDOWN_CHARS:
        raise HTTPException(status_code=413, detail="Markdown payload too large.")

    options = _build_options(payload)
    _validate_template(options.template)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "typ" if options.to_typst else "pdf"
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_name = f"mark2pdf_{timestamp}_{uuid4().hex[:8]}.{suffix}"
    output_path = OUTPUT_DIR / output_name

    log_buffer: io.StringIO | None = None
    log_output = ""
    try:
        if options.verbose:
            log_buffer = io.StringIO()
            stdout_tee = _TeeIO(sys.__stdout__, log_buffer)
            stderr_tee = _TeeIO(sys.__stderr__, log_buffer)
            with redirect_stdout(stdout_tee), redirect_stderr(stderr_tee):
                result = convert_from_string(
                    content=payload.markdown,
                    output_path=output_path,
                    options=options,
                    config=CONFIG,
                )
            log_output = _format_log(log_buffer.getvalue())
        else:
            result = convert_from_string(
                content=payload.markdown,
                output_path=output_path,
                options=options,
                config=CONFIG,
            )
    except SystemExit as exc:
        if log_buffer is not None:
            log_output = _format_log(log_buffer.getvalue())
        detail = "pandoc/typst is not available."
        if log_output:
            detail = f"{detail}\n\n{log_output}"
        raise HTTPException(status_code=500, detail=detail) from exc
    except Exception as exc:
        if log_buffer is not None:
            log_output = _format_log(log_buffer.getvalue())
        detail = str(exc)
        if log_output:
            detail = f"{detail}\n\n{log_output}"
        raise HTTPException(status_code=500, detail=detail) from exc

    if result is None or not Path(result).exists():
        if log_buffer is not None:
            log_output = _format_log(log_buffer.getvalue())
        detail = "Conversion failed."
        if log_output:
            detail = f"{detail}\n\n{log_output}"
        raise HTTPException(status_code=500, detail=detail)

    media_type = "text/plain" if options.to_typst else "application/pdf"
    return FileResponse(
        path=str(result),
        media_type=media_type,
        filename=Path(result).name,
    )


@app.get("/healthz", response_class=PlainTextResponse)
def healthz() -> PlainTextResponse:
    return PlainTextResponse("ok")
