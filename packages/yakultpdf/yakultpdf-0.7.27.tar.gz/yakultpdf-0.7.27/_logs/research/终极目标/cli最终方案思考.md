# mark2pdf CLI 独立发布方案 - 全面思考

> 编写日期：2025-12-22
> 文档性质：技术规划文档
> 核心目标：将 mark2pdf 打造为可独立发布的命令行工具
> 目标平台：**macOS**

---

## 一、现状分析

### 1.1 当前架构优势

| 维度 | 现状 | 评价 |
|------|------|------|
| 构建系统 | hatchling + pyproject.toml | ✅ 符合现代规范 |
| CLI 框架 | Click | ✅ 成熟稳定 |
| 入口点 | `mark2pdf`、`md2pdf` 两个命令 | ✅ 已配置 |
| 测试覆盖 | 260+ 测试用例 | ✅ 良好 |
| 模块化 | 8 个独立模块 | ✅ 合理拆分 |

### 1.2 当前阻碍发布的问题

1. **外部依赖未声明**：Pandoc 和 Typst 是必需的系统级依赖，但未在任何地方明确声明和检查
2. **模板打包问题**：`template/` 目录未纳入包分发，安装后无法找到
3. **路径硬编码残留**：部分代码仍依赖开发环境的相对路径
4. **命令统一性**：两个命令入口分工不够清晰
5. **用户文档缺失**：缺少面向终端用户的安装和使用文档
6. **版本管理粗放**：版本号更新需手动同步

---

## 二、目标愿景（以终为始）

### 2.1 用户安装体验

最终目标是让用户能通过以下任一方式安装：

```bash
# 方式1: uv (推荐，替代 pipx)
uv tool install mark2pdf

# 方式2: pipx (经典)
pipx install mark2pdf

# 方式3: pip
pip install mark2pdf

# 方式4: Homebrew (macOS 用户)
brew install fangjun/tap/mark2pdf
```

### 2.2 用户视角：安装到了哪里？（macOS）

用户最关心的是："我装完之后，怎么用？文件在哪？"

#### A. 命令入口
安装后，用户在终端拥有 **一个核心命令**：`mark2pdf`。
（为了兼容性，也会同时存在 `md2pdf`，但文档中只宣传 `mark2pdf`）

#### B. 安装路径揭秘

| 安装方式 | 可执行文件位置 (软链) | 真实物理位置 | 优势 |
| :--- | :--- | :--- | :--- |
| **uv** (New & Hot) | `~/.local/bin/mark2pdf` | `~/.local/share/uv/tools/mark2pdf/` | **极速**，现代化的 pipx 替代品 |
| **pipx** | `~/.local/bin/mark2pdf` | `~/.local/pipx/venvs/mark2pdf/` | **环境隔离**，经典稳定 |
| **Homebrew** | `/opt/homebrew/bin/mark2pdf` | `/opt/homebrew/Cellar/mark2pdf/.../` | **系统级**，统一管理 |
| **pip** (User) | `~/Library/Python/3.x/bin...` | `~/Library/Python/3.x/site-packages/...` | 容易冲突（**不推荐**） |

**总结**：
无论哪种方式，用户都不需要关心具体路径，只需要知道终端里能直接敲 `mark2pdf` 即可。

### 2.3 工作流演进：告别 createpdf.py

**用户疑问**："现在目录里有一个 `createpdf.py`，以后我是不是直接敲命令就行了？"

**答案：是的！**

| 模式 | 操作方式 | 优点 | 缺点 |
| :--- | :--- | :--- | :--- |
| **现状 (脚本模式)** | `./createpdf.py` | 逻辑透明，方便魔改 | 升级麻烦（需重新复制脚本），目录杂乱 |
| **未来 (CLI 模式)** | `mark2pdf build` | **极简**，升级工具即升级功能 | 个性化修改稍难（需改 config） |

**演进计划**：
1.  **过渡期**：`mark2pdf init` 仍保留复制脚本的可选参数，但默认推荐 CLI 模式。
2.  **终态**：工作区仅保留 `mark2pdf.config.toml` 和 `in/` 目录，完全去脚本化。

### 2.4 用户使用体验

```bash
# 初始化工作区
mark2pdf init my-project

# 转换单个文件
mark2pdf convert article.md

# 转换目录
mark2pdf convert --dir ./docs

# 查看帮助
mark2pdf --help
```

### 2.3 开发者维护体验

```bash
# 发布新版本（自动化）
git tag v0.5.0 && git push --tags
# CI 自动构建并发布到 PyPI
```

---

## 三、改进路线图

### Phase 1: 代码层准备（1-2 次迭代）

#### 3.1.1 模板打包（关键）

**问题**：当前 `template/` 目录不在包内，安装后找不到模板。

**方案**：使用 `importlib.resources` 访问包内资源。

