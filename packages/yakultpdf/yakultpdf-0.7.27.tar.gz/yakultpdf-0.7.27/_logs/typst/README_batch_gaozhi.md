# batch_gaozhi.py 使用说明

## 功能描述

`batch_gaozhi.py` 是一个批量处理脚本，用于将指定目录中的所有 markdown 文件转换为稿纸格式的 PDF，并将它们合并成一个大文件。

## 使用方法

```bash
# 基本用法
uv run scripts/batch_gaozhi.py <目录名>

# 示例：处理 nlist 目录中的所有 md 文件
uv run scripts/batch_gaozhi.py nlist

# 带详细输出的处理
uv run scripts/batch_gaozhi.py nlist --verbose

# 指定输出文件名
uv run scripts/batch_gaozhi.py nlist --output my_collection

# 脚本会自动保留所有单独的PDF文件
```

## 参数说明

- `目录名`：相对于 `_working/in` 的目录名，包含要处理的 md 文件
- `--output, -o`：输出文件名（不含扩展名），默认为 `{目录名}_merged`
- `--verbose, -v`：显示详细的处理信息

## 工作流程

1. 扫描指定目录中的所有 `.md` 文件
2. 对每个 md 文件调用 `makegaozhi.py` 转换为稿纸格式的 PDF
3. 使用 pymupdf 将所有生成的 PDF 合并成一个大文件
4. 始终保留单独的 PDF 文件

## 输出文件

- 合并后的 PDF 文件：`_working/out/{输出文件名}.pdf`
- 单独的 PDF 文件：`_working/out/{原文件名}.pdf`（始终保留）

## 依赖要求

- `click`：命令行参数处理
- `pymupdf`：PDF 合并功能
- `makegaozhi.py`：单个文件转换脚本
- `pandoc` 和 `typst`：PDF 生成工具

## 示例

```bash
# 处理 nlist 目录，生成 nlist_merged.pdf
uv run scripts/batch_gaozhi.py nlist --verbose

# 处理其他目录，自定义输出文件名
uv run scripts/batch_gaozhi.py my_articles --output my_book
```

## 注意事项

- 输入目录必须位于 `_working/in` 下
- 所有输出文件保存在 `_working/out` 下
- 确保 `makegaozhi.py` 脚本可以正常工作
- 需要安装 pandoc 和 typst 工具
