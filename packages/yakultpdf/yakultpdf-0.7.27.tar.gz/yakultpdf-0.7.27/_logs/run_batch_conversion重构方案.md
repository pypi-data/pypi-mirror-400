# run_batch_conversion 重构方案

## 现状分析

- **行数**：204 行（第235-439行）
- **职责过多**：参数准备、配置加载、frontmatter合并、文件发现、单/多线程调度、结果汇总
- **重复代码**：单线程和多线程路径中都有 frontmatter 合并和 options 构建逻辑
- **复杂的 postprocess 处理**：tc 标志需要追加到 processor_names，并发模式不支持自定义函数

## 函数拆分设计

### 0. 后处理器准备（新增）

```
_prepare_postprocessors(postprocess, processor_names, tc, jobs) 
    -> tuple[list[str] | None, Callable | None, int]
```
- 职责：处理 postprocess 函数 vs processor_names 的优先级
- 逻辑：
  - 若 processor_names 存在且 tc=True，追加 "to_traditional_chinese"
  - 若 jobs>1 且使用自定义 postprocess 函数，降级为 jobs=1
  - 若 jobs>1 且 tc=True 但无 processor_names，创建 ["to_traditional_chinese"]
- 返回：(最终 processor_names, 最终 postprocess 函数, 最终 jobs)
- 预计：~20 行

### 1. 配置准备阶段

```
_prepare_batch_config(directory, workspace_dir, config) -> BatchConfig
```
- 职责：加载配置、合并 frontmatter、确定输入输出目录
- 返回：包含所有配置信息的 dataclass
- 预计：~45 行

### 2. 文件发现阶段

```
_discover_batch_files(input_dir: Path) -> list[Path]
```
- 职责：获取并排序待处理文件列表
- 排除：index.md
- 预计：~15 行

### 3. 单文件处理（已存在）

```
_convert_batch_file(...) -> tuple[str, bool, str | None]
```
- 现有函数，保持不变
- 已拆分至第19-75行

### 4. 单线程执行

```
_run_sequential(files, batch_config, postprocess_fn) -> tuple[int, int]
```
- 职责：顺序执行所有文件转换
- 返回：(成功数, 失败数)
- 预计：~35 行

### 5. 多线程执行

```
_run_parallel(files, batch_config, jobs, processor_names) -> tuple[int, int]
```
- 职责：并发执行所有文件转换
- 返回：(成功数, 失败数)
- 预计：~45 行

### 6. 主函数（重构后）

```
run_batch_conversion(...) -> bool
```
- 职责：协调各阶段，打印进度，返回结果
- 调用顺序：准备 → 发现 → 执行 → 汇报
- 预计：~50 行

## BatchConfig 数据结构

```python
@dataclass
class BatchConfig:
    config: object               # 工作区配置
    input_dir: Path              # 输入目录
    output_subdir: Path          # 输出目录（用于打印）
    file_indir: str              # convert_file 用的 indir
    file_outdir: str             # convert_file 用的 outdir
    default_frontmatter: dict | None  # 默认 frontmatter
    options_base_fm: dict        # 用于模板解析的合并 frontmatter
    template: str | None         # CLI 模板
    config_template: str | None  # 配置文件默认模板
    verbose: bool
    overwrite: bool              # 已合并 CLI > config
    tc: bool
    force_filename: bool
```

**注意**：`open_file` 参数在批量模式下不支持，无需传递。

## 测试策略

### 先加测试

1. **单元测试**：各辅助函数独立测试
   - `_prepare_batch_config`：验证 frontmatter 合并逻辑
   - `_discover_batch_files`：验证文件过滤和排序
   
2. **集成测试**：批量转换端到端
   - 单线程模式
   - 多线程模式（jobs=2）
   - 空目录处理
   - 参数组合：tc、template、overwrite

### 测试文件位置

```
tests/test_batch_conversion.py
```

## 重构步骤

1. [ ] 编写测试用例，确保现有行为被覆盖
2. [ ] 创建 `BatchConfig` dataclass
3. [ ] 提取 `_prepare_postprocessors` 函数
4. [ ] 提取 `_prepare_batch_config` 函数
5. [ ] 提取 `_discover_batch_files` 函数
6. [ ] 提取 `_run_sequential` 函数
7. [ ] 提取 `_run_parallel` 函数
8. [ ] 重构 `run_batch_conversion` 主函数
9. [ ] 运行测试验证

## 风险点

- **进程间通信**：多线程模式下 `BatchConfig` 需要可序列化
- **postprocess 处理**：单线程用函数，多线程用名称列表，需保持一致
- **打印输出**：保持用户可见的进度输出不变
