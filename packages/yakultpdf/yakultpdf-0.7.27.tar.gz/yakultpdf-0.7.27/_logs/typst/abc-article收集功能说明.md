# abc-articles 收集功能说明

## 概述

mark2pdf 模板实现了一个 article-item 收集功能，允许在 Markdown 文档中定义特殊标记的 article-item 块，这些 article-item 会被自动收集并在文档末尾统一显示。该功能参考了 Typst 官方模板 `dashing-dept-news/lib.typ` 的设计模式。

## 功能特点

- **声明式收集**：只需在需要的地方使用标记，无需手动管理 article-item 列表
- **自动收集**：无论 article-item 在文档的哪个位置定义，都会被自动收集
- **统一显示**：所有收集的 article-item 在文档末尾以"article-item 集合"的形式统一显示
- **保持样式**：收集的 article-item 保持原有的样式（灰色背景、圆角边框等）

## 工作流程

### 1. 标记阶段（Markdown 源文件）

在 Markdown 文件中使用 `:::{#abc}` 标记来定义要收集的 article-item：

```markdown
::: {#abc}
这是要收集的 article-item 内容
可以包含多行文本
支持 Markdown 格式
:::
```

### 2. 转换阶段（Pandoc 处理）

Pandoc 将 Markdown 转换为 Typst 时，会将 `:::{#abc}` 转换为 `<abc>` 标签：

**输入（Markdown）：**
```markdown
::: {#abc}
这是第一篇 article-item，应该被收集到文档末尾。
:::
```

**输出（Typst）：**
```typst
#block[
这是第一篇article-item，应该被收集到文档末尾。

] <abc>
```

### 3. 收集阶段（Typst 处理）

在 `mark2pdf.typ` 模板中，通过以下机制实现 article-item 收集：

#### 3.1 状态变量定义
```typst
// 用于收集article-item的状态变量
#let articles = state("articles", ())
```

#### 3.2 article-item 收集函数
```typst
// 定义article函数 - 收集article-item而不是直接显示
#let article(content) = articles.update(it => it + (content,))
```

#### 3.3 标签处理规则
```typst
// 处理pandoc转换后的标签
show <abc>: it => {
  article(it.body)
}
```

当遇到 `<abc>` 标签时，会调用 `article()` 函数，将 article-item 内容添加到状态中。

### 4. 显示阶段（文档渲染）

#### 4.1 article-item 显示函数
```typst
// 显示所有收集的article-item
#let show-articles() = context {
  let collected-articles = articles.final()
  if collected-articles.len() > 0 {
    v(3em)
    heading(level: 1)[article-item集合]
    v(2em)
    for article-content in collected-articles {
      block(
        above: 2em,
        below: 2em,
        width: 100%,
        fill: rgb("#F8F9FA"),
        radius: 0.5em,
        inset: (left: 1.5em, top: 1em, right: 1.5em, bottom: 1em)
      )[#article-content]
    }
  }
}
```

#### 4.2 在文档末尾调用
```typst
// THIS IS THE ACTUAL BODY:
doc                                          // this is where the content goes

// 在文档末尾显示所有收集的article-item
show-articles()
```

## 完整案例

### 输入文件（test_articles.md）

```markdown
---
title: 测试 article-item 收集功能
---

# 测试文档

这是正文内容。

## 第一部分

正文内容继续...

::: {#abc}
这是第一篇 article-item，应该被收集到文档末尾。
:::

## 第二部分

更多正文内容...

::: {#abc}
这是第二篇 article-item，也应该被收集到文档末尾。
:::

## 第三部分

最后一部分正文内容。

::: {#abc}
这是第三篇 article-item，同样会被收集。
:::
```

### 转换后的 Typst 文件（部分）

```typst
= 测试文档
<测试文档>
这是正文内容。

== 第一部分
<第一部分>
正文内容继续…

#block[
这是第一篇article-item，应该被收集到文档末尾。

] <abc>
== 第二部分
<第二部分>
更多正文内容…

#block[
这是第二篇article-item，也应该被收集到文档末尾。

] <abc>
== 第三部分
<第三部分>
最后一部分正文内容。

#block[
这是第三篇article-item，同样会被收集。

] <abc>
```

### 最终输出效果

在生成的 PDF 中，文档结构如下：

1. **标题**：测试文档
2. **第一部分**：正文内容继续...
3. **第二部分**：更多正文内容...
4. **第三部分**：最后一部分正文内容。
5. **article-item 集合**（自动添加的标题）
   - 第一篇 article-item，应该被收集到文档末尾。
   - 第二篇 article-item，也应该被收集到文档末尾。
   - 第三篇 article-item，同样会被收集。

## 技术实现细节

### 状态管理系统

