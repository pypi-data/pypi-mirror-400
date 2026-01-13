# Typst 状态管理调研总结

## 问题
在 `term-doc` 设置状态，在 `termgrid` 里面可以获取 state 吗？

## 答案
**是的，可以在 `term-doc` 设置状态，在 `termgrid` 里面获取状态。**

## 调研结果

### 1. Typst 状态管理基本语法
```typst
// 创建状态
#let my-state = state("key", initial-value)

// 更新状态（在函数内部不需要 # 前缀）
my-state.update(new-value)

// 获取状态（需要 context）
#let current-value = context my-state.get()

// 获取最终状态
#let final-value = context my-state.final()
```

### 2. 状态在函数间传递的工作原理
- 状态是全局的，可以在任何地方访问
- 状态更新按文档布局顺序进行，不是按代码执行顺序
- 状态更新必须在文档内容中才能生效

### 3. 实际测试验证
我们创建了测试文件验证了以下功能：

#### 基本状态操作测试
```typst
#let s = state("x", 0)
#let compute(expr) = [
  #s.update(x => eval(expr.replace("x", str(x))))
  [New value is #context s.get().]
]
```

#### term-doc 和 termgrid 状态传递测试
```typst
// 创建状态
#let category-state = state("current-category", "none")

// 在 term-doc 中设置状态
#let term-doc-with-state(body) = {
  // 设置初始状态
  category-state.update("document-started")
  body
}

// 在 termgrid 中获取和更新状态
#let termgrid-with-state(category: none) = [
  // 获取当前状态
  #let current-state = context category-state.get()
  
  // 更新状态
  category-state.update(category)
  
  // 显示状态信息
  Current state: #current-state, Processing category: #category
]
```

### 4. 关键语法要点
1. **状态更新语法**：在函数内部调用 `state.update()` 时，前面**不需要** `#` 前缀
2. **状态获取语法**：使用 `context state.get()` 获取当前状态值
3. **状态作用域**：状态是全局的，可以在任何函数中访问

### 5. 实际应用场景
- 跟踪当前处理的分类
- 记录文档处理进度
- 在多个组件间共享状态信息
- 实现跨函数的状态管理

## 结论
Typst 的状态管理系统完全支持在 `term-doc` 中设置状态，在 `termgrid` 中获取状态。状态是全局的，可以在文档的任何地方访问和更新，这为复杂的文档处理逻辑提供了强大的支持。
