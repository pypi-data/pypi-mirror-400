# frontmatter 控制 overview-fill

通过 frontmatter 的 `overview-fill` 字段，统一设置文档中所有 `<overview>` 块的默认背景色。

## 使用

```yaml
---
overview-fill: lightblue   # 或 #E4F6F6 或 default
---
```

支持值：
- `default` → 粉色 `#FFF5F5`
- `lightblue` → 浅蓝 `#E4F6F6`  
- `#XXXXXX` → 任意颜色

## 优先级

overview 块内的 `fill=` 配置 > frontmatter `overview-fill` > 系统默认 `#FFF5F5`
