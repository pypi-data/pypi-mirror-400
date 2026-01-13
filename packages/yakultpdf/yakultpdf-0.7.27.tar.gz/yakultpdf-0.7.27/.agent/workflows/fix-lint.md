---
description: 自动修复 Python 代码质量问题 (Ruff lint)
---

# Python 代码质量修复流程

## 1. 运行 Ruff 检查并自动修复

```bash
uv run ruff check --fix .
```

如果有无法自动修复的错误，分析错误并手动修复。

## 2. 运行 Ruff 格式化

```bash
uv run ruff format .
```

## 3. 运行 pytest，确保没有破坏

```bash
uv run pytest -v --tb=short 2>&1 
```

## 4. 验证修复结果

// turbo
```bash
uv run ruff check .
```

确保没有剩余错误后完成。