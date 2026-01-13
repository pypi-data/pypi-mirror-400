# ProcessBuilder 重构文档

## 1. 背景与问题

之前的 `process_builder.py` 存在以下问题：
- **职责不清**：混合了 CLI 参数解析、日志输出和逻辑构建。
- **副作用**：函数内部直接调用 `click.echo`，导致无法在非 CLI 环境（如 Web 服务或测试）中复用。
- **扩展性差**：难以获取构建过程中的详细状态（如哪些处理器缺失）。

## 2. 重构目标

- **彻底解耦**：移除所有 `click` 依赖，使其成为纯 Python 逻辑模块。
- **信息丰富**：返回结构化的结果对象，而非简单的 Callable。
- **职责归位**：参数解析移回 `cli.py`。

## 3. 核心设计

引入 `PostprocessBuildResult` 数据类作为构建结果：

```python
# 伪代码结构
class PostprocessBuildResult:
    chain: Callable | None  # 最终的处理函数链
    loaded: list[str]       # 成功加载的处理器
    missing: list[str]      # 未找到的处理器
```

## 4. 实现细节

### Process Builder (Logic)

`build_postprocessor_chain` 现在的逻辑：
1. 接收纯字符串列表 `names`。
2. 尝试加载每个处理器。
3. 收集 `loaded` 和 `missing` 列表。
4. 组装函数链 `chain`。
5. 返回 `PostprocessBuildResult`。
6. **不做任何输出**。

### CLI (Presentation)

CLI (`cli.py`) 负责交互：
1. 解析 flags 获取 names 列表。
2. 调用 `build_postprocessor_chain`。
3. 根据返回的 `result` 对象：
    - 打印 `missing` 警告。
    - 打印 `loaded` 信息（如果 verbose）。
    - 使用 `result.chain` 执行后续操作。

## 5. 收益

- **可测试性**：可以轻松编写单元测试验证构建逻辑，无需 mock stdout。
- **灵活性**：调用方完全控制如何处理缺失的处理器（报错、忽略或日志）。
- **清晰性**：数据流向变得单向且明确。
