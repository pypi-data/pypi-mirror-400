# Backcover BigLogo 实现计划

创建时间: 2026-01-03

## 需求

在 backcover-lib 中创建新的封底样式 `biglogo`，并修改现有的 `default` 样式：

- **default 样式**: 去掉中心的大 logo（保留左下角小 logo）
- **biglogo 样式**: 去掉左下角小 logo（保留中心大 logo）

用 `theme.backcoverstyle` 控制，类似 `theme.coverstyle` 的处理方式。

## 实现步骤

### 1. 创建新的封底库文件

复制 `nb-backcover-lib.typ` 为 `nb-backcover-biglogo-lib.typ`：
- 函数名改为 `backcoverpage_biglogo` 或保持 `backcoverpage`
- 保留中心 logo（第19-22行）
- 删除左下角 logo（第25行）

### 2. 修改现有 `nb-backcover-lib.typ`

- 去掉中心 logo 部分（第19-22行的 align(center + horizon) 块）
- 保留左下角的 logo（第25行）

### 3. 修改 `nb.typ` 主模板

1. 添加 import：
   ```typst
   #import "./nb-backcover-biglogo-lib.typ": backcoverpage as biglogo_backcover
   ```

2. 添加 `backcoverstyle` 参数（默认 "default"）到 conf 函数

3. 添加选择封底函数的逻辑（类似 coverstyle）：
   ```typst
   let backcoverpage_fn = if backcoverstyle == "biglogo" {
     biglogo_backcover
   } else {
     backcoverpage  // default
   }
   ```

4. 在 pandoc 模板部分添加：
   ```typst
   $if(theme.backcoverstyle)$
   backcoverstyle: "$theme.backcoverstyle$",
   $endif$
   ```

### 4. 更新 frontmatter.yaml 注释

添加 `backcoverstyle` 配置说明：
```yaml
# theme:
#   backcoverstyle: "default"   # 封底样式: "default" / "biglogo"
```

## 文件变更清单

| 文件 | 操作 |
|------|------|
| `nb-backcover-lib.typ` | 修改：去掉中心 logo |
| `nb-backcover-biglogo-lib.typ` | 新建：复制并去掉左下角 logo |
| `nb.typ` | 修改：添加 backcoverstyle 控制逻辑 |
| `frontmatter.yaml` | 修改：添加配置说明 |