```python
# src/helper_workingpath/helper_working_path.py（改进后）
import importlib.resources

def get_bundled_template_dir() -> Path:
    """获取包内置模板目录"""
    with importlib.resources.files("markdown2pdf") / "templates" as p:
        return Path(p)
```

**pyproject.toml 改动**：

```toml
[tool.hatch.build.targets.wheel]
packages = [
    "src/markdown2pdf",
    # ... 其他模块
]
# 包含模板文件
include = [
    "src/markdown2pdf/templates/**/*.typ",
    "src/config_manager/resources/**/*",
]
```

**目录结构调整**：
```
src/
├── markdown2pdf/
│   ├── templates/          # 将 template/ 移入包内
│   │   ├── nb.typ
│   │   ├── nb-lib.typ
│   │   └── ...
```

#### 3.1.2 外部依赖检查增强

**问题**：用户安装后运行，若缺少 Pandoc/Typst 只会报错，不友好。

**方案**：启动时检查，若缺失则询问用户是否自动安装（通过 Homebrew）。

```python
# src/markdown2pdf/deps.py（新建）
import shutil
import sys
import subprocess

EXTERNAL_DEPS = {
    "pandoc": {
        "install_cmd": "brew install pandoc",
        "min_version": "3.0",
    },
    "typst": {
        "install_cmd": "brew install typst",
        "min_version": "0.11",
    },
}

def install_dep(dep: str, install_cmd: str) -> bool:
    """尝试自动安装依赖"""
    print(f"\n⚡️ 正在安装 {dep}...")
    try:
        subprocess.check_call(install_cmd, shell=True)
        print(f"✅ {dep} 安装成功！")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ 安装失败，请手动运行: {install_cmd}")
        return False

def check_external_deps(fail_fast: bool = True) -> list[str]:
    """检查外部依赖，缺失时询问是否安装"""
    missing = []
    for dep, info in EXTERNAL_DEPS.items():
        if not shutil.which(dep):
            print(f"⚠️  未检测到 {dep} ({info['min_version']}+)")
            
            # 询问用户
            choice = input(f"❓ 是否尝试自动安装? (使用 Homebrew) [Y/n] ").strip().lower()
            if choice in ("", "y", "yes"):
                if install_dep(dep, info['install_cmd']):
                    continue # 安装成功，继续检查下一个
            
            # 如果没自动安装或安装失败，记录缺失
            missing.append(dep)
            print(f"❌ 请手动安装: {info['install_cmd']}")

    if missing and fail_fast:
        sys.exit(1)
    return missing
```

#### 3.1.3 命令统一

**问题**：`mark2pdf` 和 `md2pdf` 两个命令职责重叠。

**方案**：统一为 `mark2pdf` 子命令模式。

```bash
mark2pdf init [dir]      # 初始化工作区 (默认生成 config，不生成脚本)
mark2pdf build           # 构建当前工作区 (核心命令，替代 createpdf.py)
mark2pdf convert <file>  # 转换单文件 (Ad-hoc 模式)
mark2pdf update          # 更新 (仅在脚本模式下有效)
mark2pdf version         # 显示版本和依赖信息
```

**命令分工**：

| 命令 | 对应原脚本用法 | 场景 | 特点 |
| :--- | :--- | :--- | :--- |
| `build` | `./createpdf.py` (无参) | **日常构建** | 读取配置与默认入口，**全自动** |
| `convert` | `./createpdf.py xxx.md` | **临时转换** | 指定文件，手动指定参数 |

**为什么需要 `build`？**
因为它通过 `mark2pdf.config.toml` 固化了项目配置（如默认模板、输出目录），用户无需每次输入一长串参数，相当于“一键执行”。

---

### Phase 2: 打包与分发（1 次迭代）

#### 3.2.1 PyPI 发布准备

**pyproject.toml 完善**：

```toml
[project]
name = "mark2pdf"  # 建议改用统一名称
version = "0.5.0"
description = "Markdown to PDF converter using Pandoc and Typst"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Your Name", email = "email@example.com"}]
keywords = ["markdown", "pdf", "typst", "pandoc", "cli"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Text Processing :: Markup :: Markdown",
]

[project.urls]
Homepage = "https://github.com/yourname/mark2pdf"
Documentation = "https://github.com/yourname/mark2pdf#readme"
Repository = "https://github.com/yourname/mark2pdf.git"
Issues = "https://github.com/yourname/mark2pdf/issues"

[project.scripts]
mark2pdf = "config_manager.cli:main"
md2pdf = "markdown2pdf.cli:cli"  # 保留兼容性
```

#### 3.2.2 版本管理自动化

