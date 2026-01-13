FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
  wget \
  fontconfig \
  fonts-arphic-ukai \
  fonts-arphic-uming \
  fonts-dejavu-core \
  fonts-freefont-ttf \
  fonts-ipafont-gothic \
  fonts-ipafont-mincho \
  fonts-liberation \
  fonts-noto-cjk \
  fonts-noto-color-emoji \
  fonts-noto-core \
  fonts-noto-extra \
  fonts-urw-base35 \
  fonts-wqy-microhei \
  fonts-wqy-zenhei \
  ca-certificates \
  xz-utils \
  build-essential \
  cmake \
  pkg-config \
  libopencc-dev \
  && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
  arch="$(dpkg --print-architecture)"; \
  case "$arch" in \
  amd64) pandoc_arch="amd64" ;; \
  arm64) pandoc_arch="arm64" ;; \
  *) echo "Unsupported architecture: $arch" >&2; exit 1 ;; \
  esac; \
  pandoc_tag="$(python -c "import json,urllib.request; print(json.load(urllib.request.urlopen('https://api.github.com/repos/jgm/pandoc/releases/latest'))['tag_name'])")"; \
  wget -qO- "https://github.com/jgm/pandoc/releases/download/${pandoc_tag}/pandoc-${pandoc_tag}-linux-${pandoc_arch}.tar.gz" \
  | tar xz --strip-components=1 -C /usr/local

RUN set -eux; \
  arch="$(dpkg --print-architecture)"; \
  case "$arch" in \
  amd64) typst_arch="x86_64-unknown-linux-musl" ;; \
  arm64) typst_arch="aarch64-unknown-linux-musl" ;; \
  *) echo "Unsupported architecture: $arch" >&2; exit 1 ;; \
  esac; \
  wget -qO- "https://github.com/typst/typst/releases/latest/download/typst-${typst_arch}.tar.xz" \
  | tar xJ --strip-components=1 -C /usr/local/bin

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra web --no-install-project

COPY . .
RUN uv sync --frozen --no-dev --extra web

# Manual custom fonts (e.g. YouSheBiaoTiHei)
COPY web_ui/fonts/ /usr/share/fonts/yakultpdf/

# Auto-install supported fonts
RUN uv run yakultpdf fonts install lxgw-wenkai --dir /usr/share/fonts/yakultpdf/
RUN uv run yakultpdf fonts install source-han-sans --dir /usr/share/fonts/yakultpdf/
# RUN uv run yakultpdf fonts install yozai --dir /usr/share/fonts/yakultpdf/

RUN fc-cache -fv

ENV TYPST_FONT_PATHS=/usr/share/fonts/yakultpdf

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "web_ui.web_server:app", "--host", "0.0.0.0", "--port", "8000"]
