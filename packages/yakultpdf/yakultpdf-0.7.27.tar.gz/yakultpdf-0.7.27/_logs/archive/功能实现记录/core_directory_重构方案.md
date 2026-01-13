# Core/Directory 重构方案（最终实现版）

## 一、重构背景

根据 cli拆分核查报告，两个主函数存在以下问题：
- `convert_file()` 占 172 行，`convert_directory()` 占 127 行
- 预处理、繁体转换、沙箱创建、Pandoc 调用等逻辑重复度高达 80-100%

---

## 二、✅ 重构完成实际结果

**执行日期**：2023-12-23

### 文件结构变化

```
src/markdown2pdf/
├── __init__.py     (18行)   - 包入口
├── cli.py          (103行)  - CLI 参数解析
├── core.py         (249行)  - 核心转换逻辑（原292行）
├── defaults.py     (31行)   - 默认值
├── directory.py    (162行)  - 目录模式（原209行）
└── utils.py        (148行)  - 共享工具函数（新建）
```

### 行数变化

| 文件 | 重构前 | 重构后 | 变化 |
|-----|--------|--------|-----|
| core.py | 292行 | 249行 | **-43行** ✅ |
| directory.py | 209行 | 162行 | **-47行** ✅ |
| utils.py | 新建 | 148行 | 共享函数集中 |

### 主函数行数（核心指标）

| 函数 | 重构前 | 重构后 | 减少 |
|-----|--------|--------|-----|
| `convert_file()` | 172行 | ~115行 | **-57行** ✅ |
| `convert_directory()` | 127行 | ~86行 | **-41行** ✅ |

### 验证结果

- [x] `uv run pytest` 264 passed ✅
- [x] `uv run md2pdf airdrop_zh.md --verbose` 正常 ✅
- [x] `uv run md2pdf --dir Digital-Assets-Report-EO14178 --verbose` 正常 ✅

---

## 三、实现详情

### utils.py 包含的共享函数

| 函数 | 功能 | 原位置 |
|-----|------|--------|
| `get_config_dirs()` | 获取 tmp_dir 和 input_dir | core.py 内联代码 |
| `inject_default_frontmatter()` | 注入默认 frontmatter | core.py |
| `get_output_filename()` | 从 frontmatter 提取输出文件名 | core.py |
| `apply_default_preprocessing()` | 应用默认预处理链（3步合1） | 新建 |

### core.py 保留的核心函数

| 函数 | 功能 |
|-----|------|
| `execute_in_sandbox()` | 沙箱执行（被 core 和 directory 共享） |
| `convert_file()` | 单文件转换主入口 |

### 关键设计决策

#### 1. get_config_dirs() 不再 fallback

```python
def get_config_dirs() -> tuple[Path, Path]:
    """
    获取 tmp_dir 和 input_dir
    配置加载失败时直接抛出异常。
    """
    from config_manager import ConfigManager
    config = ConfigManager.load()
    return config.tmp_dir, config.input_dir
```

**理由**：配置缺失应该是显式错误，而非静默回退。

#### 2. apply_default_preprocessing() 放在 utils.py

```python
def apply_default_preprocessing(
    content: str,
    removelink: bool = False,
    verbose: bool = False,
) -> str:
    """
    执行顺序：
    1. pre_remove_links（可选）
    2. pre_add_line_breaks
    3. pre_for_typst
    """
```

**理由**：这是 markdown2pdf 特有的预处理组合，不属于通用的 helper_markdown。

#### 3. execute_in_sandbox() 保留在 core.py

参数化设计解决 core 和 directory 的差异：

| 参数 | core.py 调用 | directory.py 调用 |
|-----|-------------|------------------|
| `temp_filename` | 原文件名 | `{output_name}.md` |
| `images_source_dir` | `input_dir` | `dir_path` |
| `sandbox_prefix` | `"md2pdf_"` | `"md2pdf_dir_"` |

#### 4. execute_in_sandbox 不导出到 __init__.py

仅供包内使用，不作为公共 API。

---

## 四、模块依赖关系

```
cli.py
    ├─→ core.convert_file()
    └─→ directory.convert_directory()

core.py
    ├─→ utils.get_config_dirs()
    ├─→ utils.inject_default_frontmatter()
    ├─→ utils.get_output_filename()
    ├─→ utils.apply_default_preprocessing()
    └─→ execute_in_sandbox() [内部]

directory.py
    ├─→ core.execute_in_sandbox()
    ├─→ utils.get_config_dirs()
    ├─→ utils.get_output_filename()
    └─→ utils.apply_default_preprocessing()
```

---

## 五、待办事项

以下问题已在重构中确认：

| 问题 | 决定 |
|-----|------|
| helper_markdown 是否接受新函数？ | ❌ 不接受，放在 utils.py |
| 是否导出 execute_in_sandbox？ | ❌ 不导出，仅内部使用 |
| convert_directory 是否支持 postprocess？ | 暂不支持，需要时再添加 |


---

## 附录：P4 优化方案建议 (ConversionOptions)

### 1. 痛点：参数爆炸

目前 `convert_file` 和 `convert_directory` 函数的参数列表过长且重复，每次新增功能（如添加 `--header`）都需要修改多处函数签名，扩展性差。

### 2. 解决方案

使用 `dataclass` 封装转换选项：

#### 新建 `src/markdown2pdf/options.py`

```python
from dataclasses import dataclass

@dataclass
class ConversionOptions:
    """转换配置选项"""
    template: str = "nb.typ"
    cover: bool = False
    coverimg: str | None = None
    to_typst: bool = False
    savemd: bool = False
    removelink: bool = False
    tc: bool = False
    overwrite: bool = False
    verbose: bool = False
    # 未来可轻松扩展：
    # header_text: str | None = None
```

### 3. 代码对比

#### 优化前（现状）

```python
# core.py
def convert_file(
    input_file: str,
    # --- 这一长串在每个函数里都要抄一遍 ---
    template: str = DEFAULT_TEMPLATE,
    cover: bool = False,
    coverimg: str | None = None,
    to_typst: bool = False,
    ... (10+ 个参数)
)
```

#### 优化后

```python
# core.py
from .options import ConversionOptions

def convert_file(
    input_file: str,
    output_file: str | None = None,
    options: ConversionOptions = ConversionOptions(),  # 仅需一个参数
    # 路径参数仍可根据需要保留
    indir: str = "_working/in",
    outdir: str = "_working/out",
)
```

### 4. 实施步骤

1.  **定义**：在 `options.py` 中定义 `ConversionOptions`。
2.  **修改 CLI**：在 `cli.py` 中解析参数后，构建 `options` 对象。
3.  **内聚**：core 和 directory 中的函数改为接收 `options` 对象。
4.  **调用**：更新 `createpdf.py` 和所有单元测试的调用方式。

### 5. 收益

- **整洁**：函数签名极其干净。
- **易扩展**：新增参数只需修改 `ConversionOptions` 定义和 CLI 解析，无需动核心逻辑签名。
- **类型安全**：所有选项都有明确类型。

