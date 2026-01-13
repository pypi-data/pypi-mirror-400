# Typst 模板导入机制简化方案

## 最终实现

当用户设定模板名称为 `nb` 时，系统按以下顺序查找：

| 优先级 | 路径 | 说明 |
|:---:|:---|:---|
| 1 | `nb.typ` | 直接模板文件 |
| 2 | `nb/nb.typ` | 目录下同名模板文件 |
| 3 | `nb/index.typ` | 目录下 index 文件 |

## 修改的文件

### 核心逻辑
- `src/mark2pdf/helper_workingpath/helper_working_path.py`
  - 新增 `_resolve_template_variants()` 辅助函数
  - 修改 `_get_bundled_template_path()` 支持变体查找
  - 修改 `_check()` 函数使用新逻辑

### 默认值
- `src/mark2pdf/defaults.py` - DEFAULT_TEMPLATE 改为 `"nb"`
- `src/mark2pdf/config/defaults.py` - 配置模板中改为 `"nb"`

### 测试更新
- `src/mark2pdf/core/tests/test_cli.py`
- `src/mark2pdf/tests/test_cli.py`
- `src/mark2pdf/tests/test_manager.py`
- `src/mark2pdf/tests/test_batch_conversion.py`
- `src/mark2pdf/helper_workingpath/tests/test_working_path_helper.py`

## 使用方式

```yaml
# frontmatter 中只支持 theme.template 格式
theme:
  template: nb  # 自动解析为 nb.typ 或 nb/nb.typ 或 nb/index.typ
```

完整路径（如 `nb/nb.typ`）仍然有效，作为回退兼容。
