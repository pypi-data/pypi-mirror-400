# Pandoc + Typst 作为网站后端服务的可行性讨论

> 日期：2026-01-01

## 一、核心问题

pandoc 和 typst 都是**命令行二进制工具**，需要在服务器上运行子进程。这带来几个挑战：

### 1.1 Serverless 平台基本不行

- **Cloudflare Workers**：❌ 不支持，V8 isolate 无法执行系统二进制
- **Vercel Edge Functions**：❌ 不支持系统调用
- **AWS Lambda**：⚠️ 技术上可以，但需要打包二进制到 layer，麻烦
- **Deno Deploy**：❌ 不支持

### 1.2 容器平台可行

- **Railway**：✅ 支持 Docker，可以安装任意二进制
- **Fly.io**：✅ 支持，甚至有持久卷
- **Render**：✅ 支持 Docker
- **自建 VPS**：✅ 完全控制

---

## 二、技术方案对比

### 方案 A：直接跑 Python + subprocess

```
┌─────────────────────────────────┐
│   Flask/FastAPI Web 服务         │
│   subprocess 调用 pandoc/typst   │
└─────────────────────────────────┘
```

**优点**：
- 实现简单，直接复用现有代码
- 调试方便

**缺点**：
- 每次请求创建子进程，开销大
- 并发时可能资源争抢

**适合**：低频使用，个人工具

---

### 方案 B：编译 Typst 为 WASM

typst 官方有 typst-wasm，理论上可以在纯 JS 环境运行。

**问题**：
- pandoc 没有官方 wasm 版本
- typst-wasm 缺少很多功能（如字体）
- 整个流程需要重写

**结论**：目前不现实

---

### 方案 C：预编译的微服务容器

```
┌─────────────────────────────────┐
│   Docker 容器                    │
│   ├── Python 应用               │
│   ├── Pandoc (预装)             │
│   └── Typst (预装)              │
└─────────────────────────────────┘
```

**这是最实际的方案**

---

## 三、实际约束

### 3.1 冷启动

- 容器启动需要时间（1-3秒）
- 第一次请求会慢

**缓解**：
- 保持至少一个实例常驻
- Railway/Fly.io 都支持最小实例数

### 3.2 字体

- 中文字体体积大（10-50MB 每个）
- 需要打包进镜像或挂载

**方案**：
- 内置 Noto Sans CJK（开源，约 20MB）
- 自定义字体通过持久卷挂载

### 3.3 并发

- 每个 pandoc/typst 调用消耗 CPU 内存
- 需要限制并发数

**方案**：
- 使用信号量控制同时执行数
- 或者用队列（Redis + Celery）

### 3.4 临时文件

- 转换过程需要写临时文件
- 需要定期清理

**方案**：
- 使用 `/tmp` (大多数平台自动清理)
- 或者用内存文件系统

---

## 四、成本估算

| 平台 | 最低配置 | 价格 |
|------|---------|------|
| Railway | 1 vCPU, 512MB | ~$5/月 |
| Fly.io | shared-cpu-1x, 256MB | ~$2/月 |
| Render | 512MB | 免费层有限制 |
| 自建 VPS | 1核2G | ~$5-10/月 |

---

## 五、Vercel 场景分析

### 5.1 Vercel 调用外部服务 ✅ 可行

```
┌─────────────────────────────────┐
│   Vercel (前端 + API Route)      │
│   调用外部 HTTP API              │
└──────────────┬──────────────────┘
               │ HTTP POST
               ↓
┌─────────────────────────────────┐
│   Railway/Fly.io (mark2pdf 服务) │
│   pandoc + typst                │
└─────────────────────────────────┘
```

**这是推荐方案**：
- Vercel 负责前端 + 鉴权 + 请求转发
- 后端服务（Railway/Fly.io）处理 PDF 生成
- 分离关注点，各司其职

**示例代码（Vercel API Route）**：
```typescript
// pages/api/convert.ts
export default async function handler(req, res) {
  const response = await fetch('https://your-mark2pdf.fly.dev/convert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ markdown: req.body.markdown }),
  });
  
  const pdf = await response.arrayBuffer();
  res.setHeader('Content-Type', 'application/pdf');
  res.send(Buffer.from(pdf));
}
```

---

### 5.2 Vercel Serverless Functions（非 Edge）⚠️ 技术上可行但不推荐

Vercel 普通 Serverless Functions（Node.js runtime）**理论上可以**执行二进制，但：

| 限制 | 说明 |
|------|------|
| 包体积 | 最大 50MB（压缩后），pandoc + typst 可能超限 |
| 执行时间 | 免费 10s，Pro 60s，转换可能超时 |
| 临时空间 | `/tmp` 只有 500MB |
| 维护困难 | 需要手动打包二进制到 layer |

**实操困难**：
- 需要编译 Linux x86_64 版本的 pandoc/typst
- 每次部署都要带上几十 MB 的二进制
- 调试体验差

**结论**：能跑，但太折腾，不如单独跑个容器服务

---

### 5.3 推荐架构

```
用户 → Vercel (Next.js) → Railway (mark2pdf API)
           │                      │
           ├─ 前端界面            ├─ /convert POST
           ├─ 用户鉴权            ├─ pandoc + typst
           └─ 请求限流            └─ 返回 PDF
```

**好处**：
- Vercel 免费额度处理前端
- 后端服务按需付费（~$5/月）
- 易于独立扩展和调试

---

## 六、结论与建议

### 5.1 可行性：✅ 可行，但有约束

pandoc + typst 方案**可以**作为网站后端服务运行，但必须使用**容器化部署**。

### 5.2 适合场景

- ✅ 个人/小团队内部工具
- ✅ 低频调用的文档服务
- ⚠️ 高并发场景需要仔细设计

### 5.3 不适合场景

- ❌ Serverless/边缘函数
- ❌ 资源受限的免费层

### 5.4 推荐路线

1. **先在本机验证**：docker-compose 起服务
2. **选平台**：Railway 或 Fly.io（对 Docker 友好）
3. **控制并发**：限制同时处理数
4. **预热实例**：避免冷启动

---

## 六、待验证的问题

1. typst 编译中文文档的实际耗时？
2. 容器镜像大小优化空间？（当前 Dockerfile 估计 500MB+）
3. 是否需要队列来削峰？
