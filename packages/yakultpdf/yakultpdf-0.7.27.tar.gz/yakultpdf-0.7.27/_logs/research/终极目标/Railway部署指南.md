# Railway 部署指南

Railway 是一个现代化的 PaaS 平台，非常适合部署 Docker 化应用。本指南介绍如何在 Railway 上部署本项目。

## 1. 核心机制

- **原生 Docker 支持**：直接读取 `Dockerfile` 构建。
- **自动构建**：连接 GitHub 后，Push 代码自动触发部署。
- **动态端口**：Railway 注入 `$PORT` 环境变量，应用必须监听此端口 (Host: `0.0.0.0`)。

## 2. 准备 Dockerfile

在项目根目录确保 `Dockerfile` 配置正确。

**关键配置项 (伪代码/示例)**:

```dockerfile
# 基础镜像
FROM python:3.10-slim

# 环境设置
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 启动命令 (关键)
# 必须监听 0.0.0.0 并使用 $PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### 注意事项

1.  **监听地址**: 必须是 `0.0.0.0`。
2.  **端口**: 必须读取环境变量 `PORT`。

## 3. 部署方式

推荐 **基于 GitHub** 的自动部署。

1.  **登录 Railway**: 使用 GitHub 账号。
2.  **新建项目**: 选择 "Deploy from GitHub repo"。
3.  **选择仓库**: 选中本项目仓库。
4.  **配置变量**: 在 "Variables" 中添加必要的环境变量 (如 `DATABASE_URL`, API Key 等)。
5.  **生成域名**: 在 "Settings" -> "Networking" 中生成公网域名。

## 4. 高级配置 (railway.json)

如需自定义构建行为，可在根目录添加 `railway.json`。

```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn core.wsgi",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

## 5. 常见问题

-   **持久化**: Railway 文件系统是临时的。如需保存文件，请挂载 **Volume**。
-   **构建速度**: 优化 Dockerfile 层级，先 COPY 依赖文件安装，再 COPY 代码。
