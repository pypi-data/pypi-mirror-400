# Typst 状态管理实现状态说明

## 当前状态：✅ 已实现并有效

### 实现概述
当前的 Typst 状态管理系统已经成功实现并正常工作。通过 `term-lib.typ` 中的状态管理机制，可以在 `term-doc` 函数中设置全局状态，并在 `termgrid` 函数中获取和使用这些状态。

### 核心实现

#### 1. 状态定义
```typst
#let source-state = state("source", none)
#let cn-state = state("cn", false)
```

#### 2. 状态设置（在 term-doc 中）
```typst
#let term-doc(
  title: none,
  source: none,
  cn: false,
  body
) = {
  // 设置状态 - 必须在文档内容中调用才能生效
  source-state.update(source)
  cn-state.update(cn)
  
  // ... 其他文档设置
  body
}
```

#### 3. 状态获取（在 termgrid 中）

注意，必须在  context[]中获取！！！！

```typst
#let termgrid(
  category: none,
  source: none,
  cn: false,
)={
  context [
    #let actual-source = if source != none { source } else { source-state.get() }
    #let actual-cn = if cn != false { cn } else { cn-state.get() }
    
    // 使用状态值进行数据处理
    #let data = csv(actual-source, row-type: dictionary)
    #let filtered-data = data.filter(term => term.category == category)
    
    // ... 渲染逻辑
  ]
}
```

### 工作流程

1. **文档级别设置**：在 markdown 文件的 frontmatter 中设置 `source` 和 `cn` 参数
2. **状态传递**：`term-doc` 函数读取 frontmatter 参数并更新全局状态
3. **状态使用**：`termgrid` 函数获取全局状态，如果没有显式传入参数则使用状态值
4. **数据渲染**：基于状态值加载对应的 CSV 数据并渲染术语卡片

### 实际应用示例

#### 英文版本 (term.md)
```yaml
---
title: "LLM Lingo: Must-Know Terms"
source: llmtermcn.csv
cn: false
---
```

#### 中文版本 (term_cn.md)
```yaml
---
title: "LLM Lingo: Must-Know Terms"
source: llmtermcn.csv
cn: true
---
```

### 关键特性

1. **全局状态管理**：状态在文档级别设置，在整个文档中可用
2. **参数优先级**：显式传入的参数优先于状态值
3. **自动语言切换**：根据 `cn` 状态自动显示英文或中文内容
4. **数据源管理**：根据 `source` 状态自动加载对应的 CSV 数据

### 技术要点

- **状态更新语法**：在函数内部调用 `state.update()` 时不需要 `#` 前缀
- **状态获取语法**：使用 `context state.get()` 获取当前状态值
- **状态作用域**：状态是全局的，可以在任何函数中访问
- **状态生效时机**：状态更新必须在文档内容中调用才能生效

### 验证状态

当前实现已经通过以下方式验证：
- ✅ 状态可以在 `term-doc` 中正确设置
- ✅ 状态可以在 `termgrid` 中正确获取
- ✅ 英文和中文版本都能正确渲染
- ✅ 数据源切换正常工作
- ✅ 参数优先级机制正常

### 使用说明

1. 在 markdown 文件的 frontmatter 中设置 `source` 和 `cn` 参数
2. 使用 `#term-doc()` 包装整个文档内容
3. 在需要显示术语的地方使用 `#termgrid(category:"分类名")`
4. 系统会自动根据状态加载对应的数据和语言版本

## 总结

当前的 Typst 状态管理实现已经完全可用，提供了灵活的参数传递和状态管理机制，支持多语言和多数据源的术语文档生成。实现简洁高效，符合 Typst 的最佳实践。
