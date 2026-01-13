# mark2pdf PyPI 发布改造分析

## 一、当前状态分析

### 1.1 已具备的条件

**打包配置**
- ✅ 使用 `pyproject.toml` + hatchling 作为构建后端
- ✅ 已定义版本号和 CLI 入口点
- ✅ 模板文件可打包到包内

**可编程 API**
- ✅ 提供核心 API：`convert_file`, `convert_from_string`, `convert_directory`
- ✅ 支持 `ConversionOptions` 配置对象

**依赖**
- ✅ 已声明 Python 依赖：click, PyYaml, markdown-it-py, mdit-py-plugins, opencc, pillow

---

## 二、需要改造的内容

### 2.1 必须项（高优先级）

#### (1) 重命名为 mark2pdf
- 见 [mark2pdf重构方案.md](./mark2pdf重构方案.md)

#### (2) 添加 LICENSE 文件
- ✅ **已完成**
- 已添加 MIT LICENSE 文件

#### (3) 完善 README.md
- ✅ **已完成**
- 已重写 README，包含详细的安装说明、CLI 用法和 API 示例


#### (4) 补充 pyproject.toml 元数据
- ✅ **已完成**
- 已添加 authors, license, keywords, classifiers

```toml
[project]
name = "mark2pdf"
authors = [{name = "...", email = "..."}]
license = "MIT"
keywords = ["pdf", "markdown", "pandoc", "typst", "converter"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[project.urls]
Homepage = "https://github.com/xxx/mark2pdf"
```

---

### 2.2 推荐项（中优先级）

#### (5) 资源文件路径处理
- ✅ **代码已实现**：`helper_working_path.py` 已使用 `importlib.resources` 读取 `mark2pdf.templates`
- ✅ **已验证打包**：已确认 wheel 包中包含 `templates/*.typ` 和 `resources/frontmatter.yaml` 等非 Python 文件


#### (6) 添加 CHANGELOG.md
- ✅ **已完成**
- 已记录 0.7.3 版本变更

---

### 2.3 可选项（低优先级）

#### (7) 发布前测试
- ✅ **已验证构建**：`uv build` 成功生成 wheel 和 tar.gz
- ✅ **内容检查**：已确认 LICENSE 和 templates 包含在 wheel 中

```bash
uv build
twine check dist/*
pip install dist/mark2pdf-xxx.whl  # 干净环境测试
```

#### (8) Docker 镜像
- 已有 Dockerfile，可提供预配置镜像

---

## 三、改造清单

| 任务 | 优先级 | 工作量 |
|------|-------|--------|
| 重命名为 mark2pdf（含重构） | 高 | 2 小时 |
| 创建 LICENSE 文件 | 高 | 5 分钟 |
| 完善 README.md | 高 | 30 分钟 |
| 补充 pyproject.toml 元数据 | 高 | 10 分钟 |
| 验证资源文件路径 | 高 | 30 分钟 |
| 添加 CHANGELOG.md | 中 | 20 分钟 |
| 本地构建测试 | 中 | 20 分钟 |

---

## 四、用户调用示例（目标）

```bash
# 安装
pip install mark2pdf

# CLI
mark2pdf convert sample.md
mark2pdf convert --dir docs
```

```python
# 可编程 API
from mark2pdf import convert_file
convert_file("document.md")
```

---

## 五、已解决问题

1. ✅ **版本号同步**：已改用 `importlib.metadata` 动态读取
2. ✅ **模块名冲突**：重构方案中已整合为 `mark2pdf.*` 子模块
3. ✅ **PyPI 名称冲突**：已确认 `mark2pdf` 可用

---

## 六、发布范围讨论

### 6.1 核心包 vs WebUI

当前项目结构中，`web_ui/` 是独立目录（不在 `src/mark2pdf` 内）：

```
mark2pdf/
├── src/mark2pdf/     # 核心包（CLI + API）
├── web_ui/           # WebUI（独立）
│   ├── web_server.py
│   └── web_home.html
└── ...
```

**建议：仅发布核心包，不包括 webui**

| 考量 | 说明 |
|------|------|
| 分离关注点 | 核心功能是 MD→PDF 转换，webui 是附加功能 |
| 依赖简洁 | webui 可能引入额外依赖（Flask 等），核心用户不需要 |
| 现有结构 | `web_ui/` 在 `src/` 外，打包时默认不包含 |
| 常见做法 | CLI/API 作为核心包，webui 作为可选插件 |

**可选方案**：
- 将来可通过 `pip install mark2pdf[webui]` 安装（optional dependencies）
- 或发布独立包 `mark2pdf-webui`

---

### 6.2 fonts 目录

当前 `fonts/` 目录位于项目根目录，包含 `FZQingFSJW_Cu.TTF`（~5MB）。

**用途澄清**：
- 此目录**仅供 web_ui / Docker 使用**，与核心包无关
- 核心包用户通过 `mark2pdf fonts install` 按需下载字体到工作区

**是否纳入 web_ui？**

| 方案 | 说明 |
|------|------|
| ✅ 纳入 `web_ui/fonts/` | 结构更清晰，web_ui 相关资源集中管理 |

**建议**：将 `fonts/` 移入 `web_ui/fonts/`，同时更新 `Dockerfile` 和 `docker-compose.yml` 中的路径引用。
- **状态现状**：`fonts/` 已移动至 `web_ui/fonts/`，根目录已无此文件夹（✅ 已完成）。

---

## 七、发布操作指南

### 1. 准备工作
- 注册 PyPI 账号并获取 Token
- 确认 `dist/` 目录已清理（推荐）

### 2. 构建
```bash
rm -rf dist/
uv build
```

### 3. 发布
```bash
# 替换为实际 token
uv publish --token pypi-xxxxxxxxxxxx
```

### 4. 验证
```bash
pip install mark2pdf
```

---

*分析日期：2026-01-03*