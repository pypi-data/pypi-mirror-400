# Package 最终方案思考：基于当前代码现状

> 编写日期：2026-01-01
> 核心目标：评估当前 `mark2pdf` 架构现状，规划服务端落盘模式的 SDK 改进路径

## 一、当前架构现状分析

### 1.1 包结构

```
src/
├── mark2pdf/              # CLI + 工作区管理 (对外入口)
│   ├── cli.py            # 主 CLI
│   ├── config.py         # 配置数据类 (Mark2pdfConfig, PathsConfig, BuildConfig)
│   ├── config_loader.py  # 配置加载器 (ConfigManager)
│   ├── conversion.py     # 转换执行封装 (run_conversion, run_directory_conversion, run_batch_conversion)
│   └── commands/         # 子命令 (init, update, version, gaozhi, mdimage 等)

├── markdown2pdf/         # 核心转换引擎
│   ├── core.py           # convert_file, execute_in_sandbox
│   ├── options.py        # ConversionOptions dataclass
│   ├── directory.py      # convert_directory
│   └── utils.py          # 预处理工具

├── helper_*/             # 辅助模块 (typst, markdown, interfile, workingpath 等)
```

### 1.2 已有优势（与之前版本比较）

| 能力 | 当前状态 | 说明 |
|------|---------|------|
| 配置解耦 | ✅ 已完成 | `ConfigManager` 支持独立模式，`convert_file` 接受 `config` 参数 |
| 沙箱执行 | ✅ 已完成 | `execute_in_sandbox` 使用 `tempfile` 创建隔离环境 |
| 可选依赖 | ✅ 已完成 | 配置加载使用 `try/except ImportError` 容错 |
| 模板多层查找 | ✅ 已完成 | 包内置模板支持 (`importlib.resources`) |
| CLI/Core 分离 | ✅ 基本完成 | `markdown2pdf.core` 可独立调用，不强依赖 CLI |

### 1.3 待改进项

| 能力 | 当前状态 | 说明 |
|------|---------|------|
| 字符串输入 | ✅ 已实现 | `convert_from_string()` 支持从内存字符串转换 |
| 服务端落盘模式 | ✅ 已实现 | `convert_from_string()` 支持直接指定输出路径 |
| Docker 适配 | ⚠️ 部分 | Dockerfile 草案完成，字体问题已解决 |

---

## 二、核心改造方案

### 2.1 高层 API 设计

目标：支持服务端落盘场景，简洁调用 + 灵活输出路径控制

```python
# 目标 API：服务端调用
from mark2pdf import convert_markdown

# 方式一：从文件转换（当前已支持）
output_path = convert_markdown(
    input_file="input.md",
    output_dir="/var/www/pdfs/",
    template="nb.typ",
)

# 方式二：从字符串转换（待实现）
output_path = convert_markdown(
    content="# Hello World",
    output_path="/var/www/pdfs/hello.pdf",
    template="nb.typ",
)
```

### 2.2 实现路径

基于现有 `convert_file` 改造，新增 `convert_from_string` 函数：

```python
# markdown2pdf/core.py 新增

def convert_from_string(
    content: str,
    output_path: Path | str,
    options: ConversionOptions = ConversionOptions(),
    default_frontmatter: dict | None = None,
    postprocess: Callable[[str], str] | None = None,
    images_dir: Path | str | None = None,
) -> Path | None:
    """
    从内存字符串转换为 PDF 文件

    Args:
        content: Markdown 内容
        output_path: 输出 PDF 文件路径（服务端落盘位置）
        options: 转换选项
        default_frontmatter: 默认 frontmatter
        postprocess: 后处理函数
        images_dir: 图片目录（可选，供 Markdown 中的图片引用）

    Returns:
        成功返回输出文件 Path，失败返回 None
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="mark2pdf_") as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 复用现有沙箱逻辑
        result = execute_in_sandbox(
            content=content,
            temp_filename="input.md",
            output_path=output_path,  # 直接写入目标位置
            images_source_dir=Path(images_dir) if images_dir else tmp_path,
            tmp_dir=tmp_path,
            sandbox_prefix="str_",
            options=options,
        )

        return result
```

