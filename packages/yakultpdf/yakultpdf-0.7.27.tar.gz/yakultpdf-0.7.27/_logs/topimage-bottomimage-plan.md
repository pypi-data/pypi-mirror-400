# nb-lib 新增 `<topimage>` 和 `<bottomimage>` 语法方案

## 需求
- `<topimage>`: 顶部出血图片，自动分页后放置
- `<bottomimage>`: 底部出血图片，放在当前页底部，后续内容换页

## 分页策略

| 语法 | 行为 |
|------|------|
| topimage | `pagebreak()` → 图片放新页顶部出血 |
| bottomimage | 图片浮动到当前页底部出血 → `place.flush()` → `pagebreak()` |

## 代码实现

```typst
// 顶部出血图片
#let topimage-impl(img) = {
  pagebreak(weak: true)
  place(
    top,
    float: true,
    clearance: 1em,
    move(
      dx: -2.5cm,
      dy: -2.5cm,
      box(
        width: 21cm,
        height: 10cm,  // 固定高度
        clip: true,
        image(img, width: 100%, height: 100%, fit: "cover")
      )
    )
  )
}

// 底部出血图片（方案C）
#let bottomimage-impl(img) = {
  place(
    bottom,
    float: true,
    clearance: 1em,
    move(
      dx: -2.5cm,
      dy: 2.5cm,
      box(
        width: 21cm,
        height: 10cm,  // 固定高度
        clip: true,
        image(img, width: 100%, height: 100%, fit: "cover")
      )
    )
  )
  place.flush()       // 确保浮动元素就位
  pagebreak(weak: true)  // 后续内容换页
}
```

## Show 规则

```typst
show <topimage>: it => topimage-impl(content-to-string(it.body, sep: "").trim())
show <bottomimage>: it => bottomimage-impl(content-to-string(it.body, sep: "").trim())
```

## 用户语法（简化，无参数）

```markdown
::: {#topimage}
images/header.jpg
:::

正文内容...

::: {#bottomimage}
images/footer.jpg
:::
```

## 页面设置参考

```typst
margin: (left: 2.5cm, top: 2.5cm, right: 6.0cm, bottom: 2.5cm)
```
