# mark2pdf CLI 统一方案 - 全面整合分析

日期：2024-12-31
**实施状态更新**: 2024-12-31

---

## 一、现状分析

### 1.1 当前架构

> ✅ **已变更**: `config_manager` 已重命名为 `mark2pdf`

```
┌─────────────────────────────────────────────────────────────────────┐
│                          pyproject.toml                             │
│  md2pdf = "markdown2pdf.cli:cli"     ← ✅ 已移除                     │
│  mark2pdf = "mark2pdf.cli:main"         ← ✅ 已更新                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
       ┌──────────────────────┴──────────────────────┐
       │                                              │
       ▼                                              ▼
┌──────────────────────┐                    ┌──────────────────────┐
│  markdown2pdf/       │                    │  mark2pdf/            │
│  (核心转换)          │                    │  (CLI + 工作区管理) │
│  - core.py           │                    │  - cli.py            │
│  - directory.py      │                    │  - conversion.py     │
└──────────────────────┘                    └──────────────────────┘
```

### 1.2 两个 CLI 功能对比

| 功能 | `md2pdf` | `mark2pdf` | 状态 |
|------|----------|-----------|------|
| 转换单文件 | ✅ | ✅ | ✅ 已实现 |
| 目录合并转换 | ✅ | ✅ | ✅ 已实现 |
| 工作区初始化 | ❌ | ✅ | ✅ 已有 |
| 工作区更新 | ❌ | ✅ | ✅ 已有 |
| 图片清理 | ❌ | ✅ | ✅ 已有 |
| 配置文件读取 | ❌ | ✅ | ✅ 已实现 |

### 1.3 createpdf.py 的角色

> ✅ **已更新**: import 已从 `config_manager` 改为 `mark2pdf`

---

## 二、目标架构

### 2.1 统一入口

> ✅ **已实现**

```
mark2pdf (唯一 CLI)
├── convert <file>            # ✅ 已实现
│   ├── --dir <目录>          # ✅ 已实现
│   ├── --batch <目录>        # ✅ 已实现
│   ├── --postprocess <name>  # ✅ 参数已预留（功能待实现）
│   └── 其他选项...           # ✅ 已实现
├── init <目录>               # ✅ 已有
├── update [目录]             # ✅ 已有
├── version                   # ✅ 已新增
└── imageclearing <file>      # ✅ 已有
```

### 2.2 createpdf.py 新定位

> ✅ **已实现**

---

## 三、postprocess 插件机制（预留）

### 3.1 当前实现范围

| 项目 | 状态 | 实施状态 |
|------|------|----------|
| `--postprocess <name>` CLI 参数 | ✅ 预留 | ✅ 已实现 |
| 插件加载器 | ❌ 暂不实现 | ✅ 基础框架已建立 |
| 工作区插件查找 | ❌ 暂不实现 | ⏳ 待实现 |
| 预定义插件库 | ❌ 暂不实现（仅 `abc-postprocess`）| ✅ abc_postprocess 已创建 |

### 3.2 smoke test 用空处理器

> ✅ **已实现**: `src/markdown2pdf/postprocessors/abc_postprocess.py`

### 3.3 后续完整实现（规划）

待需要时再实现：

- **按名称查找** - 工作区 > 预定义 ⏳
- **动态加载** - importlib 加载 .py 文件 ⏳
- **预定义处理器** - tc_convert、remove_links 等 ⏳


---

## 四、工作区自动检测

### 4.1 当前问题

> ✅ **已解决**

### 4.2 解决方案

> ✅ **已实现**: `detect_workspace()` 函数在 `mark2pdf/cli.py`

---

## 五、实现计划

### 5.1 文件变更

#### 修改

