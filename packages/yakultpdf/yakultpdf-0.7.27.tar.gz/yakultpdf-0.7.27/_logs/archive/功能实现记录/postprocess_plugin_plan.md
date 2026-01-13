# Postprocess 插件完善计划

日期：2024-12-31

---

## 一、新设计思路

### 核心设计：CLI 参数 = 后处理器快捷方式

```
--removelink  ≡  --postprocess remove_links
--tc          ≡  --postprocess tc_convert
```

**好处**：
1. 统一走 postprocess 机制，不需要额外参数层层传递
2. `remove_links` 和 `tc_convert` 成为后处理器的典型示例
3. CLI 参数只是后处理器的语法糖
4. 未来扩展只需添加新的 postprocess 即可

### 架构设计

```
src/
├── postprocess/                  # 独立包：预设后处理器
│   ├── __init__.py               # 导出所有处理器
│   ├── remove_links.py           # 移除链接
│   └── tc_convert.py             # 繁体转换
└── markdown2pdf/
    ├── postprocess.py            # 插件加载逻辑 (load_postprocessor)
    └── ...
```

**说明**：
- `src/postprocess/` - 独立包，存放预设处理器（可被其他项目复用）
- `markdown2pdf/postprocess.py` - 插件加载逻辑，属于 markdown2pdf
- 现有 `markdown2pdf/postprocessors/` 目录将被删除

---

## 二、实施计划

### 2.0 任务0：创建独立包结构

**新建目录**：`src/postprocess/`

**新建**：`src/postprocess/__init__.py`

```python
"""
postprocess 包

预设后处理器集合。
"""

from .remove_links import process as remove_links
from .tc_convert import process as tc_convert

__all__ = ["remove_links", "tc_convert"]
```

**删除**：`src/markdown2pdf/postprocessors/` 目录（含 abc_postprocess.py）

---

### 2.1 任务1：创建 `remove_links` 后处理器

**新建**：`src/postprocess/remove_links.py`

```python
"""
移除链接后处理器

移除 Markdown 内容中的链接，保留图片。
"""

from helper_markdown import pre_remove_links


def process(content: str) -> str:
    """
    移除链接（保留图片）
    
    Args:
        content: Markdown 内容
        
    Returns:
        移除链接后的内容
    """
    return pre_remove_links(content, verbose=False)
```

---

### 2.2 任务2：创建 `tc_convert` 后处理器

**新建**：`src/postprocess/tc_convert.py`

```python
"""
繁体中文转换后处理器

将简体中文内容转换为繁体中文。
"""

from opencc import OpenCC


def process(content: str) -> str:
    """
    转换为繁体中文
    
    Args:
        content: 原始内容
        
    Returns:
        繁体中文内容
    """
    cc = OpenCC("s2t")
    return cc.convert(content)
```

---

### 2.3 任务3：创建 `load_postprocessor` 加载器

**新建**：`src/markdown2pdf/postprocess.py`

```python
"""
后处理器加载器

提供 load_postprocessor 函数，从 postprocess 包加载预设处理器。
"""

from collections.abc import Callable


def load_postprocessor(name: str) -> Callable[[str], str] | None:
    """
    加载后处理器
    
    Args:
        name: 处理器名称（如 "remove_links", "tc_convert"）
        
    Returns:
        处理器函数，或 None（未找到）
    """
    try:
        import postprocess
        processor = getattr(postprocess, name, None)
        if callable(processor):
            return processor
    except ImportError:
        pass
    
    return None
```

---

### 2.4 任务4：修改 CLI 逻辑

**修改**：`src/mark2pdf/cli.py` 的 `convert` 函数

**核心改动**：将 `--removelink` 和 `--tc` 转换为 postprocessor 调用

```python
def convert(..., removelink: bool, tc: bool, postprocess: str | None, ...):
    # 构建后处理器列表
    processors = []
    
    if removelink:
        processors.append("remove_links")
    if tc:
        processors.append("tc_convert")
    if postprocess:
        processors.append(postprocess)
    
    # 加载并组合后处理器
    final_postprocess = None
    if processors:
        from markdown2pdf.postprocess import load_postprocessor
        
        funcs = [load_postprocessor(p) for p in processors]
        funcs = [f for f in funcs if f]  # 过滤 None
        
        if funcs:
            def combined(content: str) -> str:
                for fn in funcs:
                    content = fn(content)
                return content
            final_postprocess = combined
    
    # 调用 run_conversion 时传递 postprocess
    run_conversion(..., postprocess=final_postprocess, ...)
```

**说明**：
- 不再需要传递 `removelink` 和 `tc` 参数到底层
- 底层只接收 `postprocess` 函数即可
- 多个处理器可以组合执行

---

### 2.5 任务5（可选）：清理底层代码

移除 `ConversionOptions` 中的 `removelink` 和 `tc` 字段，
以及 `core.py`、`directory.py` 中的相关逻辑。

**影响范围**：
- `markdown2pdf/options.py` - 移除字段
- `markdown2pdf/core.py` - 移除内联 tc 转换逻辑
- `markdown2pdf/directory.py` - 移除内联 tc 转换逻辑
- `markdown2pdf/utils.py` - 移除 `apply_default_preprocessing` 中的 removelink 逻辑

**建议**：先完成1-4，测试通过后再做清理。

---

## 三、调用链路变化

### 变更前

```
CLI --removelink/--tc
    ↓ (参数断链)
conversion.py（未接收参数）
    ↓
core.py ConversionOptions（有字段但未设置）
    ↓
无效
```

### 变更后

```
CLI --removelink/--tc
    ↓ 转换为 postprocessor 名称
load_postprocessor("remove_links"/"tc_convert")
    ↓ 返回处理函数
conversion.py（接收 postprocess 函数）
    ↓
core.py convert_file(postprocess=...)
    ↓
执行后处理
```

---

## 四、测试计划

```bash
# 测试 remove_links
uv run mark2pdf convert sample.md --removelink -v

# 测试 tc_convert
uv run mark2pdf convert sample.md --tc -v

# 测试组合
uv run mark2pdf convert sample.md --removelink --tc -v

# 测试显式 postprocess
uv run mark2pdf convert sample.md -p remove_links -v

# 运行单元测试
uv run pytest src/markdown2pdf/tests/ -v
uv run pytest src/mark2pdf/tests/ -v
```

---

## 五、实施优先级

| 顺序 | 任务 | 工作量 |
|------|------|--------|
| 1 | 创建 `remove_links.py` | 小 |
| 2 | 创建 `tc_convert.py` | 小 |
| 3 | 更新 `__init__.py` | 小 |
| 4 | 修改 CLI 逻辑 | 中 |
| 5 | 清理底层代码（可选） | 中 |

---

## 六、插件动态加载（后续规划）

待完成基础功能后，可扩展支持：
- 工作区自定义插件：`./postprocess/<name>.py`
- importlib 动态加载 .py 文件
- 多处理器组合顺序控制
```
