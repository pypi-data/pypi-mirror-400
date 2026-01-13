# createpdf --batch 模式实现方案

## 需求描述

为 `createpdf.py` 增加 `--batch` 模式，该模式与 `--dir` 的区别：
- `--dir`：合并目录中所有 Markdown 文件为一个 PDF
- `--batch`：逐一为目录中每个 Markdown 文件生成独立的 PDF

## 使用场景

```bash
# 场景1：处理当前目录 "."
createpdf.py --batch .
# 输出：out/文件1.pdf, out/文件2.pdf, ...

# 场景2：处理子目录 "任务发布"
createpdf.py --batch 任务发布
# 输出：out/任务发布/文件1.pdf, out/任务发布/文件2.pdf, ...
```

## Frontmatter 优先级

1. **单文件 frontmatter**（最高优先级）
2. **目录中 index.md 的 frontmatter**（中优先级）
3. **工作区 frontmatter.yaml**（最低优先级）

## 技术设计

### 1. CLI 修改 (`createpdf.py`)

添加新选项：
```python
@click.option("--batch", "-b", "batch_dir", default=None, 
              help="批量模式：逐一转换目录中每个 Markdown 文件")
```

### 2. 新增函数 (`conversion.py`)

```python
def run_batch_conversion(
    directory: str,
    workspace_dir: Path,
    *,
    verbose: bool = False,
    overwrite: bool = False,
    template: str | None = None,
    tc: bool = False,
) -> bool:
```

### 3. 核心逻辑

1. **确定输入目录**：`{input_path}/{directory}`
2. **确定输出目录**：
   - 如果 `directory == "."` → 输出到 `out/`
   - 如果 `directory == "任务发布"` → 输出到 `out/任务发布/`
3. **读取目录级 frontmatter**：
   - 检查目录中是否有 `index.md`
   - 如果有，提取其 frontmatter 作为目录级默认值
4. **遍历 Markdown 文件**：
   - 获取目录中所有 `.md` 文件（排除 `index.md`）
   - 对每个文件调用 `convert_file()`
5. **Frontmatter 合并**：
   - 基础层：工作区的 `frontmatter.yaml`
   - 目录层：`index.md` 的 frontmatter
   - 文件层：各文件自己的 frontmatter（在 `convert_file` 内部处理）

### 4. 输出目录处理

需要修改 `convert_file()` 或在调用时指定正确的 `outdir`：

```python
# 确定输出子目录
if directory == ".":
    batch_outdir = config.paths.output
else:
    batch_outdir = f"{config.paths.output}/{directory}"
```

## 实现步骤

1. 在 `conversion.py` 中添加 `run_batch_conversion()` 函数
2. 在 `__init__.py` 中导出该函数
3. 修改 `createpdf.py` 添加 `--batch` 选项
4. 同步 `_working/createpdf.py`

## 注意事项

- index.md 本身不会被转换，只用于提供目录级配置
- 需要处理空目录的情况
- 需要汇报处理进度（成功/失败计数）
- 考虑是否需要并行处理（初期可以串行）
