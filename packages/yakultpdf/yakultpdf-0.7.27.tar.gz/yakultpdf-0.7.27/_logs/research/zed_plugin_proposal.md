# mark2pdf Zed 插件化方案研究

目标：将 `mark2pdf` 集成到 Zed editor 中，作为插件运行（仅限 macOS）。

## 核心背景

Zed 编辑器的插件（Extensions）机制与其他编辑器（如 VS Code）不同：
1.  **技术栈**：插件必须使用 **Rust** 编写，并编译为 **WebAssembly (Wasm)** (target `wasm32-wasip2`)。
2.  **沙箱机制**：Wasm 运行在沙箱中，但可以通过 `zed_extension_api` 获取宿主机的部分权限（如执行命令）。
3.  **主要用途**：Zed 插件目前主要用于语言支持 (LSP, TreeSlider)、主题 (Themes) 和 Slash Commands (AI 助手命令)。

基于此，我们有两种集成 `mark2pdf` 的思路：

---

## 方案一：原生 Tasks 集成（轻量级，推荐）

如果目标仅是让用户在 Zed 中方便地调用 `mark2pdf`，最“原生”且低成本的方式是使用 Zed 的 `tasks` 功能，而不是开发完整的二进制插件。

### 实现方式
在项目根目录创建 `.zed/tasks.json`：

```json
[
  {
    "label": "mark2pdf: build current file",
    "command": "mark2pdf convert $ZED_FILE --open",
    "use_new_terminal": true,
    "allow_concurrent_runs": false
  },
  {
    "label": "mark2pdf: build project",
    "command": "mark2pdf convert .",
    "use_new_terminal": true
  }
]
```

### 优缺点
*   **优点**：无需开发插件，无需编译 Rust，零依赖，配置文件随项目分发。
*   **缺点**：用户需要在每个项目中配置，或配置全局 Tasks；无法提供复杂的交互逻辑。

---

## 方案二：开发专用 Zed Extension（正式插件化）

如果要打包发布一个 `mark2pdf` 插件，让用户在 Extension Store 中下载，我们需要按照以下架构开发。

### 1. 架构设计

*   **前端 (Zed)**: 一个编译为 Wasm 的 Rust 程序。
*   **后端 (CLI)**: 宿主机上安装的 `mark2pdf` Python 包 (通过 `uv` 或 `pip` 安装)。
*   **交互**:
    1.  插件通过 `zed_extension_api::process::Command` 调用宿主机的 `mark2pdf` 命令。
    2.  插件读取 `command_palette` 或 `slash_command` 的输入触发执行。

### 2. 开发步骤

#### A. 项目初始化
结构如下：
```text
mark2pdf-zed/
├── extension.toml   # 插件元数据
├── Cargo.toml       # Rust 依赖
└── src/
    └── lib.rs       # 核心逻辑
```

`extension.toml`:
```toml
id = "mark2pdf"
name = "Mark2pdf"
version = "0.0.1"
schema_version = 1
authors = ["Your Name"]
description = "Build PDF from Markdown using mark2pdf."
repository = "https://github.com/..."
```

#### B. 核心代码 (`src/lib.rs`)

需要实现 `zed::Extension` trait。

> *注意：由于 Zed API 还在快速迭代，具体 API 签名可能变化，以下为伪代码逻辑。*

```rust
use zed_extension_api as zed;

struct Mark2pdfExtension;

impl zed::Extension for Mark2pdfExtension {
    fn new() -> Self {
        Self
    }
    
    // 如果是 Language Extension，这里会有 language_server_command
    // 但作为工具插件，我们可能需要注册 Slash Command 或 Task Provider (如果有 API)
    // 目前 Zed 对通用 "Command Palette Action" 的 API 支持较为有限，
    // 最通用的方式是提供 Slash Command (用于 Assistant) 或 集成 Language Server。
    
    // 这里假设我们通过 Slash Command 暴露功能 (用户输入 /pdf 触发)
    // 或者，更进一步，如果 mark2pdf 未来支持 LSP 协议，这里直接启动 mark2pdf lsp。
}

zed::register_extension!(Mark2pdfExtension);
```

#### C. 调用本地命令关键点

Zed 插件调用本地命令需要权限，且必须通过 `Process` API。

```rust
// 伪代码：执行构建命令
fn run_mark2pdf_build(worktree_path: &str, file_path: &str) -> Result<(), String> {
    // 检查命令是否存在
    let path = zed::worktree()?.which("mark2pdf").ok_or("mark2pdf not found")?;
    
    let output = zed::process::Command::new(&path)
        .arg("convert")
        .arg(file_path)
        .current_dir(worktree_path)
        .exec() // 这会触发权限请求
        .map_err(|e| e.to_string())?;
        
    // 处理 output
    Ok(())
}
```

### 3. 发布与安装
1.  **本地调试**：在 Zed 中 "Extensions" -> "Install Dev Extension"，选择本地目录。
2.  **发布**：提交 PR 到 `zed-industries/extensions` 仓库。

---

## 结论与建议

鉴于 Zed 插件系统目前通过 Wasm 强沙箱化，且主要针对 "语言服务 (LSP)" 和 "主题" 优化，**开发一个纯粹为了运行 Shell 命令的 Native Plugin 性价比目前较低**，且 API 限制较多（例如很难直接在 Command Palette 注册除了 LSP 相关的任意命令）。

**最佳实践路径**：
1.  **当前**：提供官方的 `.zed/tasks.json` 模板片段，推荐用户直接粘贴使用。这是最符合 Zed 哲学（Configuration over Plugin for tasks）的做法。
2.  **未来**：如果 `mark2pdf` 实现了 LSP 协议（即变成一个 Language Server），那么开发一个 Zed Extension 就非常有意义了（提供实时诊断、自动补全、保存时自动编译等）。

**推荐行动**：在文档中增加 "IDE 集成 -> Zed" 章节，记录 JSON Task 配置方法。
