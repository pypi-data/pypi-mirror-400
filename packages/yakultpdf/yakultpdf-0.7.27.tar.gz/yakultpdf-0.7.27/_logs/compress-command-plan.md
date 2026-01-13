# compress 命令实现计划

## 目标

新增 `mark2pdf compress` 命令，使用 PyMuPDF 压缩 PDF 文件大小。

## 命令设计

```bash
mark2pdf compress [FILENAME]     # 压缩单个文件（相对于 out 目录）
mark2pdf compress --all          # 压缩 out 目录下所有 PDF
mark2pdf compress --no-overwrite # 不覆盖，生成 xxx_sm.pdf
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `FILENAME` | 可选，PDF 文件名（相对于 out 目录） |
| `--all` | 压缩 out 目录下所有 PDF |
| `--no-overwrite` | 输出为 `原名_sm.pdf`，缺省覆盖原文件 |
| `--dpi` | 图片重采样 DPI，缺省 150 |
| `--verbose, -v` | 显示压缩详情 |

## 压缩策略

### 1. 基础压缩（始终执行）

```python
doc.scrub()     # 清除元数据、缩略图等
doc.ez_save()   # garbage=3 + deflate 压缩
```

### 2. 图片压缩

- **降低 DPI**：将图片重采样到指定 DPI（缺省 150）
- **PNG → JPEG**：将无损 PNG 转为有损 JPEG（质量 85）
- **保留透明**：带 alpha 通道的 PNG 保持不变

```python
for page in doc:
    for img in page.get_images():
        # 检查格式，PNG 且无透明 → 转 JPEG
        # 重采样到目标 DPI
        page.replace_image(xref, new_image)
```

## 实现

### 新建文件

`src/mark2pdf/commands/compress.py`

### 注册命令

`cli.py` 和 `commands/__init__.py` 中添加 `compress`

### 依赖

`pyproject.toml` 添加 `pymupdf`

## 输出示例

```
✅ sample.pdf: 2.5MB → 1.2MB (-52%)
✅ report.pdf: 5.0MB → 2.1MB (-58%)
📊 共压缩 2 个文件，节省 4.2MB
```
