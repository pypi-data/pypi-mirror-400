# Helper Typst 模板依赖处理简化方案

## 背景

当前 `helper_typst.py` 中的模板依赖处理逻辑较为复杂：
1. `parse_template_deps()` - 解析 `#import`/`#include` 找出 .typ 依赖
2. `parse_template_assets()` - 解析 `image()` 找出图片资产
3. `copy_template_deps()` - 逐一复制依赖文件
4. `cleanup_template_deps()` - 逐一清理依赖文件

## 问题

- 正则解析不够可靠，可能遗漏某些依赖
- 对于目录式模板（如 `nb/nb.typ`），所有依赖都在同一目录，逐个解析是多余的

## 简化思路

**目录式模板**：主模板文件在子目录中时，所有依赖都应该在同一目录，直接复制整个目录即可。

## 修改方案

### 1. 新增判断逻辑

```python
def is_directory_template(template_path: str) -> bool:
    """判断模板是否为目录式（模板文件在子目录中）"""
    template_file = Path(template_path)
    templates_dir = template_file.parent.parent  # 向上两级
    # 如果模板文件的父目录名与模板文件名匹配（如 nb/nb.typ），则为目录式
    return template_file.parent.name == template_file.stem
```

### 2. 简化 run_pandoc_typst

```python
def run_pandoc_typst(...):
    template_file = Path(template_path)
    
    # 目录式模板：复制整个模板目录
    if is_directory_template(template_path):
        template_dir = template_file.parent
        target_template_dir = Path(pandoc_workdir) / template_dir.name
        shutil.copytree(template_dir, target_template_dir, dirs_exist_ok=True)
        template_filename = f"{template_dir.name}/{template_file.name}"
    else:
        # 单文件模板：保持原有逻辑
        dependencies = parse_template_deps(template_path)
        assets = parse_template_assets(template_path)
        copy_template_deps(pandoc_workdir, template_path, dependencies + assets, verbose)
        template_filename = template_file.name
    
    # ... 执行 pandoc ...
    
    # 清理
    if is_directory_template(template_path):
        shutil.rmtree(target_template_dir, ignore_errors=True)
    else:
        cleanup_template_deps(...)
```

## 优势

1. **简单可靠**：不依赖正则解析，目录内所有文件都会被复制
2. **向后兼容**：单文件模板（如 `card.typ`）保持原有逻辑
3. **模板组织更清晰**：鼓励将模板及其依赖放在一个目录中

## 受影响的函数

- `run_pandoc_typst()` - 主函数，需要添加目录式模板判断
- 可选：保留 `parse_template_deps` 等函数用于单文件模板

## 待确认

1. 是否完全废弃 `parse_template_deps`/`parse_template_assets`？  废弃
2. 目录式模板的判断逻辑是否正确（`nb/nb.typ` vs `card.typ`）？ 正确
- **修正**：不能保留目录结构（`nb/nb.typ`），必须将 `nb/` 目录下的所有文件**平铺复制到工作目录根目录**。
  - 原因：Pandoc 生成的 Typst 文件位于工作目录根目录。如果模板中的 `#import` 使用相对路径（如 `./nb-lib.typ`），Typst 会在工作目录根目录查找，而不是 `nb/` 子目录。
  - 解决方案：将模板目录内容平铺复制。
