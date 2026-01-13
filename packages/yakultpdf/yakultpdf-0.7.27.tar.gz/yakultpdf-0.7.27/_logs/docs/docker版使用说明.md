# Docker 部署与字体配置说明

## 1. 快速开始

### 本地运行 (Docker Compose)
推荐用于本地开发和测试，自动挂载本地字体。
```bash
docker compose up -d --build
```
- 服务地址: http://localhost:8000
- 停止服务: `docker compose down`

### 本地运行 (uv)
如果你已在本地安装了 Pandoc 和 Typst：
```bash
uv sync --extra web
uv run uvicorn web_ui.web_server:app --host 0.0.0.0 --port 8000
```

## 2. Railway / 云端部署字体配置

云端环境（如 Railway）无法读取你电脑上的字体，因此必须将字体文件**打包到镜像中**。

### 第一步：准备字体文件
其中 **LXGW Wenkai (霞鹜文楷)** 和 **Source Han Sans SC (思源黑体)** 会在构建过程中**自动下载安装**，无需你手动上传。

必须要你**手动复制**到 `fonts/` 文件夹的字体（如果没有，可能导致样式差异）：

1.  **LXGW Wenkai Mono (霞鹜文楷 Mono)**
    *   用途：`nb-lib.typ` 代码块或等宽场景
    *   文件名示例：`LXGWWenKaiMono-Regular.ttf`
    *   *注：当前自动安装脚本未包含 Mono 版*
2.  **YouSheBiaoTiHei (优设标题黑)**
    *   用途：`nb-lib.typ` 标题字体
    *   文件名示例：`YouSheBiaoTiHei.ttf`
3.  **FZQingFangsongs (方正清刻本悦宋简)**
    *   用途：`gaozhi-lib.typ` 书法练习纸字体
    *   文件名示例：`FZQingFangsongs.ttf`

### 第二步：部署
项目已配置好 `Dockerfile`，会自动将 `fonts/` 目录下的所有字体复制到镜像内并安装。
1. 提交更改（包含 `fonts/` 目录下的字体文件）：
   ```bash
   git add fonts/
   git commit -m "Add custom fonts for deployment"
   git push
   ```
2. Railway 会自动重新构建并部署。

### 验证字体
可以通过查看容器日志或输出的 PDF 确认字体是否生效。如果出现字体缺失（显示的不是预期的字体），请检查文件名和 `Typst` 模板中的字体名称是否一致。

