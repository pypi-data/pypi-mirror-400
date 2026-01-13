# createpdf -o --open 选项实现方案

## 需求
在 `createpdf` 命令中增加 `-o --open` 选项，生成 PDF 后用系统默认程序打开。

## 修改范围

| 文件 | 修改内容 |
|------|----------|
| `createpdf.py` | 添加 `-o/--open` 选项 |
| `conversion.py` | 三个 `run_*` 函数添加 `open_file` 参数 |
| `core.py` | `convert_file` 返回 `Path\|None` 而非 `bool` |
| `directory.py` | `convert_directory` 同上 |
| `utils.py` | 新增 `open_with_system(filepath)` |

## 返回值变更影响范围

`convert_file` 调用方（需把 `if success:` 改为 `if result:`）：
- `scripts/gaozhi.py`
- `scripts/youth.py`
- `src/config_manager/defaults.py`
- `src/config_manager/conversion.py` - 中间层
- `tests/test_output_format.py`

`convert_directory` 调用方：
- `src/markdown2pdf/cli.py`
- `src/config_manager/conversion.py`
- `tests/test_cli.py`

## 调用链
```
createpdf.py → run_*(..., open_file=True)
  → convert_file() 返回 Path|None
  → if open_file and result: open_with_system(result)
```

---

## 后续 update 操作指引

1. **修改底层** (`core.py`, `directory.py`)
   - `convert_file` / `convert_directory` 返回 `Path | None`

2. **同步调用方** - 把 `if success:` 改为 `if result:`
   - `scripts/gaozhi.py`
   - `scripts/youth.py`
   - `cli.py`
   - `defaults.py`
   - 相关测试

3. **添加工具函数** (`utils.py`)
   ```pseudo
   def open_with_system(filepath):
       subprocess.run(["open", filepath])  # macOS
   ```

4. **修改中间层** (`conversion.py`)
   - 添加 `open_file` 参数，调用 `open_with_system`

5. **修改入口** (`createpdf.py`)
   - 添加 `-o/--open` 选项

6. **测试**
   ```bash
   createpdf test.md -o
   createpdf --dir mydir -o
   ```