| 文件 | 变更 | 状态 |
|------|------|------|
| `pyproject.toml` | 移除 `md2pdf` 入口 | ✅ 已完成 |
| `mark2pdf/cli.py` | 添加 `convert` 子命令 | ✅ 已完成 |
| `mark2pdf/conversion.py` | 支持 postprocess 名称参数 | ⏳ 待实现（当前仅函数参数） |
| `mark2pdf/resources/createpdf.py` | 精简，仅保留自定义逻辑用途 | ✅ 已完成 |

#### 新增

| 文件 | 用途 | 状态 |
|------|------|------|
| `markdown2pdf/postprocessors/__init__.py` | 插件加载器 | ✅ 已创建 |
| `markdown2pdf/postprocessors/tc_convert.py` | 预定义：繁体转换 | ⏳ 待实现 |
| `markdown2pdf/postprocessors/remove_links.py` | 预定义：移除链接 | ⏳ 待实现 |

#### 可选移除

| 文件 | 说明 | 状态 |
|------|------|------|
| `markdown2pdf/cli.py` | 保留备用 | ✅ 保留（但入口已移除）|
| `markdown2pdf/defaults.py` | 合并到 mark2pdf | ✅ 保留（被 mark2pdf 调用）|

### 5.2 内置后处理器清单

| 处理器名称 | 对应的 CLI 参数 | 状态 |
|------------|----------------|------|
| `tc_convert` | `--tc` | ⏳ 待迁移为插件（当前内联实现）|
| `remove_links` | `--removelink` | ⏳ 待迁移为插件（当前内联实现）|

### 5.3 新 CLI 结构

> ✅ **已实现**（但 `--removelink` 参数声明后未传递给底层函数）

### 5.4 createpdf.py 精简版

> ✅ **已实现**

---

## 六、使用场景对照

> ✅ **全部已实现**

| 场景 | 新方式 | 状态 |
|------|--------|------|
| 普通转换 | `mark2pdf convert sample.md` | ✅ |
| 指定模板 | `mark2pdf convert -t custom.typ` | ✅ |
| 繁体转换 | `mark2pdf convert --tc` | ✅ |
| 使用后处理 | `mark2pdf convert -p xxx` | ⏳ 参数预留，功能待实现 |
| 初始化工作区 | `mark2pdf init .` | ✅ |

---

## 七、功能增强建议

### 7.1 新增命令

- `mark2pdf version`: ✅ **已实现**

### 7.2 `convert` 命令增强

| 选项 | 状态 |
|------|------|
| `--dry-run` | ✅ 已实现 |
| `--show-config` | ✅ 已实现 |
| `--verbose` | ✅ 已实现（也会打印配置）|

### 7.3 关键设计决策

1. **createpdf.py 参数支持**: ✅ 已使用 `click` 接管
2. **`postprocess` 传参**: ✅ 按计划暂不支持
3. **工作区递归检测**: ✅ 按计划暂不支持

### 7.4 技术规范与安全性修正

1. **包名策略**: ⚠️ 偏离计划
   - 计划：保持 `config_manager`
   - 实际：已重命名为 `mark2pdf`（用户要求）

2. **模板文件加载策略**: ✅ 保持现状

3. **依赖安装安全**: ⏳ 待审查

### 7.5 配置打印逻辑与时机

> ✅ **已实现**: 按计划顺序执行

---

## 八、总结

| 变更项 | 说明 | 状态 |
|--------|------|------|
| **移除 `md2pdf`** | 统一使用 `mark2pdf` | ✅ |
| **新增 `mark2pdf convert`** | 主转换命令 | ✅ |
| **postprocess 插件化** | 预定义 + 工作区自定义 | ⏳ 框架已建，待完善 |
| **工作区自动检测** | 在工作区目录直接运行 | ✅ |
| **精简 `createpdf.py`** | 仅保留复杂自定义场景 | ✅ |
| **调试增强** | `show-config`, `dry-run` | ✅ |

### 待办事项

1. ⏳ `--removelink` 参数传递给底层函数
2. ⏳ `tc_convert` 插件独立实现
3. ⏳ `remove_links` 插件独立实现
4. ⏳ 插件动态加载机制完善
