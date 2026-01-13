# mark2pdf CLI 最终方案思考 v2

> 编写日期：2026-01-01
> 对照原文档：cli最终方案思考.md (2025-12-22)
> 核心目标：根据最新代码实现情况，更新 CLI 独立发布方案

---

## 一、已完成工作盘点

### 1.1 原规划 vs 当前实现

| 原规划项 | 当前状态 | 备注 |
|---------|----------|------|
| 命令统一（mark2pdf 子命令模式） | ✅ 已完成 | `mark2pdf` 是唯一入口 |
| `mark2pdf convert` 命令 | ✅ 已完成 | 支持 `--dir`, `--batch`, `--tc`, `--removelink` 等 |
| `mark2pdf init` / `update` | ✅ 已完成 | 在 `commands/workspace.py` |
| `mark2pdf version` | ✅ 已完成 | 在 `commands/version.py` |
| `--show-config` / `--dry-run` | ✅ 已完成 | 配置报告和执行计划展示 |
| 独立模式（无 config 运行） | ✅ 已完成 | `ConfigManager._create_standalone_config()` |
| 后处理器链 | ✅ 已完成 | `process_builder.py` |
| 配置管理器 | ✅ 已完成 | `config_loader.py` + `config.py` |
| commands 子包 | ✅ 已完成 | 7 个命令文件：clean, coverprepare, gaozhi, mdimage, version, workspace |
| 模板打包（importlib.resources） | ❌ 未完成 | 仍使用项目根目录相对路径 |
| 外部依赖检查（pandoc/typst） | ❌ 未完成 | 仅有 `check_pandoc_typst()` |
| 版本管理自动化（hatch-vcs） | ❌ 未完成 | 仍手动维护版本号 |
| PyPI 发布配置 | ❌ 未完成 | 包名仍为 `markdown2pdf` |
| Homebrew 分发 | ❌ 未完成 | 未规划 |

### 1.2 当前项目结构

```
src/
├── mark2pdf/                # CLI 入口和工作区管理
│   ├── cli.py              # 主 CLI（main, convert 命令）
│   ├── commands/           # 子命令模块
│   │   ├── clean.py
│   │   ├── coverprepare.py
│   │   ├── gaozhi.py
│   │   ├── mdimage.py
│   │   ├── version.py
│   │   └── workspace.py    # init, update
│   ├── config.py           # 配置数据类
│   ├── config_loader.py    # 配置加载逻辑
│   ├── conversion.py       # 转换执行器
│   ├── process_builder.py  # 后处理器构建
│   ├── reporter.py         # 报告输出
│   └── resources/          # 资源文件
├── markdown2pdf/           # 核心转换逻辑
│   ├── core.py             # convert_file API
│   ├── directory.py        # 目录合并
│   └── ...
├── helper_*/               # 各种辅助模块
└── postprocess/            # 后处理器
```

---

## 二、剩余核心问题重新分析

### 2.1 模板分发方案（关键设计决策）

**现状分析：**
- `helper_workingpath/resolve_template_path()` 依赖 `get_project_root()` 
- `get_project_root()` 通过查找 `pyproject.toml` 确定根目录
- 开发环境正常，但安装后无法找到模板

**核心问题：模板应该作为代码的一部分，还是作为代码之外的资源？**

#### 方案对比

| 方案 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| **A. 打包进 wheel** | 模板随代码一起发布，用 `importlib.resources` 访问 | 安装即可用；版本一致 | 模板更新需发新版；用户修改麻烦 |
| **B. 工作区必须有模板** | 每个项目自带模板 | 完全自定义；与代码解耦 | `init` 需复制模板 |
| **C. 首次运行时下载** | 从远程获取模板 | 模板可独立更新 | 需要网络；首次慢 |
| **D. 全局用户目录** | `~/.config/mark2pdf/templates/` | 一次安装全局用 | 升级时需手动更新 |

#### 当前代码已有的支持

1. `mark2pdf init` 会复制资源到工作区
2. 配置文件 `mark2pdf.config.toml` 中有 `[paths] template = "template"`
3. 模板查找会先看工作区的 `template/` 目录

**问题**：如果工作区没有 `template/`，会 fallback 到项目根目录，安装后就找不到了。


#### 多工作区场景的补充改进（结合路径处理说明）

> 参考：`_logs/archive/路径处理说明.md` 第6节

**当前代码问题**：
1. `resolve_template_path()` 回退到 `project_root/template/`，安装后无效
2. 当前代码**忽略** `config.paths.template` 配置（第97行提到的已知问题）
3. 独立模式（无 config）下无法找到模板

**改进方案：四级查找**

```
模板查找顺序（优先级从高到低）：
1. config.paths.template             # 配置指定的模板目录（尊重配置）
2. data_root/template/               # 工作区默认目录
3. ~/.config/mark2pdf/templates/      # 用户全局模板（多工作区共享）
4. 包内置模板（importlib.resources）# 最终回退（确保独立模式可用）
```

**各层职责**：
- **第1层**：用户在 config 里显式指定，可能是共享目录如 `~/my-templates`
- **第2层**：工作区本地模板，项目特定定制
- **第3层**：全局模板，多工作区共享，用户修改后全局生效
- **第4层**：保底，确保 `mark2pdf convert xxx.md` 在任意目录都能运行

**工作流程**：
1. `mark2pdf init` 默认**不**复制模板到工作区（只创建 config）
2. 首次运行时自动使用包内置模板（开箱即用）
3. `mark2pdf init --template abc`：eject 特定模板到当前工作区 `template/`（便于定制，注意，要拷贝模板的几个文本及图片，比如nb.typ , nb-lib.typ）
4. 用户如需全局模板，手动复制到 `~/.config/mark2pdf/templates/`