### 2.3 架构分层

```
┌────────────────────────────────────────────────────────────┐
│                        用户入口                             │
├────────────────────────────────────────────────────────────┤
│  CLI (mark2pdf)        │  SDK (import mark2pdf)              │
│  - convert 命令       │  - convert_markdown()              │
│  - init/update        │  - convert_from_string()           │
│  - batch/dir 模式     │  - convert_file()                  │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│                     markdown2pdf 核心                       │
├────────────────────────────────────────────────────────────┤
│  execute_in_sandbox()  - 沙箱执行 (已实现)                  │
│  预处理管道            - 链式处理 (已实现)                  │
│  ConversionOptions     - 配置对象 (已实现)                  │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│                     外部工具调用                            │
├────────────────────────────────────────────────────────────┤
│  Pandoc                │  Typst                             │
│  (Markdown → Typst)    │  (Typst → PDF)                     │
└────────────────────────────────────────────────────────────┘
```

---

## 三、已实现：字符串输入 API ✅

> **实现位置**：`src/markdown2pdf/core.py` 的 `convert_from_string()` 函数

### 3.1 API 用法

```python
from mark2pdf import convert_from_string

output = convert_from_string(
    content="# Hello World",
    output_path="/var/www/pdfs/hello.pdf",
    template="nb.typ",
    images_dir="/path/to/images",  # 可选
)
```

### 3.2 实现要点

- 基于 `execute_in_sandbox` 实现
- 支持直接指定 `output_path` 落盘
- 支持 `images_dir` 参数关联图片目录
- 单元测试：`src/markdown2pdf/tests/test_convert_from_string.py`

---

## 四、已实现：字体路径支持与字体管理

### 4.1 改动概述

- `helper_typst.py`: 新增 `font_paths` 参数，通过 `--pdf-engine-opt --font-path=` 传给 Typst
- `core.py`: 新增 `_collect_font_paths()` 自动收集字体目录，`_warn_missing_fonts()` 检测字体缺失
- `commands/fonts.py`: 新增 `mark2pdf fonts` 命令组

### 4.2 字体查找顺序

1. `config.paths.fonts` (配置指定，默认 `fonts/`)
2. `{cwd}/fonts/` (独立模式默认)
3. `{template_dir}/fonts/` (模板同级)

### 4.3 字体管理命令

```bash
mark2pdf fonts list              # 列出可安装字体
mark2pdf fonts install lxgw-wenkai  # 从 GitHub 下载安装
mark2pdf fonts install --url <url>  # 自定义 URL 安装
mark2pdf fonts status            # 查看已安装字体
```

**内置字体目录**：思源黑体、思源宋体、霞鹜文楷、悠哉字体

---

## 五、实施路线（两阶段）

### 阶段一：本机 Docker + 网页版

**目标**：在本地运行完整的 Web 服务，通过浏览器访问

| 任务 | 状态 |
|------|------|
| Dockerfile 编写 | ✅ 草案完成 |
| 字体路径支持 | ✅ 已实现 |
| FastAPI Web 服务 | ⏳ 待实现 |
| docker-compose 编排 | ⏳ 待实现 |

**交付物**：

```bash
# 一键启动
docker-compose up -d

# 浏览器访问
http://localhost:8000
```

**docker-compose.yml**：

```yaml
version: "3.8"
services:
  mark2pdf:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./output:/app/output
      - ~/Library/Fonts:/fonts:ro
    environment:
      - TYPST_FONT_PATHS=/fonts
    command: uvicorn web_server:app --host 0.0.0.0 --port 8000
```

**预期体验**：
1. 打开网页，粘贴 Markdown
2. 选择模板，点击转换
3. 下载 PDF

---

### 阶段二：服务器远程部署

**目标**：部署到云服务器，提供公开 API

| 平台 | 适合场景 | 说明 |
|------|---------|------|
| Railway | 快速上线 | 支持 Docker，配置简单 |
| Fly.io | 低延迟 | 边缘部署，冷启动快 |
| Render | 免运维 | 自动缩放 |
| 自建 VPS | 完全控制 | 需要手动维护 |