使用 Typst 的 `state()` 函数创建持久化状态：

```typst
#let articles = state("articles", ())
```

- `"articles"`：状态变量的名称
- `()`：初始值（空元组）
- 在整个文档编译过程中保持状态

### 函数式更新

使用函数式编程模式更新状态：

```typst
articles.update(it => it + (content,))
```

- `it`：当前状态值
- `(content,)`：单元素元组，将新内容包装成元组
- `+`：元组连接操作

### Context 表达式

`articles.final()` 需要在 `context` 表达式中调用：

```typst
#let show-articles() = context {
  let collected-articles = articles.final()
  // ...
}
```

这是因为 `final()` 方法需要访问编译上下文。

### "不直接显示"的实现原理

这是整个收集机制的核心技术点。关键在于理解 Typst 中函数返回值与显示的关系。

#### 核心原理：函数返回值决定是否显示

在 Typst 中，只有当函数返回内容时，才会在页面上显示。这是理解"不直接显示"的关键。

#### 直接显示 vs 收集机制对比

**直接显示的版本：**
```typst
#let article(content) = {
  block(
    above: 2em,
    below: 2em,
    width: 100%,
    fill: rgb("#F8F9FA"),
    radius: 0.5em,
    inset: (left: 1.5em, top: 1em, right: 1.5em, bottom: 1em)
  )[#content]
}
```
- 函数返回一个 `block` 元素
- 这个元素会在页面上显示
- 每次调用都会立即显示

**收集而不显示的版本：**
```typst
#let article(content) = articles.update(it => it + (content,))
```
- 函数只调用 `articles.update()`
- `articles.update()` 只更新状态，不返回任何内容
- 整个函数调用不产生任何可见输出

#### 状态更新的工作原理

```typst
articles.update(it => it + (content,))
```

这个表达式的执行过程：
1. `articles.update()` 更新状态变量
2. 更新操作本身不返回可见内容
3. 新内容被添加到状态中，但不在当前位置显示

#### 实际执行过程

当遇到 `:::{#abc}` 时：

1. **Pandoc 转换**：`:::{#abc}` → `<abc>`
2. **Typst 处理**：`show <abc>` 规则被触发
3. **函数调用**：`article(it.body)` 被调用
4. **状态更新**：内容被添加到 `articles` 状态中
5. **当前位置**：不显示任何内容（因为函数没有返回内容）
6. **文档末尾**：`show-articles()` 获取所有收集的内容并显示

#### 为什么这样设计？

这种设计的优势：
- **声明式**：只需在需要的地方标记，无需手动管理
- **灵活性**：article-item 可以在文档的任何位置定义
- **统一性**：所有 article-item 在末尾以统一格式显示
- **可维护性**：不需要手动维护 article-item 列表

## 使用场景

### 1. 学术论文
- 将重要的引文、注释收集到文档末尾
- 统一管理参考文献

### 2. 技术文档
- 收集代码示例、配置说明
- 整理常见问题和解答

### 3. 报告文档
- 收集附录内容
- 整理补充材料

### 4. 教学材料
- 收集练习题、答案
- 整理扩展阅读

## 注意事项

### 1. 标记语法
- 必须使用 `:::{#abc}` 格式
- `abc` 是固定的标识符，不能更改
- 花括号是必需的

### 2. 内容格式
- 支持 Markdown 格式
- 可以包含多行文本
- 可以包含其他 Markdown 元素（链接、图片等）

### 3. 显示顺序
- article-item 按照在文档中出现的顺序收集
- 在文档末尾按照收集顺序显示

### 4. 样式统一
- 所有收集的 article-item 使用相同的样式
- 灰色背景（#F8F9FA）
- 圆角边框（0.5em）
- 统一的内边距

## 扩展可能性

### 1. 多类型 article-item
可以扩展支持不同类型的 article-item 标记：
```markdown
::: {#note}
这是注释
:::

::: {#warning}
这是警告
:::
```

### 2. 分类显示
可以按类型分类显示 article-item：
```typst
#let show-articles-by-type() = context {
  // 按类型分组显示
}
```

### 3. 自定义样式
可以为不同类型的 article-item 设置不同的样式：
```typst
#let article-note(content) = block(fill: rgb("#E3F2FD"))[#content]
#let article-warning(content) = block(fill: rgb("#FFF3E0"))[#content]
```

## 总结

article-item 收集功能通过 Typst 的状态管理系统，实现了声明式的 article-item 收集和统一显示。该功能简化了文档结构管理，提高了内容组织的灵活性，特别适合需要将分散的内容统一展示的场景。

通过简单的 `:::{#abc}` 标记，用户可以轻松地将重要内容收集到文档末尾，而无需手动管理 article-item 列表或担心显示顺序问题。
