# mark2pdf CLI 使用说明

## 概述

`mark2pdf` 是一个 Markdown 转 PDF 工具集，提供工作区管理、图片处理、PDF 转换等功能。

```bash
mark2pdf [命令] [选项] [参数]
```

## 命令一览

| 命令 | 说明 | 需要工作区 |
|------|------|:----------:|
| `convert` | 核心转换命令：Markdown → PDF | ❌（支持独立模式） |
| `fonts` | 字体管理（下载/安装/查看） | ❌ |
| `mdimage` | 图片处理（下载/结构迁移） | ❌ |
| `gaozhi` | 稿纸排版专用转换器 | ❌（支持独立模式） |
| `coverprepare` | 封面图片尺寸检查与裁切 | ❌ |
| `clean` | 清理输出目录 | ✅（仅工作区） |
| `init` | 初始化工作区 | ❌ |
| `update` | 更新工作区脚本 | ✅（仅工作区） |
| `version` | 显示版本信息 | ❌ |

> **说明**：
> - `convert` / `gaozhi` 支持独立模式：未找到 `mark2pdf.config.toml` 时使用当前目录作为输入/输出，临时目录为 `.mark2pdf_tmp`。
> - `clean` / `update` 必须在工作区运行。


---

## 1. convert - 核心转换命令

### 三种模式

```bash
# 单文件模式（默认）
mark2pdf convert sample.md

# 目录合并模式：合并目录下所有 .md 文件后转换
mark2pdf convert --dir chapter1

# 批量模式：逐一转换目录中每个文件（各自独立输出）
mark2pdf convert --batch .
```

### 完整选项

| 选项 | 简写 | 说明 |
|------|------|------|
| `--dir` | `-d` | 目录合并模式 |
| `--batch` | `-b` | 批量模式 |
| `--template` | `-t` | 指定模板文件（如 `nb.typ`） |
| `--tc` | | 转换为繁体中文 |
| `--removelink` | | 移除超链接（保留图片） |
| `--open` | `-o` | 转换完成后打开 PDF |
| `--verbose` | `-v` | 显示详细信息 |
| `--overwrite` | | 覆盖输出文件（不添加时间戳） |
| `--postprocess` | `-p` | 后处理器名称（按名称加载） |
| `--show-config` | | 仅显示配置，不执行转换 |
| `--dry-run` | | 试运行模式，显示执行计划 |

### 使用场景

#### 调试配置
```bash
# 查看合并后的完整配置
mark2pdf convert sample.md --show-config

# 查看执行计划但不实际运行
mark2pdf convert sample.md --dry-run
```

#### 批量转换
```bash
# 转换 in/docs/ 下所有 .md 文件
mark2pdf convert --batch docs

# 繁体中文批量转换
mark2pdf convert --batch . --tc
```

#### 目录合并
```bash
# 将 chapter1/ 下所有 .md 合并为一个 PDF
mark2pdf convert --dir chapter1 -o
```

### 路径说明

- 工作区模式：`--dir` / `--batch` 参数相对于 `paths.in`（默认 `in/`）。
- 独立模式：相对于当前目录。

### 配置优先级

模板解析顺序（由高到低）：
1. CLI `--template` 参数
2. 文件 frontmatter 中的 `template` 字段
3. `mark2pdf.config.toml` 中的 `build.default_template`
4. 系统默认模板

---

## 2. mdimage - 图片处理工具

### 子命令

```bash
mark2pdf mdimage download [路径]   # 下载/清理图片
mark2pdf mdimage todir [文件]       # 单文件 → 文件夹模式
mark2pdf mdimage tofile [目录]      # 文件夹 → 单文件模式
```

### download - 图片下载

清理 Markdown 中的远程图片链接，下载到本地 `images/` 目录。

```bash
# 处理单个文件（输出 sample_processed.md）
mark2pdf mdimage download sample.md

# 处理目录下所有 .md 文件
mark2pdf mdimage download ./docs/

# 覆盖原文件
mark2pdf mdimage download sample.md --overwrite

# 调整下载延迟（避免被限流）
mark2pdf mdimage download sample.md --delay 2.0
```

**特殊处理**：
- 微信图片（403 错误）：自动重试并插入占位符
- Data URI：提取并保存为本地文件
- 已存在的本地图片：跳过

### todir - 单文件 → 文件夹模式

将 `abc.md + images/abc/*.jpg` 转换为 `abc/index.md + abc/images/*.jpg`。

```bash
# 迁移（删除原文件）
mark2pdf mdimage todir abc.md

# 保留原文件
mark2pdf mdimage todir abc.md --keep
```

### tofile - 文件夹 → 单文件模式

将 `abc/index.md + abc/images/*.jpg` 转换为 `abc.md + images/abc/*.jpg`。

```bash
# 迁移
mark2pdf mdimage tofile abc/

# 保留原文件
mark2pdf mdimage tofile abc/ --keep
```

### 两种目录结构

