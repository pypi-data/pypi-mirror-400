---
description: 在开发环境中测试模板功能
---

# 开发环境测试工作流

// turbo-all

## 前置条件

1. 确保项目根目录有 `mark2pdf.config.toml` 配置文件
2. 配置中的 `template` 路径指向源码模板目录：`src/mark2pdf/templates`
3. 输入文件放在 `_working/in/` 目录

## 测试步骤

### 1. 创建测试 Markdown 文件

在 `_working/in/` 目录下创建测试文件，例如 `test_xxx.md`：

```markdown
---
title: "测试标题"
author: "测试作者"
toc-depth: 3
theme:
  template: "nb"
  coverstyle: "darkbg"
---

# 一级标题
## 二级标题
### 三级标题

内容...
```

### 2. 运行转换命令

在项目**根目录**执行：

```bash
uv run yakultpdf convert test_xxx.md --verbose
```

- `--verbose` 显示详细日志，便于调试
- 输出 PDF 在 `_working/out/` 目录

### 3. 检查输出

打开生成的 PDF 文件验证效果。

## 常见问题

### 找不到文件

确保：
- 在项目根目录执行命令（有 `mark2pdf.config.toml`）
- 测试文件在 `_working/in/` 目录中

### 图片/资源找不到

- 图片放在 `_working/in/images/` 目录
- frontmatter 中引用相对路径如 `./images/xxx.png`

### 字体警告

- 开发测试可忽略字体警告，系统会回退默认字体
- 如需特定字体，放在 `_working/fonts/` 目录