**与独立模式的兼容**：
- 独立模式下 `data_root = cwd`，第1、2层查找 cwd 下的模板
- 若都没有，第3层全局模板可用（用户自行维护）
- 若全局也没有，第4层包内置保底，**开箱即用**

**代码改动**：
- `resolve_template_path()`：
  - 接受 `config` 参数，尊重 `config.paths.template`
  - 增加 `~/.config/mark2pdf/templates/` 查找
  - 增加 `importlib.resources` 回退
- `mark2pdf init`：增加 `--with-templates` 选项
- 可选：`mark2pdf templates` 子命令（list/update/reset）

#### 模板打包方案

**选择**：使用 hatch 的 `forced-include` 直接打包项目根目录的 `template/`

**pyproject.toml 修改**：
```toml
[tool.hatch.build.targets.wheel]
packages = [
    "src/markdown2pdf",
    "src/mark2pdf",
    # ... 其他包
]

[tool.hatch.build.targets.wheel.force-include]
"template" = "mark2pdf/templates"  # 打包到 mark2pdf/templates/
```

**代码访问方式**：
```python
from importlib.resources import files

def get_bundled_template(name: str) -> Path:
    """获取包内置模板路径"""
    return files("mark2pdf.templates").joinpath(name)
```

**优势**：
- ✅ 模板保留在项目根目录，便于开发时直接使用
- ✅ 打包时自动纳入 wheel，安装后可用
- ✅ 不改变现有目录结构

### 2.2 包名统一

**决定：直接改名为 `mark2pdf`**


### 2.3 外部依赖检查

**现状：**
- `helper_typst/check_pandoc_typst()` 仅做存在性检查
- 缺少版本检查、自动安装引导

**改进空间（低优先级）：**
- 添加版本检查
- 提示 `brew install pandoc typst`

### 2.4 版本管理

**现状：**
- `pyproject.toml` 中硬编码 `version = "0.5.29"`
- 无 Git tag 自动化

**建议（低优先级）：**
- 暂时维持手动管理
- 发布前统一更新版本号

---

## 三、真正需要解决的问题

### 3.1 优先级排序

| 优先级 | 问题 | 阻塞程度 | 工作量 |
|--------|------|----------|--------|
| P0 | 模板打包（importlib.resources） | 阻塞发布 | 中 |
| P1 | pyproject.toml 完善（分类、关键词等） | 影响发现性 | 小 |
| P2 | README 更新（安装说明） | 影响用户体验 | 小 |
| P3 | 版本自动化（hatch-vcs） | 不阻塞 | 小 |
| P4 | Homebrew 发布 | 可选 | 中 |

### 3.2 P0 任务分解：模板打包

1. **目录结构调整**
   ```
   src/markdown2pdf/
   ├── templates/          # 新建
   │   ├── nb.typ
   │   ├── nb-lib.typ
   │   ├── gaozhi.typ
   │   ├── gaozhi-lib.typ
   │   └── ...
   ```

2. **pyproject.toml 更新**
   ```toml
   [tool.hatch.build.targets.wheel]
   include = [
       "src/markdown2pdf/templates/**/*.typ",
   ]
   ```

3. **代码修改**
   - `helper_workingpath/helper_working_path.py`：添加 `get_bundled_template()` 函数
   - `resolve_template_path()`：优先查找工作区模板，fallback 到包内置

4. **测试验证**
   - 开发模式：`uv run mark2pdf convert` 正常
   - 安装模式：`pip install dist/*.whl && mark2pdf convert` 正常

---

## 四、对原文档"build 命令"的重新思考

原文档规划了 `mark2pdf build` 作为"一键构建"命令，与 `convert` 分开：

```
mark2pdf build           # 构建当前工作区（等同于旧 createpdf.py 无参运行）
mark2pdf convert <file>  # 转换单文件
```

**当前实现：**
- 只有 `mark2pdf convert`，默认 `filename=index.md`
- `mark2pdf convert` 实际上已经覆盖了 `build` 的场景

**重新评估：**
- 是否需要 `build`？
  - Pro: 语义更清晰（build = 工作区整体构建）
  - Con: 增加命令复杂度，`convert` 已足够

**建议：暂不添加 `build`**
- `mark2pdf convert`（无参数）= 构建 `in/index.md`
- 如果需要批量，用 `mark2pdf convert --batch .`
- 用户反馈后再决定是否添加 `build` 别名

---

## 五、下一步行动建议

### 5.1 短期（准备发布）

1. ✅ **检查现有测试覆盖**：确保 260+ 测试通过
2. 🔲 **模板打包**：实现 P0 任务
3. 🔲 **pyproject.toml 完善**：添加分类、关键词、URLs
4. 🔲 **README 更新**：安装说明、快速入门
5. 🔲 **测试发布到 TestPyPI**

### 5.2 中期（发布后）

1. 🔲 收集用户反馈
2. 🔲 版本自动化（hatch-vcs）
3. 🔲 Shell 补全

### 5.3 长期（扩展）

1. 🔲 Homebrew tap
2. 🔲 考虑 `mark2pdf` 作为 PyPI 包名

---

## 六、总结

与 2025-12-22 的原规划相比：
- **已完成**：命令统一、子命令架构、配置管理、独立模式、后处理器链
- **核心遗留**：模板打包问题（阻塞发布）
- **可延后**：版本自动化、Homebrew

当前代码架构已相当成熟，专注解决**模板打包**即可准备发布。
