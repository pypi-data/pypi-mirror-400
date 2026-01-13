# nb / nb-lib 可配置项梳理

## 当前 frontmatter 配置项

### 基础元数据
- `title` - 文章标题
- `description` - 文章说明（封面引用区）
- `author` - 作者
- `date` - 日期
- `edition` - 系列名（封面右上方）
- `publication-info` - 出版物信息

### 封面相关
- `heroimage` - 封面图（对象：image + caption）
- `logo` - logo 图片

### 目录与结构
- `toc-depth` - 目录深度（数值）
- `sourcelink` - 目录页来源信息

### 样式与主题
- `tyfont` - 正文字体
- `tyfont_title` - 标题字体
- `overview-fill` - overview 块默认背景色

### 页面元素
- `leftheader` - 页眉左侧内容
- `watermark` - 页面背景水印
- `footer-image` - 页脚右侧图片（如二维码）

### 禁用项（统一入口）
- `disables` - 禁用项列表，支持 `cover` / `backcover` / `toc` / `indent` / `pagenumber` / `header`

---

## 本次讨论结论

| 议题 | 结论 |
|-----|------|
| 1）页码 | ✅ `disables: [pagenumber]` 隐藏页码 |
| 2）toc 和版权页 | ✅ `disables: [toc]` 仅关闭目录；封底由 `backcover` 控制 |
| 3）封面版式 | 暂不变化 |
| 4）右侧留空 | 暂不变化 |

---

## 配置逻辑说明

- `disables: [cover]` → 同时关闭封面和封底
- `disables: [backcover]` → 仅关闭封底
- `disables: [toc]` 或 `toc-depth: 0` → 仅关闭目录，封底不受影响
- `disables: [pagenumber]` → 隐藏页码
- `disables: [header]` → 隐藏页眉
- `disables: [indent]` → 关闭首行缩进
