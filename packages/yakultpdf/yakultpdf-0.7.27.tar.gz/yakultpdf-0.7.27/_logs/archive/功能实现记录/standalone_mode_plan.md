# convert/gaozhi 独立运行模式计划

## 问题

当前 `convert` 和 `gaozhi` 必须在含 `mark2pdf.config.toml` 的工作区运行，否则报错。

**期望**: 用户可在任意目录直接运行 `mark2pdf convert test.md`。

---

## 方案

### 核心改动：ConfigManager 增加 fallback

```python
# config_loader.py

@classmethod
def _resolve_data_root(cls) -> Path | None:
    # 1. 当前目录有配置 -> 返回
    # 2. 向上查找配置 -> 返回
    # 3. 都没有 -> 返回 None（不抛异常）

@classmethod  
def load(cls) -> Mark2pdfConfig:
    data_root = cls._resolve_data_root()
    if data_root:
        return cls._load_toml(data_root)
    return cls._create_standalone_config()

@classmethod
def _create_standalone_config(cls) -> Mark2pdfConfig:
    # 独立模式：输入输出均为当前目录
    return Mark2pdfConfig(
        paths=PathsConfig(input=".", output=".", tmp="."),
        build=BuildConfig(default_template="nb.typ"),
        data_root=Path.cwd(),
        code_root=get_code_root(),
    )
```

---

## 修改文件

| 文件 | 改动 |
|------|------|
| `config_loader.py` | `_resolve_data_root` 返回 None 而非抛异常；新增 `_create_standalone_config` |
| `gaozhi.py` | 无需改动（自动继承） |

---

## 验证计划

### 现有测试

```bash
uv run pytest src/mark2pdf/tests/ -v
```

### 新增测试用例

在 `test_cli.py` 新增：

```python
def test_convert_standalone_mode(tmp_path, monkeypatch):
    """在无配置文件目录运行 convert --dry-run 应使用默认配置"""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "test.md").write_text("# Test")
    
    result = runner.invoke(main, ["convert", "test.md", "--dry-run"])
    assert result.exit_code == 0
    assert "test.md" in result.output
```

### 手动验证

```bash
cd /tmp
echo "# Hello" > hello.md
mark2pdf convert hello.md --dry-run
# 预期：显示执行计划，paths.input=. paths.output=.
```

