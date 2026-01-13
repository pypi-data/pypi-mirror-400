# NB 模板语法扩展说明

本文档说明了 NB 模板支持的特殊语法扩展。

## 封面与封底 (Cover & Backcover)

封面样式通过 frontmatter 的 `coverstyle` 参数控制，封底样式通过 `backcoverstyle` 控制。

```yaml
---
theme:
  coverstyle: "default"   # 可选: "default", "report", "darkbg"
  backcoverstyle: "default" # 可选: "default", "biglogo"
  coverbg: "images/bg.jpg" # 仅当 coverstyle: "darkbg" 时生效
---
```

## 整页图片 (Fullimage)

显示一张占据整页的图片，自动分页。

```markdown
::: {#fullimage}
images/photo.jpg
fit=cover
:::
```
- 第一行：图片路径
- `fit`: 图片填充方式，可选 `cover` (铺满), `contain` (完整显示), `stretch` (拉伸)。默认 `contain`。

## 顶部出血图片 (Topimage)

强制分页，并在新页面的顶部显示一张出血（无边距）图片。文本内容在图片下方开始。

```markdown
::: {#topimage}
images/header.jpg
:::
```
- 图片按原始比例显示，宽度撑满页面。

## 底部出血图片 (Bottomimage)

在当前页面的底部显示一张出血（无边距）图片，并作为当前页面的结束（后续内容强制分页）。

```markdown
::: {#bottomimage}
images/footer.jpg
:::
```
- 图片按原始比例显示，宽度撑满页面。
- **排版注意**：如果当前页面的剩余空间不足以放下图片（例如文字过多），**图片会被自动挤到下一页的底部**。
- **编辑建议**：建议在放置 `bottomimage` 前预览页面空间，确保有足够位置。如果图片跑到了下一页，说明上一页文字太多，需要删减文字或调整位置。

## 带背景内容页 (Pagebg)

设置当前页面的背景图片。

```markdown
::: {#pagebg}
bg=images/background.jpg

# 页面标题
这里是带有背景图片的内容...
:::
```
- `bg=...`: 指定背景图片路径。
- 也支持 `{#pagebgwhite}`，文字颜色自动设为白色。

## 全页纯色块 (Overview / Fullpage)

创建一个整页的纯色块页面，常用于章节过渡或概览。

```markdown
::: {#overview}
fill=#E4F6F6

# 章节标题
章节简介...
:::
```
- `fill=...`: 自定义背景色（可选）。如果不指定，使用默认粉色或 frontmatter 中配置的 `overview-fill`。
- 也支持 `{#ending}`，内容垂直居中偏下显示。

## 评论块 (Custom Blocks)

- `::: {#comment}`: 将内容收集到文档末尾显示（不显示在当前位置）。
- `::: {#floatcomment}`: 在页面右侧显示浮动评论框。