**API 设计**：

```python
POST /convert
Content-Type: application/json

{
    "markdown": "# Hello World",
    "template": "nb.typ",
    "options": {"verbose": false}
}

Response: PDF 文件 (application/pdf)
```

**安全考虑**：
- 限制请求频率
- 限制输入大小
- 定时清理输出目录

---

### 阶段二补充：Vercel + 后端服务架构

**场景**：前端部署在 Vercel，PDF 生成由独立后端服务处理

```
用户 → Vercel (Next.js) → Railway/Fly.io (mark2pdf API)
           │                      │
           ├─ 前端界面            ├─ /convert POST
           ├─ 用户鉴权            ├─ pandoc + typst
           └─ 请求限流            └─ 返回 PDF
```

**为什么不在 Vercel Serverless Functions 里直接跑 pandoc/typst？**

| 限制 | 说明 |
|------|------|
| 包体积 | 最大 50MB，pandoc + typst 可能超限 |
| 执行时间 | 免费 10s，Pro 60s，转换可能超时 |
| 维护困难 | 需要手动打包 Linux 二进制 |

**推荐方案**：Vercel 前端 + 独立容器后端

**示例代码（Vercel API Route 转发）**：
```typescript
// pages/api/convert.ts
export default async function handler(req, res) {
  const response = await fetch('https://your-mark2pdf.fly.dev/convert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ markdown: req.body.markdown }),
  });
  
  const pdf = await response.arrayBuffer();
  res.setHeader('Content-Type', 'application/pdf');
  res.send(Buffer.from(pdf));
}
```

---

## 六、风险评估

### 6.1 进程隔离

**结论**：安全 ✅
- 每个转换在独立临时目录中执行
- Pandoc/Typst 是 stateless 命令行工具

### 6.2 字体问题

**已解决** ✅：通过 `font_paths` 参数支持自定义字体目录

### 6.3 模板资源

**已解决** ✅：`pyproject.toml` 配置打包模板到 `mark2pdf/templates`

---

## 七、总结

当前进度：

| 能力 | 状态 |
|------|------|
| 配置解耦 | ✅ |
| 沙箱执行 | ✅ |
| 模板打包 | ✅ |
| 字体路径 | ✅ |
| 字体管理命令 | ✅ (`mark2pdf fonts`) |
| 字符串输入 API | ✅ (`convert_from_string`) |
| 服务端落盘模式 | ✅ |
| 本机 Docker | ⏳ 阶段一 |
| 网页界面 | ⏳ 阶段一 |
| 远程部署 | ⏳ 阶段二 |

预估工作量：阶段一约 1-2 天。

---

## 附录：Docker 配置详情

### A.1 Dockerfile

```dockerfile
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    fontconfig \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 安装 Pandoc
RUN wget -qO- https://github.com/jgm/pandoc/releases/download/3.5/pandoc-3.5-linux-amd64.tar.gz \
    | tar xz --strip-components=1 -C /usr/local

# 安装 Typst  
RUN wget -qO- https://github.com/typst/typst/releases/download/v0.12.0/typst-x86_64-unknown-linux-musl.tar.xz \
    | tar xJ --strip-components=1 -C /usr/local/bin

WORKDIR /app
CMD ["python"]
```

### A.2 构建与运行

```bash
# 构建
docker build -t mark2pdf:dev .

# 运行（挂载代码 + 工作区）
docker run -it --rm \
    -v $(pwd):/app \
    -v ~/notes:/data \
    mark2pdf:dev bash

# 容器内安装（开发模式）
pip install -e .

# 转换
mark2pdf convert /data/sample.md
```

### A.3 自定义字体

```bash
# 挂载本机字体目录
docker run -it --rm \
    -v $(pwd):/app \
    -v ~/Library/Fonts:/fonts:ro \
    -e TYPST_FONT_PATHS=/fonts \
    mark2pdf:dev bash
```

> **提示**：Typst 会自动读取 `TYPST_FONT_PATHS` 环境变量指定的字体目录
