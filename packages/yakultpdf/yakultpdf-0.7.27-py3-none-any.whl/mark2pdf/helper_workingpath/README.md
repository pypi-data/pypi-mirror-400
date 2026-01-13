# Working Path Helper

一个用于管理项目工作目录结构的 Python 工具库，提供安全的目录创建、文件路径解析和安全保存功能。

## 功能特性

- ✅ 自动检测项目根目录（通过 pyproject.toml 或 package.json）
- ✅ 安全创建工作目录结构
- ✅ 智能输入输出路径解析
- ✅ 文件安全保存（避免覆盖现有文件）
- ✅ 可配置的输入输出目录（读取 mark2pdf.config.toml）
- ✅ 完整的错误处理和验证

## 安装和使用

### 1. 安装为包（推荐）

将 `working_path` 目录放在您的 scripts 目录中：

```bash
# 方式1：放在项目 scripts 目录中
cp -r /path/to/working_path /your/project/scripts/

# 方式2：放在 site-packages 中（需要setup.py或pyproject.toml配置）
# 推荐使用 uv add . 进行可编辑安装
```

### 2. 确保在 Python 路径中

确保您的项目结构正确，Python 可以找到 working_path 包：

```
your_project/
├── scripts/
│   ├── working_path/          # 拷贝到这里
│   │   ├── __init__.py
│   │   ├── working_path_helper.py
│   │   ├── test_working_path_helper.py
│   │   └── README.md
│   └── your_main_script.py    # 您的脚本也在这里
├── pyproject.toml
└── ...
```

### 2. 导入使用

在您的代码中导入所需函数（uv 会自动处理 Python 路径）：

```python
# 方式 1：从包中导入函数（推荐）
from working_path import (
    get_project_root,
    create_working_dirs,
    safesave_path,
    resolve_inout_paths
)

# 方式 2：导入整个模块
from working_path import working_path_helper

# 方式 3：直接导入特定函数
from working_path.working_path_helper import create_working_dirs, resolve_inout_paths
```

### 3. 不同目录结构的导入方式

#### 3.1 在项目根目录的 scripts/ 中使用（推荐）

```python
# 当 working_path 在 scripts/ 目录中时
from working_path import resolve_inout_paths, get_project_root
```

#### 3.2 在子目录中使用（如 tmp/ 目录）

```python
# 当脚本在子目录中，working_path 也在同一子目录时
from working_path import resolve_inout_paths, get_project_root
```

#### 3.3 从项目根目录的 src/ 包中导入

```python
# 当 working_path 在 src/aibench/working_path 中时
from aibench.working_path import resolve_inout_paths, get_project_root
```

#### 3.4 解决相对导入问题

**问题**：相对导入 `from .working_path import ...` 不工作

**原因**：相对导入只能在包（package）内部使用，而独立的脚本文件不是包的一部分。

**解决方案**：
- 使用绝对导入：`from working_path import ...`
- 或者添加路径到 sys.path（不推荐）

```python
# ❌ 错误：相对导入在独立脚本中不工作
from .working_path import resolve_inout_paths

# ✅ 正确：使用绝对导入
from working_path import resolve_inout_paths, get_project_root
```

## 核心函数

### `get_project_root() -> Path`

获取项目根目录（通过查找项目标识文件）。

**优先级顺序：**
1. `pyproject.toml` - Python 项目
2. `package.json` - Node.js 项目

```python
root = get_project_root()
print(f"项目根目录：{root}")
```

### `create_working_dirs() -> dict`

创建标准的工作目录结构。

```python
dirs = create_working_dirs()
print(f"工作目录：{dirs['working']}")
print(f"输入目录：{dirs['in']}")
print(f"输出目录：{dirs['out']}")
print(f"临时目录：{dirs['tmp']}")
```

**目录结构：**
```
project_root/
├── in/      # 输入文件目录
├── out/     # 输出文件目录
└── tmp/     # 临时文件目录
```

### `safesave_path(filename) -> str`

安全保存路径，如果文件已存在则添加时间戳。

```python
# 文件不存在时返回原路径
path1 = safesave_path("output.txt")  # "output.txt"

# 文件存在时添加时间戳
path2 = safesave_path("existing.txt")  # "existing_09-18-1430.txt"
```

### `resolve_inout_paths(infile, outfile=None, indir=None, outdir=None, ext="md") -> tuple`

解析输入和输出文件路径。

**重要限制：输入文件名不能包含目录路径，必须是纯文件名**

```python
# 基本用法
in_path, out_path = resolve_inout_paths("input.md")
# in_path: "/project/in/input.md"
# out_path: "/project/out/input_09-18-1430.md"

# 自定义输出文件名
in_path, out_path = resolve_inout_paths("input.md", outfile="result")
# out_path: "/project/out/result_09-18-1430.md"

# 自定义输出扩展名
in_path, out_path = resolve_inout_paths("input.txt", ext="csv")
# out_path: "/project/out/input_09-18-1430.csv"

# 错误示例：包含目录路径（将被拒绝）
in_path, out_path = resolve_inout_paths("subdir/input.md")
# 返回：(None, None) 并显示错误信息

# 错误示例：相对路径（将被拒绝）
in_path, out_path = resolve_inout_paths("./input.md")
# 返回：(None, None) 并显示错误信息
```

