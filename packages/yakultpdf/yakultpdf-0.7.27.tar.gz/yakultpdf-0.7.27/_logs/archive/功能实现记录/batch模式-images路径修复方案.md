# Batch 模式 images 路径修复方案

## 问题

batch 模式下，`convert_file()` 的 `images_source_dir` 从 `config.input_dir` 获取，
导致图片路径错误：

- 期望：`in/任务发布/images/`
- 实际：`in/images/`

---

## 潜在漏洞分析

### 漏洞 1：`resolve_inout_paths` 的路径拼接逻辑

`resolve_inout_paths()` 有特殊的路径处理逻辑（第 145-162 行）：

```python
is_default_indir = indir == "_working/in"

if config is not None and config.data_root is not None:
    if is_default_indir:
        indir_path = config.input_dir           # 使用 config 的绝对路径
    else:
        indir_path = config.data_root / indir   # ⚠️ 拼接 data_root + indir
```

**问题**：如果 batch 模式传入 `indir="in/任务发布"`：
- `is_default_indir = False`
- `indir_path = data_root / "in/任务发布"`

这个逻辑是正确的，但需要确保 batch 模式传入的是相对路径（如 `in/任务发布`），而不是绝对路径。

### 漏洞 2：`core.py` 的 overwrite 分支路径计算

`convert_file()` 第 147-162 行有一个 overwrite 分支：

```python
if options.overwrite:
    outdir_path = root_dir / outdir
    output_path = outdir_path / f"{input_path_obj.stem}.{ext}"
```

这里直接用 `root_dir / outdir` 计算输出路径。如果 `outdir` 是 `out/任务发布`，会正确拼接。
✅ 无问题

### 漏洞 3：images_source_dir 需要绝对路径

`execute_in_sandbox` 期望 `images_source_dir` 是绝对路径（用于 symlink）。

如果我们直接用 `indir` 参数，需要确保转换为绝对路径。

**核心问题**：`indir` 参数可能是：
- 相对路径：`in/任务发布` → 需要拼接 `data_root`
- 绝对路径：`/Users/.../in/任务发布` → 直接使用

### 漏洞 4：Path.cwd() vs data_root

方案中写的是：
```python
indir_path = Path(indir)
if not indir_path.is_absolute():
    indir_path = Path.cwd() / indir_path  # ⚠️ 使用 cwd
```

但实际上项目使用的是 `data_root`（工作区目录），不是 `cwd`。

**应该改为**：
```python
if not indir_path.is_absolute():
    indir_path = config.data_root / indir_path  # ✅ 使用 data_root
```

### 漏洞 5：单文件模式的兼容性

单文件模式调用链：`run_conversion()` → `convert_file(indir=config.paths.input)`

`config.paths.input` 是什么？查看 `ConfigManager`：
- 通常是 `"_working/in"` 或自定义相对路径

单文件模式期望图片在 `in/images/`，修改后：
- `indir = "_working/in"` → `images_source_dir = data_root / "_working/in"` ✅

兼容性 OK。

---

## 修正后的方案

### 核心修改

#### 1. `convert_file()` (core.py)

```python
# 当前（第 206 行）
tmp_dir, input_dir = get_config_dirs()

return execute_in_sandbox(
    ...
    images_source_dir=input_dir,
    ...
)


# 改为
from config_manager import ConfigManager

config = ConfigManager.load()
tmp_dir = config.tmp_dir

# 从 indir 参数推导 images 来源（需要绝对路径）
indir_path = Path(indir)
if not indir_path.is_absolute():
    if config.data_root:
        indir_path = config.data_root / indir
    else:
        indir_path = get_project_root() / indir

return execute_in_sandbox(
    ...
    images_source_dir=indir_path,  # ✅ 从 indir 参数推导
    ...
)
```

**注意**：这里不需要新的 `get_tmp_dir()` 函数，因为 `convert_file` 内部已经有
ConfigManager 的 import（第 151 行的 overwrite 分支）。可以复用。

#### 2. 简化：不修改 utils.py

既然 `core.py` 会自己加载 ConfigManager，可以保留 `get_config_dirs()` 但不再使用。
或者直接删除 `get_config_dirs()` 这个函数（如果没有其他调用者）。

#### 3. `directory.py` 同步修改

```python
# 当前（第 156 行）
tmp_dir, _ = get_config_dirs()

# 改为：直接获取 tmp_dir
from config_manager import ConfigManager
config = ConfigManager.load()
tmp_dir = config.tmp_dir
```

#### 4. `run_batch_conversion()` 修正

```python
# 确定每个文件的输入/输出目录
if directory == ".":
    file_indir = config.paths.input      # "in" 或 "_working/in"
    file_outdir = config.paths.output
else:
    file_indir = f"{config.paths.input}/{directory}"   # "in/任务发布"
    file_outdir = f"{config.paths.output}/{directory}"

result = convert_file(
    input_file=md_file.name,  # 纯文件名
    indir=file_indir,
    outdir=file_outdir,
    ...
)
```

---

## 修改文件清单

1. **`src/markdown2pdf/core.py`**
   - 移除 `get_config_dirs()` 调用
   - 直接使用 ConfigManager 获取 `tmp_dir`
   - 从 `indir` 参数推导 `images_source_dir`（注意绝对路径转换）

2. **`src/markdown2pdf/directory.py`**
   - 移除 `get_config_dirs()` 调用
   - 直接使用 ConfigManager 获取 `tmp_dir`

3. **`src/markdown2pdf/utils.py`**
   - 删除 `get_config_dirs()` 函数（或标记为 deprecated）

4. **`src/config_manager/conversion.py`**
   - `run_batch_conversion()` 调整 indir/outdir 为包含子目录的相对路径

---

## 测试要点

1. **单文件模式**：`createpdf.py 文件名`
   - 图片从 `in/images/` ✅

2. **目录模式**：`createpdf.py --dir 目录名`
   - 图片从 `in/目录名/images/` ✅（本来就是对的，使用 `dir_path`）

3. **batch 模式**：`createpdf.py --batch 目录名`
   - 图片从 `in/目录名/images/` ✅

4. **batch 模式 + 当前目录**：`createpdf.py --batch .`
   - 图片从 `in/images/` ✅
