# Frontmatter Theme 配置方案

## 需求

1. 新增 `theme` 配置组到 frontmatter
2. `theme.template` - 指定模板文件
3. `theme.coverstyle` - 指定封面样式 ("default" / "report")
4. 移除顶级 `template` 字段（不保留向后兼容）

## 配置结构

### Frontmatter 新格式

```yaml
---
title: 文档标题
theme:
  template: "nb/nb.typ"     # 模板文件
  coverstyle: "report"      # 封面样式
---
```

### 优先级

`theme.template` > `config.toml [options].default_template`

### config.toml 保持不变

```toml
[paths]
template = "template"       # 模板目录（保留）

[options]
default_template = "nb.typ" # 全局默认模板（保留）
```

## 修改文件

### Python 端

1. `config/loader.py`
   - `resolve_template()` 读取 `frontmatter["theme"]["template"]`
   - 移除对顶级 `template` 的支持

2. `helper_typst/helper_typst.py`
   - 传递 `theme.coverstyle` 到 typst

3. `resources/frontmatter.yaml`
   - 添加 theme 示例注释

### Typst 端

4. `templates/nb/nb.typ`
   - 同时导入两个 cover lib
   - 根据 coverstyle 参数选择

```typst
#import "./nb-cover-lib.typ": coverpage as default_cover
#import "./nb-report-cover-lib.typ": coverpage as report_cover

#let conf(
  coverstyle: "default",  // 新增
  // ...
) = {
  let coverpage = if coverstyle == "report" { report_cover } else { default_cover }
  // ...
}
```

Pandoc 模板：
```typst
$if(theme.coverstyle)$
coverstyle: "$theme.coverstyle$",
$endif$
```

## 实现步骤

- [x] 修改 `config/loader.py`
- [x] 修改 `cli.py` 和 `conversion.py` 的调用点
- [x] 修改 `nb.typ`
- [x] 更新 `frontmatter.yaml`
- [x] 测试（ruff check 通过）
