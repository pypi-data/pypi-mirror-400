# mark2pdf VS Code/Cursor Extension 方案研究 (v3)

目标：开发一个轻量级的 VS Code (及 Cursor) 插件，为 `mark2pdf` 提供原生集成体验。

## 1. 核心价值与功能定位

插件的核心定位是 **CLI Wrapper**，旨在提供比终端更便捷的入口，而非替代 CLI。

核心功能：
1.  **便捷入口**：提供命令面板 (Command Palette) 和右键菜单，无需记忆命令行参数。
2.  **可视化反馈**：在 Output 面板显示构建日志，能够点击错误跳转（这是 CLI 难以做到的）。
3.  **任务集成**：通过 VS Code Task 系统运行构建。

---

## 2. 架构设计

### A. 插件主体
*   **技术栈**：Node.js / TypeScript。
*   **运行机制**：作为简单的胶水层，直接调用宿主机环境中已安装的 `mark2pdf` CLI。
*   **环境假设**：假设用户已经安装了 `mark2pdf` (通过 `pip` 或 `uv`)。插件只负责检测并运行，如果找不到则报错提示用户手动安装。

### B. 关键技术点

#### 1. CLI 调用
*   优先检测当前 Workspace 选定的 Python 环境 (与 Python 插件联动)。
*   Fallback 到系统 `PATH` 中的 `mark2pdf` 命令。
*   使用 `child_process.spawn` 执行构建命令。

#### 2. 日志与诊断
*   **Output Channel**：创建一个名为 "Mark2pdf" 的输出面板，实时流式显示 CLI 的标准输出/错误。
*   **Problem Matcher**：编写正则匹配规则，解析 `mark2pdf` 的错误日志（如 `Error: file not found at line 10`），自动在编辑器中生成波浪线报错。

#### 3. 预览机制 (Native)
*   **不内置 Viewer**：保持插件轻量。
*   **行为**：构建成功后，调用 VS Code 原生 API `vscode.open(uri)` 打开生成的 PDF 文件。
    *   如果用户安装了 `vscode-pdf` 等插件，会在 VS Code 内打开。
    *   否则，会调用系统默认 PDF 阅读器打开。

---

## 3. 具体实施方案

1.  **Commands**:
    *   `Mark2pdf: Convert Current File`: 构建当前编辑器焦点的 `.md` 或 `.typ` 文件。
    *   `Mark2pdf: Convert Project`: 在根目录下运行 `mark2pdf convert .`。

2.  **Menus**:
    *   **编辑器标题栏**：添加一个 "Build PDF" 图标。
    *   **资源管理器右键**：对 `.md` 文件及文件夹添加 "Convert with mark2pdf"。

3.  **Task Provider**:
    *   自动检测 `mark2pdf.config.toml`，注册为 VS Code Task (`Terminal -> Run Task`)。
    *   允许用户在 `.vscode/tasks.json` 中配置额外参数。

4.  **Configuration**:
    *   `mark2pdf.executablePath`: 允许用户手动指定 `mark2pdf` 的路径（解决环境检测不到的问题）。

---

## 4. 结论

这是一个标准且克制的 IDE 插件方案。
它不包含任何 Python 源码，不包含大型二进制依赖（如 pdf.js），维护成本极低。它仅仅是把 CLI 的能力以 GUI 的形式暴露出来，符合 Unix 哲学。