## 完整示例

```python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click",
# ]
# ///
import click
from working_path import (
    get_project_root,
    create_working_dirs,
    resolve_inout_paths,
    safesave_path
)

@click.group()
def cli():
    """Working Path Helper CLI - 工作目录管理工具命令行界面"""
    pass

@cli.command()
def root():
    """显示项目根目录"""
    try:
        root_dir = get_project_root()
        click.echo(f"📦 项目根目录：{root_dir}")
    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)

@cli.command()
def init():
    """初始化工作目录结构"""
    try:
        dirs = create_working_dirs()
        click.echo(f"✅ 目录创建成功：")
        for name, path in dirs.items():
            click.echo(f"  {name}: {path}")
    except FileExistsError as e:
        click.echo(f"⚠️  {e}")

@cli.command()
@click.argument('input_file')
@click.option('--output', '-o', help='输出文件名')
@click.option('--ext', default='md', help='输出文件扩展名')
def process(input_file, output, ext):
    """处理输入文件并保存到输出目录"""
    # 解析输入输出路径
    in_path, out_path = resolve_inout_paths(
        input_file,
        outfile=output,
        ext=ext
    )

    if not in_path or not out_path:
        click.echo("❌ 路径解析失败", err=True)
        return

    click.echo(f"📁 输入文件：{in_path}")
    click.echo(f"💾 输出文件：{out_path}")

    # 示例处理：转换为大写
    try:
        with open(in_path, 'r', encoding='utf-8') as f_in:
            content = f_in.read()

        processed_content = content.upper()

        with open(out_path, 'w', encoding='utf-8') as f_out:
            f_out.write(processed_content)

        click.echo(f"✅ 处理完成：{out_path}")

    except FileNotFoundError:
        click.echo(f"❌ 输入文件不存在：{in_path}", err=True)
    except Exception as e:
        click.echo(f"❌ 处理错误：{e}", err=True)

if __name__ == "__main__":
    cli()
```

## 错误处理

### 目录已存在错误
```python
try:
    dirs = create_working_dirs()
except FileExistsError as e:
    print(f"目录已存在：{e}")
    # 处理已存在的情况
```


### 文件不存在错误
```python
in_path, out_path = resolve_inout_paths("nonexistent.md")
if in_path is None:
    print("输入文件不存在")
```

### 目录路径验证错误
```python
# 包含目录路径的文件名将被拒绝
in_path, out_path = resolve_inout_paths("subdir/file.md")
if in_path is None:
    print("输入文件名包含目录路径，请输入纯文件名")

# 相对路径也将被拒绝
in_path, out_path = resolve_inout_paths("./file.md")
if in_path is None:
    print("输入文件名包含目录路径，请输入纯文件名")
```

## 配置选项

### 工作目录配置
- 若存在 `mark2pdf.config.toml`，优先使用其中的 `paths.in/out/tmp`
- 否则使用项目根目录下的 `in/out/tmp`

### 路径解析配置
- 输入目录：从配置读取，未配置则默认 `in`
- 输出目录：从配置读取，未配置则默认 `out`
- 输出扩展名：`md` （可配置）
- **输入限制**：输入文件名必须是纯文件名，不能包含目录路径

## 测试

运行测试确保功能正常：

```bash
# 进入 scripts 目录
cd /your/project/scripts/working_path

# 运行所有测试
uv run pytest test_working_path_helper.py -v

# 运行特定测试
uv run pytest test_working_path_helper.py::test_create_working_dirs -v

# 运行测试并生成覆盖率报告
uv run pytest test_working_path_helper.py --cov=working_path_helper --cov-report=html

# 运行Python脚本示例
uv run python -c "from working_path import create_working_dirs; print('✅ 导入成功')"
```

## 注意事项

1. **项目要求**：项目根目录必须包含以下任一标识文件（按优先级顺序）：
   - `pyproject.toml`（Python 项目）
   - `package.json`（Node.js 项目）
2. **uv 工具**：推荐使用 `uv run` 来运行脚本和测试，uv 会自动处理 Python 路径
3. **目录结构**：将 working_path 放在 scripts/ 目录中，与您的脚本在一起
4. **导入方式**：使用绝对导入 `from working_path import ...`，避免相对导入 `from .working_path import ...`
5. **目录权限**：确保有创建目录的写入权限
6. **文件安全**：`safesave_path` 防止意外覆盖重要文件
7. **输入验证**：输入文件名必须是纯文件名，不能包含目录路径（`/` 或 `\`）
8. **错误处理**：始终处理可能抛出的异常
