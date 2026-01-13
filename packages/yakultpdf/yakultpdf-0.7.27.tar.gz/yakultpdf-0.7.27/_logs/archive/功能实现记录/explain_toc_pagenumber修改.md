# TOC 和 PageNumber 配置

## 默认行为

| 配置项 | 默认 | 关闭方式 |
|-------|------|---------|
| 目录 | **显示**（toc-depth: 3） | `disables: [toc]` |
| 页码 | **显示** | `disables: [pagenumber]` |

---

## 为什么改用 disables

`disables` 是列表型变量，pandoc 只有在该字段存在时才会输出变量，避免了布尔 `false` 被忽略导致的“无法关闭”问题。

---

## 示例

默认显示目录和页码（无需设置）：
```yaml
---
title: 文章标题
---
```

关闭目录和页码：
```yaml
---
title: 文章标题
disables:
  - toc
  - pagenumber
---
```