**方案**：使用 `hatch-vcs` 或 `setuptools-scm` 基于 Git tag 自动生成版本号。

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/markdown2pdf/_version.py"
```

#### 3.2.3 CI/CD 流程（GitHub Actions）

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  push:
    tags: ['v*']

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

---

### Phase 3: 增强体验（后续迭代）

#### 3.3.1 Homebrew 分发

**创建 Homebrew Tap**：

1. 创建 GitHub 仓库：`homebrew-mark2pdf`
2. 添加公式：`Formula/mark2pdf.rb`

```ruby
class Mark2pdf < Formula
  include Language::Python::Virtualenv

  desc "Markdown to PDF converter using Pandoc and Typst"
  homepage "https://github.com/yourname/mark2pdf"
  url "https://files.pythonhosted.org/packages/.../mark2pdf-0.5.0.tar.gz"
  sha256 "..."

  depends_on "python@3.12"
  depends_on "pandoc"
  depends_on "typst"

  resource "click" do
    url "https://files.pythonhosted.org/packages/.../click-8.1.7.tar.gz"
    sha256 "..."
  end

  # ... 其他 Python 依赖的 resource 声明

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/mark2pdf", "--version"
  end
end
```

**用户安装**：
```bash
brew tap yourname/mark2pdf
brew install mark2pdf
```

#### 3.3.2 Shell 自动补全

```python
# src/config_manager/cli.py
import click

@click.group()
def main():
    """mark2pdf - Markdown 转 PDF 工具集"""
    pass

# 生成补全脚本
# mark2pdf --install-completion bash
# mark2pdf --install-completion zsh
```

#### 3.3.3 配置文件支持（XDG 规范）

```python
# 全局配置位置
~/.config/mark2pdf/config.toml

# 项目配置（已有）
./mark2pdf.config.toml

# 优先级：项目 > 用户全局 > 系统默认
```

---

## 四、关键技术决策

### 4.1 包名统一

| 选项 | 优点 | 缺点 |
|------|------|------|
| `mark2pdf` | 简洁，与命令一致 | 需改现有包名 |
| `markdown2pdf` | 保持现状 | 与命令名不一致 |

**建议**：采用 `mark2pdf`，更具品牌识别度。

### 4.2 模板分发策略

| 策略 | 说明 |
|------|------|
| 打包进 wheel | 推荐，安装即可用 |
| 首次运行下载 | 增加首次启动时间 |
| 独立资源包 | 管理复杂 |

**建议**：模板随包分发，用户可通过工作区机制覆盖。

### 4.3 外部依赖处理

| 策略 | 说明 |
|------|------|
| 仅文档说明 | 简单，但用户体验差 |
| 运行时检查 | 仅仅提示，不够友好 |
| **交互式安装** | **推荐**，询问后自动调 brew 安装 |

**建议**：运行时检查 + **询问安装** + 自动调用 Homebrew。

---

## 五、验证清单

### 5.1 自动化测试

- [ ] 所有现有测试通过 (`uv run pytest`)
- [ ] 模板加载测试（打包后路径正确）
- [ ] 外部依赖检查测试
- [ ] CLI 子命令测试

### 5.2 手动验证

1. **全新安装测试**：
   ```bash
   # 创建干净虚拟环境
   python -m venv /tmp/test-mark2pdf
   source /tmp/test-mark2pdf/bin/activate
   pip install dist/mark2pdf-*.whl

   # 验证命令可用
   mark2pdf --help
   mark2pdf init /tmp/test-workspace
   cd /tmp/test-workspace
   
   # 测试 1: 构建整个工作区
   mark2pdf build

   # 测试 2: 转换单文件
   mark2pdf convert in/index.md
   ```

2. **pipx 安装测试**：
   ```bash
   pipx install dist/mark2pdf-*.whl
   mark2pdf --version
   ```

---

## 六、迭代计划建议

| 阶段 | 内容 | 优先级 |
|------|------|--------|
| v0.5.0 | 模板打包、依赖检查、命令统一 | 高 |
| v0.6.0 | PyPI 发布、CI/CD | 高 |
| v0.7.0 | 文档完善、错误信息国际化 | 中 |
| v1.0.0 | Homebrew、Shell 补全、稳定 API | 中 |

---

## 七、参考资料

1. [Python 打包用户指南](https://packaging.python.org/)
2. [Hatchling 文档](https://hatch.pypa.io/)
3. [Click 文档](https://click.palletsprojects.com/)
4. [Homebrew Python 公式指南](https://docs.brew.sh/Python-for-Formula-Authors)
5. [pipx 最佳实践](https://pypa.github.io/pipx/)

---

## 八、总结

将 mark2pdf 打造为可独立发布的 CLI 工具，核心挑战在于：
1. **模板资源的正确打包与访问**
2. **外部依赖（Pandoc/Typst）的优雅处理**
3. **用户安装体验的持续优化**

通过上述规划，可以在 3-4 次迭代后实现目标。关键是每一步都要写好测试、写好文档，为最终的公开发布打好基础。