| 模式 | Markdown 位置 | 图片位置 |
|------|--------------|---------|
| Flat（单文件） | `./abc.md` | `./images/abc/*.jpg` |
| Folder（文件夹） | `./abc/index.md` | `./abc/images/*.jpg` |

---

## 3. fonts - 字体管理

```bash
mark2pdf fonts list
mark2pdf fonts install <font_name>
mark2pdf fonts install --url <download_url>
mark2pdf fonts status
```

常用示例：
```bash
mark2pdf fonts install lxgw-wenkai
mark2pdf fonts install source-han-sans
```

## 4. gaozhi - 稿纸排版转换器

专用于 gaozhi.typ 模板的转换器，支持批量转换后合并。

### 单文件模式

```bash
mark2pdf gaozhi sample.md
mark2pdf gaozhi sample.md -o  # 转换后打开
```

### 目录模式

逐个转换目录中所有 .md 文件（排除 index.md），然后合并为单个 PDF。

```bash
# 转换 nlist/ 下所有文件，合并为 nlist_gaozhi.pdf
mark2pdf gaozhi --dir nlist

# 自定义输出文件名
mark2pdf gaozhi --dir nlist --output "我的稿纸合集"

# 处理当前目录
mark2pdf gaozhi --dir . --output merged
```

### 选项

| 选项 | 简写 | 说明 |
|------|------|------|
| `--dir` | `-d` | 目录模式 |
| `--output` | | 合并输出文件名（不含扩展名） |
| `--verbose` | `-v` | 显示详细信息 |
| `--open` | `-o` | 转换完成后打开 |
| `--help` | `-h` | 显示帮助 |

---

## 5. coverprepare - 封面准备工具

检查图片尺寸是否适合全页显示，并可裁切转换。

### check - 检查图片

```bash
# 检查是否适合 A4 全页
mark2pdf coverprepare check cover.png

# 检查是否适合 A5
mark2pdf coverprepare check cover.png --paper a5

# 简写（默认子命令）
mark2pdf coverprepare cover.png

# 裁切转换为目标尺寸
mark2pdf coverprepare check cover.png --paper a4 --crop
```

### list - 列出支持的纸型

```bash
mark2pdf coverprepare list
```

支持的纸型（@300dpi）：

| 纸型 | 尺寸（像素） |
|------|-------------|
| a4 | 2480 × 3508 |
| a5 | 1748 × 2480 |
| letter | 2550 × 3300 |
| legal | 2550 × 4200 |
| b5 | 2079 × 2953 |
| 16:9 | 1920 × 1080 |
| 4:3 | 1600 × 1200 |

---

## 6. clean - 清理输出目录

删除输出目录中的 PDF 文件。

```bash
# 预览将要删除的文件
mark2pdf clean --dry-run

# 交互式确认删除
mark2pdf clean

# 强制删除（无确认）
mark2pdf clean -f
```

| 选项 | 简写 | 说明 |
|------|------|------|
| `--dry-run` | | 仅列出文件，不删除 |
| `--force` | `-f` | 强制删除，不确认 |

---

## 7. init / update - 工作区管理

### init - 初始化工作区

在目标目录创建工作区结构（配置文件、模板、脚本）。

```bash
mark2pdf init .
mark2pdf init /path/to/project
```

**要求**：目标目录必须为空（允许 `.DS_Store`）。

### update - 更新工作区脚本

更新现有工作区中的 `createpdf.py` 脚本到最新版本。

```bash
# 更新当前目录
mark2pdf update

# 更新指定目录
mark2pdf update /path/to/project
```

---

## 7. version - 版本信息

```bash
mark2pdf version
```

显示 `markdown2pdf` 包的版本号。

---

## 工作区结构

初始化后的典型工作区结构：

```
project/
├── mark2pdf.config.toml    # 工作区配置
├── frontmatter.yaml       # 默认 frontmatter
├── createpdf.py          # 快捷转换脚本
├── in/                    # 输入目录
│   ├── sample.md
│   └── images/
│       └── sample/
├── fonts/                 # 字体目录（可选）
└── out/                   # 输出目录
    └── sample.pdf
```

### mark2pdf.config.toml 示例

```toml
[project]
name = "我的文档项目"

[paths]
input = "in"
output = "out"
fonts = "fonts"

[build]
default_template = "nb.typ"
overwrite = false

[frontmatter]
author = "作者名"
```

---

## 常见问题

### Q: 如何转换为繁体中文？
```bash
mark2pdf convert sample.md --tc
```

### Q: 如何批量处理一个目录？
```bash
# 逐一转换（各自独立 PDF）
mark2pdf convert --batch docs

# 合并转换（单个 PDF）
mark2pdf convert --dir docs
```

### Q: 如何清理微信文章中的图片？
```bash
mark2pdf mdimage download wechat_article.md --delay 2.0
```
微信图片会自动使用特殊 User-Agent 和重试机制。

### Q: 转换后如何自动打开？
```bash
mark2pdf convert sample.md -o
mark2pdf gaozhi sample.md -o
```

### Q: 如何查看当前配置？
```bash
mark2pdf convert --show-config
```
