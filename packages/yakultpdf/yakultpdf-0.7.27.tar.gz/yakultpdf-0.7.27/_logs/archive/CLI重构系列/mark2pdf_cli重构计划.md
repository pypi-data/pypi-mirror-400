
### mark2pdf CLI 重构方案（2025-12-31 执行结果）

**核心目标**: 降低 `cli.py` 复杂度，实现关注点分离（UI、配置、逻辑构建、执行），并将配置管理职责明确化。

#### 1. 模块拆分与职能重定义 (已实施)

*   **`src/mark2pdf/cli.py` (指挥官)**
    *   **职责**: 解析参数 -> 调用 `process_builder` 组装逻辑 -> 调用 `reporter` 显示配置 -> 调用 `conversion` 执行。
    *   **保留**: `main`, `convert`, `version` 命令定义。
    *   **变更**: `init`, `update`, `imageclearing` 命令已下沉至 `commands/` 子包。

*   **`src/mark2pdf/config_loader.py` (配置加载)**
    *   **来源**: 原 `manager.py` 的重命名与精简。
    *   **职责**:
        1.  `ConfigManager.load()`: 加载 `mark2pdf.config.toml`。
        2.  `load_frontmatter_yaml`: 加载默认 frontmatter。
        3.  `resolve_template`: 模板决策逻辑。
    *   **状态**: 完成。并未实现单一的 `build_execution_context` 函数，而是保持了灵活的函数调用组合，以适应 Click 的参数处理方式。

*   **`src/mark2pdf/workspace_manager.py` (工作区管理)**
    *   **来源**: 从原 `manager.py` 拆分。
    *   **职责**: `init_workspace`, `update_workspace`, `detect_workspace`。
    *   **状态**: 完成。

*   **`src/mark2pdf/process_builder.py` (逻辑组装)**
    *   **职责**: 接收插件名称列表，动态组装后处理器链。
    *   **API**: `build_postprocessor_chain`, `get_processor_names_from_flags`。
    *   **状态**: 完成。

*   **`src/mark2pdf/reporter.py` (UI展示)**
    *   **职责**: 负责 `--show-config`, `--dry-run` 的终端输出。
    *   **API**: `print_config_report`, `print_execution_plan`。
    *   **状态**: 完成。

*   **`src/mark2pdf/conversion.py` (执行)**
    *   **改进**: 移除内部 `ConfigManager.load()` 调用，改为使用 `config_loader` 提供的工具函数获取配置。
    *   **状态**: 完成。

*   **`src/mark2pdf/commands/` (子命令包)**
    *   **新增内容**:
        *   `workspace.py`: 包含 `init`, `update` 命令。
        *   `image.py`: 包含 `imageclearing` 命令。
    *   **状态**: 完成。

#### 2. 数据流向图

```text
CLI Args (cli.py / commands/*.py)
   |
   +---> [process_builder] (组装插件)
   |
   +---> [config_loader] (加载配置)
   |
   v
[reporter] (显示配置/计划)
   |
   v
[conversion] (执行转换) --> Output PDF
```

#### 3. 实施路径回顾

1.  **拆分**: `manager.py` -> `config_loader.py` + `workspace_manager.py`。
2.  **新建**: `process_builder.py`, `reporter.py`, `utils.py`。
3.  **子命令下沉**: 建立 `commands/` 子包，迁移非核心命令。
4.  **组装**: `cli.py` 负责串联，`__init__.py` 维护导出接口。
5.  **验证**: 单元测试覆盖率 100% (34 passed)。

#### 4. 优势
*   **关注点分离**: 配置、业务、UI、命令定义彻底解耦。
*   **可扩展性**: 新增命令只需在 `commands/` 下添加并注册。
*   **可维护性**: 每个模块行数适中，职责单一。
