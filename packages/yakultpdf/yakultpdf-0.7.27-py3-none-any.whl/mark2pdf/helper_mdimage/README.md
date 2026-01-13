# helper_mdimage 使用说明

## 组件
- `mdimage_assets.py`: URL 编码、文件名生成、格式探测/WebP 转换、data URI 保存、微信特例处理、带重试下载。
- `mdimage_rewrite.py`: `rewrite_markdown_images` API，按规则重写 Markdown 图片并返回统计。
- `mdimage_cli.py`: Click 命令行入口（同时由 `scripts/md_image_cleaning_new.py` 复用）。
- `md_image_cleaning_new.py`: 仓库主入口脚本，保持原 `md_image_cleaning.py` 不变。

## 安装依赖
- 需要 `click` 与 `pillow`（原脚本同样依赖）。本仓库已用于脚本注释声明，通常按项目环境安装即可。

## 命令行用法
```bash
# 单文件（默认写入 *_processed.md）
python3 scripts/md_image_cleaning_new.py path/to/file.md

# 覆盖原文件
python3 scripts/md_image_cleaning_new.py path/to/file.md --samefile

# 目录模式（批量处理目录下 .md，图片统一放 images/<目录名>/）
python3 scripts/md_image_cleaning_new.py path/to/dir

# 自动从工作区输入目录补全文件 (默认读取 mark2pdf.config.toml 的 paths.in 或使用 ./in)
python3 scripts/md_image_cleaning_new.py demo.md
```

常用选项：
- `--delay <秒>`：下载间隔（默认 1.5，首张不等待）。
- `--wechat-placeholder / --no-wechat-placeholder`：微信下载失败是否插入占位符（默认开启）。
- `--samefile`：直接覆盖原文件。

## API 用法
```python
from mark2pdf.helper_mdimage import rewrite_markdown_images
from pathlib import Path

result = rewrite_markdown_images(
    content=markdown_text,
    images_dir=Path("docs/images/article"),
    rel_dir="images/article",  # Markdown 中的相对目录
    delay=0.5,
    wechat_placeholder=True,
)
print(result.downloaded, result.skipped)
processed = result.content
```

## 规则对齐要点
- 自动补全输入路径：优先读取 `mark2pdf.config.toml` 的 `paths.in`，否则使用当前目录下的 `in`。
- 清理 `Copy Image` 标记；先处理 data URI，再处理 HTTP，跳过本地路径。
- 文件命名：`stem + "_" + md5(url)[:6] + suffix`，无扩展时 `<hash>.png`，非法字符替换 `_`。
- 已存在复用：检查 png/jpeg/jpg/gif/webp/bmp/ico/svg。
- URL 编码与特例：微信参数清洗 + 专属头；Contentful/长 query 保留；`_next/image` 等代理不强制格式参数。
- 下载：重试 3 次（429/异常递增等待），WebP 尝试转 PNG；失败的微信可插入 HTML 占位符。
- Markdown 重写：成功/复用改为相对路径，保留属性尾缀 `{...}`；统计跳过/下载/失败。***
