# 批量并发方案：--jobs 参数

## 目标

为 `mark2pdf convert --batch` 增加 `--jobs` 参数，用 ProcessPoolExecutor 并发处理多个文件。

## 现状

`run_batch_conversion()` 仅支持串行循环（conversion.py），调用 `convert_file()`。

## 设计

### 为什么用 ProcessPoolExecutor

- 每个文件独立，无共享状态
- 多进程可并行预处理（正则、MarkdownIt）和外部进程（pandoc/typst）
- 默认 `--jobs 1` 保守安全

### 实现要点

**CLI**（cli.py convert 命令）：
```python
@click.option("--jobs", "-j", default=1, type=click.IntRange(1, None), help="并发数（仅批量模式有效）")
```

**核心逻辑**（conversion.py）：
```python
def run_batch_conversion(..., jobs: int = 1):
    # 准备阶段不变
    
    if jobs == 1:
        for md_file in sorted(md_files):
            # 原有串行逻辑
    else:
        with ProcessPoolExecutor(max_workers=min(jobs, len(md_files))) as executor:
            futures = {executor.submit(_convert_batch_file, args): f for f in md_files}
            for future in as_completed(futures):
                # 收集结果
```

### 需处理的问题

| 问题 | 解决 |
|------|------|
| 序列化 | config/frontmatter 可直接 pickling；批量模式沿用现状不启用 postprocess |
| 工作目录 | 每个子进程独立沙箱（tempfile 自动隔离） |
| 输出 | jobs>1 打印并发数，失败文件单独输出，最后统一汇总 |
| 错误 | 一个失败不影响其他，最后汇总 |

## 性能预估（M1 MacBook，jobs=4）

| 场景 | 串行 → 并发 | 加速 |
|------|------------|------|
| 10 个小文件 | 30s → 10s | ~3x |
| 10 个中文件 | 60s → 20s | ~3x |

推荐 `--jobs 4`，`jobs>8` 收益递减。

## 涉及文件

| 文件 | 修改 |
|------|------|
| cli.py | 增加 `--jobs` 参数，并传递给批量转换 |
| conversion.py | `run_batch_conversion` 增加 jobs 逻辑与并行 worker |
| config/reporter.py | dry-run 输出并发信息 |
