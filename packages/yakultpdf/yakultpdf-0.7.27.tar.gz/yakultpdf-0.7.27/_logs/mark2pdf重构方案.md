# mark2pdf 重构方案

## 背景

当前项目名 `mark2pdf` 在 PyPI 上已被占用，且存在多个顶级模块（`markdown2pdf`、`helper_*` 等）可能与其他包冲突。

**目标**：重命名为 `mark2pdf`，并将所有模块整合到单一命名空间下。

---

## 一、模块映射

### 主包

`mark2pdf` → `mark2pdf`

### 子模块

| 原模块 | 新模块 |
|-------|-------|
| `markdown2pdf` | `mark2pdf.core` |
| `helper_markdown` | `mark2pdf.helper_markdown` |
| `helper_typst` | `mark2pdf.helper_typst` |
| `helper_gaozhi` | `mark2pdf.helper_gaozhi` |
| `helper_interfile` | `mark2pdf.helper_interfile` |
| `helper_mdimage` | `mark2pdf.helper_mdimage` |
| `helper_workingpath` | `mark2pdf.helper_workingpath` |
| `postprocess` | `mark2pdf.postprocess` |

---

## 二、目录结构

### 当前

```
├── template/             # 项目根目录下
src/
├── mark2pdf/
├── markdown2pdf/
├── helper_markdown/
├── helper_typst/
├── ...
└── postprocess/
```

### 目标

```
src/mark2pdf/
├── __init__.py         # 公开 API
├── cli.py
├── config.py
├── conversion.py
├── core/               # 原 markdown2pdf
├── helper_markdown/
├── helper_typst/
├── helper_xxx/
├── postprocess/
├── commands/
├── resources/
└── templates/          # 原 template/（移入包内）
```

---

## 三、变更操作

### 3.1 目录移动

```bash
mv src/mark2pdf src/mark2pdf
mv src/markdown2pdf src/mark2pdf/core
mv src/helper_* src/mark2pdf/
mv src/postprocess src/mark2pdf/postprocess
mv template src/mark2pdf/templates    # 模板移入包内
```

### 3.2 import 替换规则

| 原 | 新 |
|---|---|
| `from markdown2pdf import X` | `from mark2pdf.core import X` |
| `from helper_xxx import Y` | `from mark2pdf.helper_xxx import Y` |
| `from mark2pdf import Z` | `from mark2pdf import Z` |
| `from postprocess import W` | `from mark2pdf.postprocess import W` |

### 3.3 pyproject.toml

```toml
[project]
name = "mark2pdf"
version = "0.7.0"

[project.scripts]
mark2pdf = "mark2pdf.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/mark2pdf"]
# templates/ 已在包内，无需 force-include
```

---

## 四、公开 API

`mark2pdf/__init__.py` 导出：

```python
# 核心 API
from .core import convert_file, convert_from_string, convert_directory

# 配置
from .config_loader import ConfigManager

# 版本（从 pyproject.toml 读取）
__version__ = ...
```

**Python 调用**：

```python
from mark2pdf import convert_file
convert_file("doc.md")
```

**CLI 使用方式**（推荐 `uv run`）：

```bash
uv run mark2pdf sample.md                    # 转换单个文件
uv run mark2pdf --dir docs                   # 转换整个目录
uv run mark2pdf sample.md --indir in         # 自定义输入目录
```

---

## 五、实施步骤

1. 创建分支 `refactor/mark2pdf`  -> （无需,当前分支）
2. 移动目录（按 3.1）
3. 批量替换 import（按 3.2）
4. 更新 `pyproject.toml`
5. 运行测试 `uv run pytest`
6. 测试 CLI `mark2pdf --help`
7. 更新 README

---

## 六、注意事项

- 检查相对导入（模块内部 `from .xxx import`）
- 更新资源文件路径引用
- 测试文件中的 import 也需更新
