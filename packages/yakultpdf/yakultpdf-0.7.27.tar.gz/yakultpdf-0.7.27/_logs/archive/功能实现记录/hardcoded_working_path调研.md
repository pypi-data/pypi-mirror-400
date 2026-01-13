# `_working` 硬编码路径调研

## 问题

代码中多处写死 `_working`，影响灵活性。

## 涉及文件

| 文件 | 行号 | 问题 |
|------|------|------|
| `helper_working_path.py` | 58 | `root / "_working"` 硬编码 |
| `helper_working_path.py` | 102 | 默认参数 `_working/in` |
| `helper_working_path.py` | 145-146 | 字符串比较判断默认值 |
| `mdimage_cli.py` | 39 | 回退路径 `_working/in` |
| `test_cli.py` | 多处 | 测试硬编码（可接受，如果是测试 _working，那么不要测试它！） |   

## 方案对比

| 方案 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| A | 模块常量 | 改动小 | 仍硬编码 |
| B | 完全配置化 | 最灵活 | 需改兼容逻辑 |
| **C** | 常量 + 配置优先 | 折中 | — |

## 建议

采用 **方案 B**：
不需要向后兼容

---

## 实施记录

- 移除 `_working` 默认值：`src/helper_workingpath/helper_working_path.py`
- 改用配置驱动：`src/markdown2pdf/core.py`、`src/markdown2pdf/directory.py`
- 输入目录自动补全改为配置优先：`src/helper_mdimage/mdimage_cli.py`
- 测试与文档同步更新：`src/mark2pdf/tests/test_cli.py`、`src/mark2pdf/tests/test_manager.py`、`src/helper_workingpath/README.md`、`src/helper_mdimage/README.md`
