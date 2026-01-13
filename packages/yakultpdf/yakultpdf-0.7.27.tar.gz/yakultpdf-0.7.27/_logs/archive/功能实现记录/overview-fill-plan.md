# Overview 底色功能

## 目标
为 `overview` 标签增加底色配置功能，参考 `pagebg` 的实现方式。

## 当前状态
- `overview` 调用 `fullpage`，固定使用 `fill: rgb("#FFF5F5")`（浅粉色）
- 无法在 Markdown 中指定底色

## 设计方案

### 使用语法（Markdown 中）
```markdown
::: {#overview}
内容...
:::

::: {#overview}
fill=lightblue

内容...
:::

::: {#overview}
fill=#E4F6F6

内容...
:::
```

### 底色选项
1. **default** - 默认浅粉色 `#FFF5F5`
2. **lightblue** - 浅蓝色 `#E4F6F6`
3. **任意值** - 如 `#AABBCC` 等十六进制颜色

### 实现思路

1. 修改 `fullpage` 函数，增加 `fill` 参数：
   ```typst
   #let fullpage(
     bottom: false,
     fill: rgb("#FFF5F5"),  // 默认值
     body,
   ) = { ... }
   ```

2. 新增 `fullpage-with-fill` 函数解析 `fill=` 配置：
   ```typst
   #let fullpage-with-fill(body, raw-str, bottom: false) = {
     // 从 raw-str 提取 fill= 配置
     // 支持 default / lightblue / 任意颜色值
     // 调用 fullpage(fill: 解析后的颜色, ...)
   }
   ```

3. 颜色解析逻辑：
   - 无 fill= → 默认 `#FFF5F5`
   - fill=default → `#FFF5F5`
   - fill=lightblue → `#E4F6F6`
   - fill=#XXXXXX → 使用该颜色

4. 修改 `show <overview>` 规则：
   ```typst
   show <overview>: it => fullpage-with-fill(it.body, content-to-string(it.body))
   ```
