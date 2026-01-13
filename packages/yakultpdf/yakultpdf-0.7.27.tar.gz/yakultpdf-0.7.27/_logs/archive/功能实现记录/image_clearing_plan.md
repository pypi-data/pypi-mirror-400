# imageclearing 重构计划

## 1. 目标

将 `imageclearing` 重构为 `mark2pdf image` 命令组，包含两个核心功能：
1. `process`: 图片清理与下载
2. `migrate`: 目录结构转换 (单文件模式 <-> 文件夹模式)

## 2. 功能设计

### 2.1 模式定义

- **单文件模式 (Flat Mode)**
  - Markdown: `in/abc.md`
  - 图片目录: `in/images/abc/`
  - 图片链接: `![](images/abc/1.jpg)`

- **文件夹模式 (Folder Mode)**
  - Markdown: `in/abc/index.md` (或 `abc.md`)
  - 图片目录: `in/abc/images/`
  - 图片链接: `![](images/1.jpg)`

### 2.2 mark2pdf image process

用于下载远程图片并清理无效链接。

**逻辑 (伪代码):**

```python
def process(path):
    if 是文件夹(path):
        处理文件夹内所有 .md 文件
        return

    # 单个文件处理
    if 存在目录("images/" + 文件名stem):
        模式 = 单文件模式
        图片目录 = "images/" + 文件名stem
    else if 存在目录("./images"):
        模式 = 文件夹模式
        图片目录 = "./images"
    else:
        报错("找不到图片目录")
    
    读取内容()
    下载远程图片(到=图片目录)
    写入内容()
```

### 2.3 mark2pdf image migrate

用于在两种模式间转换。

**命令:**
- `mark2pdf image migrate abc.md --to-folder`
- `mark2pdf image migrate abc/ --to-file`

**逻辑 (伪代码):**

```python
# 单文件 -> 文件夹 (--to-folder)
def migrate_to_folder(file_path):
    # 输入: in/abc.md
    
    创建目录("in/abc")
    创建目录("in/abc/images")
    
    移动文件("in/abc.md", "in/abc/index.md")
    移动内容("in/images/abc/*", "in/abc/images/")
    
    更新内容链接:
    replace("images/abc/", "images/")
```

```python
# 文件夹 -> 单文件 (--to-file)
def migrate_to_file(folder_path):
    # 输入: in/abc/
    
    md_file = 找md文件(folder_path) # 如 in/abc/index.md
    
    移动文件(md_file, "in/abc.md")
    创建目录("in/images/abc")
    移动内容("in/abc/images/*", "in/images/abc/")
    
    更新内容链接:
    replace("images/", "images/abc/")
    
    删除空目录("in/abc")
```

## 3. 实现步骤

1. 创建 `src/mark2pdf/commands/image.py`，定义 `proccess` 和 `migrate` 命令。
2. 实现 `ImageProcessor` 类，支持通用图片格式 (`*.*`)。
3. 实现 `StructureMigrator` 类，负责移动文件和替换链接。
4. 在 `cli.py` 中注册新命令。
5. 移除旧的 `imageclearing` 命令。
