# yakultpdf

**基于 Pandoc 和 Typst 的 Markdown 转 PDF 工具**

将 Markdown 文件转换为精美的 PDF。支持 Frontmatter 配置、自动化目录管理以及通过 Python 代码调用。

## 安装

```bash
pip install yakultpdf
```

> **注意**：使用前请确保已安装 [Pandoc](https://pandoc.org/) 和 [Typst](https://typst.app/)。

## CLI 使用

**1. 初始化与配置**
```bash
# 初始化工作区（创建配置和目录结构）
yakultpdf init

# 安装常用中文字体（如 lxgw-wenkai）
yakultpdf fonts install lxgw-wenkai
```

**2. 转换文档**
```bash
# 转换单个文件 (默认输出到 out/ 目录)
yakultpdf convert document.md

# 转换单个文件并指定输出文件名
yakultpdf convert document.md --output my-report

# 转换整个目录（自动合并目录内所有 md 文件）
yakultpdf convert --dir docs/
```

**3. 更多功能**
```bash
# 复制内置模板到本地 template/ 目录
yakultpdf template
```

## Python API 使用

注意，导入时使用 `mark2pdf`：

```python
from mark2pdf import convert_file, convert_directory

# 1. 转换单个文件
# 将 input.md 转换为 output.pdf，使用默认配置
convert_file("input.md", output_file="output.pdf")

# 2. 转换目录
# 将 docs 目录下的所有 Markdown 合并转换为 merged_report.pdf
convert_directory("docs", output_file="merged_report.pdf")
```

