# mark2pdf Next.js 集成分析

日期：2024-12-31

如果将 `mark2pdf` 用作 Next.js 项目的构建时预处理工具（例如生成 PDF 供下载），需要考虑以下几点：

## 1. 安装与依赖

- **Python 环境**：Next.js 环境（Node.js）通常不包含 Python。
    - **推荐**：使用 `uv` 管理 Python 环境，确保 CI/CD 环境已安装 `uv`。
    - **方式**：在 `package.json` 中定义脚本，自动使用 `uv run` 执行。

## 2. npm script 集成

在 `package.json` 中：

```json
{
  "scripts": {
    "pdf:build": "uv run mark2pdf convert --dir docs --outdir public/pdfs",
    "build": "npm run pdf:build && next build"
  }
}
```

## 3. 核心考虑点

| 关注点 | 建议方案 |
|--------|----------|
| **输出目录** | 必须输出到 `public/` 目录，以便 Next.js 能提供静态文件下载。 |
| **构建缓存** | Next.js 有构建缓存。PDF 生成较慢，建议利用 inputs/outputs 缓存机制（如 TurboRepo）避免重复生成。 |
| **错误处理** | `mark2pdf` 失败应阻塞构建（返回非零 exit code），防止发布缺少 PDF 的版本。 |
| **Vercel/Netlify** | 需确保部署环境支持 Python + Pandoc + Typst。可能需要自定义 Build Image 或使用 Docker。 |

## 4. 开发体验 (DX)

- **Watch 模式**：用户修改 Markdown 时自动重新生成 PDF。
    - 结合 `concurrently`：`"dev": "concurrently 'next dev' 'npm run pdf:watch'"`
    - 需实现 `mark2pdf convert --watch`（低优先级特性）。
