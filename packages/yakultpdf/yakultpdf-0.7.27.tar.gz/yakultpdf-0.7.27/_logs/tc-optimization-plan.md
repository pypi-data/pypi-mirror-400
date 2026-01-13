# 繁体转换(tc)优化方案

## 问题分析（经核查确认）

### 问题一：重复执行（已确认）

完整调用链追踪：

```
CLI (cli.py:101-102)
  ├─ tc=True → 构建 postprocess 函数链（包含 to_traditional_chinese）
  └─ 调用 run_conversion(postprocess=final_postprocess, tc=tc)
        │
        ▼
conversion.py (65-85)
  ├─ 构建 ConversionOptions(tc=tc)  
  └─ 调用 convert_file(postprocess=postprocess, ...)
        │
        ▼
core.py (257-263)
  ├─ postprocess(content)         ← 第一次转换（来自后处理链）
  └─ if options.tc:
         convert_to_traditional() ← 第二次转换（core 内部）
```

**同样的问题也存在于**：
- `core.py` 的 `convert_from_string()` 函数（355-358行）
- `directory.py` 的 `convert_directory()` 函数（168-174行）

### 问题二：每次新建实例

`utils.py:22-23`：
```python
def convert_to_traditional(text: str) -> str:
    return OpenCC("s2t").convert(text)
```
每次调用都 new 一个 OpenCC 实例。

### 问题三：无条件加载

`utils.py` 顶部 `from opencc import OpenCC`，即使不用 tc 也要加载。

## 修改方案

### 1. 去除重复执行

**调整方案**：保留 core 层的 tc 转换（确保最终输出全量转换），CLI 构建后处理器链时不再加入 `to_traditional_chinese`，避免双重转换。

涉及文件：
- `src/mark2pdf/cli.py`：构建 postprocess 链时禁用 tc 处理器
- `src/mark2pdf/process_builder.py`：支持显式控制 tc 是否加入 postprocess

### 2. 按需加载 + 单例缓存

修改 `utils.py`：

```python
# 删除顶部的: from opencc import OpenCC

# 替换 convert_to_traditional 函数为：
_opencc_s2t = None

def convert_to_traditional(text: str) -> str:
    """转换为繁体中文（按需加载 OpenCC）"""
    global _opencc_s2t
    if _opencc_s2t is None:
        from opencc import OpenCC
        _opencc_s2t = OpenCC("s2t")
    return _opencc_s2t.convert(text)
```

## 涉及文件汇总

| 文件 | 修改内容 |
|------|----------|
| `src/mark2pdf/core/utils.py` | 删除顶部 import，改用按需加载 + 单例 |
| `src/mark2pdf/cli.py` | tc 不再加入 postprocess 链，避免重复转换 |
| `src/mark2pdf/process_builder.py` | 支持控制 tc 是否加入 postprocess |

## 效果

- 不使用 `--tc` 时：不加载 opencc 模块，无额外开销
- 使用 `--tc` 时：只加载一次 OpenCC，只执行一次转换
