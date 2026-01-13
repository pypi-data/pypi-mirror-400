# Python lru_cache 装饰器说明

## 什么是 lru_cache

`lru_cache` 是 Python 标准库 `functools` 模块中的装饰器，用于**缓存函数返回值**。

LRU = Least Recently Used（最近最少使用），当缓存满时，自动删除最久未使用的结果。

## 基本用法

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(n):
    print(f"计算 {n}...")
    return n * n

# 第一次调用，执行函数
result = expensive_function(5)  # 输出: 计算 5...

# 第二次调用相同参数，直接返回缓存，不执行函数
result = expensive_function(5)  # 无输出
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `maxsize=128` | 缓存最多 128 个不同参数的结果（默认） |
| `maxsize=None` | 无限制缓存 |
| `maxsize=1` | 只缓存最后一次调用结果 |
| `typed=True` | 区分类型，`f(3)` 和 `f(3.0)` 分别缓存 |

## 适用场景

1. **昂贵的计算**：结果不变但计算耗时的函数
2. **单例模式**：用 `maxsize=1` 缓存一个实例
3. **递归优化**：如斐波那契数列，避免重复计算

## 本项目中的应用

```python
# utils.py
@lru_cache(maxsize=1)
def _get_opencc_s2t():
    from opencc import OpenCC
    return OpenCC("s2t")

# md_preprocess.py
@lru_cache(maxsize=1)
def _build_markdown_parser():
    return MarkdownIt("commonmark").use(dollarmath_plugin)
```

**目的**：`OpenCC` 初始化有开销（约 10-50ms），用 `lru_cache(maxsize=1)` 确保只创建一次，后续调用复用同一实例。

## 与多进程（ProcessPoolExecutor）的关系

`lru_cache` 的缓存存储在**进程内存**中。多进程场景下：

```
主进程: 缓存 OpenCC 实例 ✓
    ↓ fork
子进程 1: 独立内存，重新创建 OpenCC
子进程 2: 独立内存，重新创建 OpenCC
```

**结论**：每个子进程会各创建一次实例，但影响不大：
- 子进程数量有限（通常 4-8 个）
- 每个子进程内部的缓存仍然有效
- OpenCC 初始化开销可忽略

## 注意事项

1. **参数必须可哈希**：list、dict 不能作为参数（可用 tuple 代替）
2. **缓存占用内存**：大对象或大量参数组合需注意
3. **清除缓存**：`function.cache_clear()` 可手动清除

## 参考

- [Python 官方文档 - functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
