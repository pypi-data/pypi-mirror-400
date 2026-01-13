// nb-lib.typ - Newsletter 主库文件
// 提供 newsletter 样式的文档模板，包含评论收集、浮动评论、全页面显示等功能

// 辅助函数：从 content 中提取纯文本字符串
// 因为当 pandoc 转换 ::: {#fullimage} 块时，内容不是简单的字符串，
// 而是一个 content 对象（sequence 类型），需要递归提取文本
// sep: 连接符，默认换行（用于 pagebg），单行内容用空字符串
#let content-to-string(content, sep: "\n") = {
  let result = if content.has("text") {
    content.text
  } else if content.has("children") {
    content.children.map(c => content-to-string(c, sep: sep)).join(sep)
  } else if content.has("body") {
    content-to-string(content.body, sep: sep)
  } else if content == [ ] {
    if sep == "" { "" } else { " " }
  } else {
    ""
  }
  // 统一处理 pandoc 转义：\_ -> _
  result.replace("\\_", "_")
}

// 状态：用于收集 comments，然后在结尾处显示
#let comments = state("comments", ())

// 遇到  comments 时，不是显示（没有返回显示元素），而是将之收集到  comments 状态中
#let comment(body) = comments.update(it => it + (body,))

#let floatc(body) = {
  // 创建一个浮动在右侧的comment box
  let float-box = rect(
    fill: rgb(255, 255, 255, 20%),
    inset: 1em,
    width: 5cm,
    {
      set par(
        leading: 0.9em,
        first-line-indent: 0em,
      )
      set image(width: 90%)
      body
    },
  )

  // 使用box函数创建不占据布局空间的容器，然后在这个容器内使用move函数

  // 使用 context 测量当前位置，确保不超出页面顶部
  context {
    // 获取当前位置
    let pos = here().position()

    // 获取页面顶部边距（从 page 设置中）
    let top-margin = 2.5cm // 根据你的 page 设置

    // 计算安全的向上偏移量
    // pos.y 是当前位置距页面顶部的距离
    // 确保偏移后不会超出顶部边距
    let safe-dy = calc.max(-pos.y + top-margin + 0.5cm, -4cm)

    // box(
    //   width: 0pt,
    //   height: 0pt,
    //   move(
    //     dx: 21cm - 8.5cm,
    //     dy: safe-dy,
    //     float-box
    //   )
    // )

    box(place(
      top + left,
      // scope: "parent",      // 相对整页（跨列）
      dx: 21cm - 8.5cm,
      dy: safe-dy,
      float-box,
    ))
    // sym.wj
    h(0pt, weak: true)
  }
}


#let endcomment(commentsarray) = {
  set text(size: 0.85em)
  set par(leading: 0.85em, first-line-indent: 0em)

  for element in commentsarray {
    element
    v(24pt, weak: true)
  }
}

#let fullpage(
  bottom: false,
  fill: rgb("#FFF5F5"),
  body,
) = {
  pagebreak()
  set page(fill: fill, background: none)
  if (bottom) {
    v(1fr)
    body
    v(4em)
  } else {
    body
  }
  pagebreak()
}

// 解析 fill= 配置的 fullpage
// 支持: default（默认粉色）, lightblue（浅蓝）, 任意颜色值如 #E4F6F6
// default-fill: 可通过 frontmatter 设置的默认颜色
#let fullpage-with-fill(body, raw-str, bottom: false, default-fill: none) = {
  let lines = raw-str.split("\n")
  // 根据 default-fill 参数确定初始颜色
  let fill-color = if default-fill == "lightblue" {
    rgb("#E4F6F6")
  } else if default-fill != none and default-fill != "default" {
    rgb(default-fill)
  } else {
    rgb("#FFF5F5") // 系统默认粉色
  }

  for line in lines {
    let trimmed = line.trim()
    if trimmed.starts-with("fill=") {
      let value = trimmed.slice(5).trim()
      if value == "default" {
        fill-color = rgb("#FFF5F5")
      } else if value == "lightblue" {
        fill-color = rgb("#E4F6F6")
      } else {
        fill-color = rgb(value)
      }
      break
    }
  }

  // 过滤掉 fill= 配置行
  show regex("fill=.+"): none

  fullpage(bottom: bottom, fill: fill-color, body)
}

// 整页图片：图片占满整页
// fit: "cover" 铺满裁切, "contain" 完整显示可能留白, "stretch" 拉伸变形
// bg: 背景色（图片留白时显示）
#let fullimage(
  img, // 图片路径
  fit: "contain", // cover/contain/stretch
  bg: white, // 背景色
) = {
  pagebreak(weak: true)
  set page(
    margin: 0pt,
    header: none,
    footer: none,
    fill: bg,
  )
  // 居中显示图片
  align(center + horizon, image(img, width: 100%, height: 100%, fit: fit))
  pagebreak(weak: true)
}
// 带背景图的内容页
// 语法：第一行 "bg=图片路径"，空行后是内容
// 示例：
//   ::: {#pagebg}
//   bg=images/bg.jpg
//
//   # 标题
//   内容...
//   :::
// 注意：body 是原始 content，raw-str 是纯文本（用于提取 bg= 配置）
#let pagebg-impl(body, raw-str, text-color: black) = {
  // 从纯文本中提取 bg= 配置
  let lines = raw-str.split("\n")
  let bg-image = none

  for line in lines {
    let trimmed = line.trim()
    if trimmed.starts-with("bg=") {
      bg-image = trimmed.slice(3).trim()
      break
    }
  }

  pagebreak()
  set page(
    background: if bg-image != none {
      image(bg-image, width: 100%, height: 100%, fit: "cover")
    } else {
      none
    },
  )
  set text(fill: text-color)
  // 覆盖标题颜色
  show heading: set text(fill: text-color)

  // 过滤掉 bg= 配置行，只显示其他内容
  // 遍历 body 的 children，跳过包含 bg= 的文本节点
  show regex("bg=.+"): none

  body
  pagebreak()
}

#let pagebg(body, raw-str) = pagebg-impl(body, raw-str, text-color: black)
#let pagebg-white(body, raw-str) = pagebg-impl(body, raw-str, text-color: white)

// 顶部出血图片（按图片原始比例显示）
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
        image(img, width: 100%),
      ),
    ),
  )
}

// 底部出血图片（按图片原始比例显示）
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
        image(img, width: 100%),
      ),
    ),
  )
  place.flush()
  pagebreak(weak: true)
}

#let nb(
  title: [Newsletter title],
  author: [Author],
  description: [Newsletter description], //显示于封面图下
  hero-image: none, //封面图，包括图片与说明
  edition: none, //系列信息显示于右上方
  publication-info: none, //出版物信息
  date: none,
  toc: false, //是否显示目录
  toc-depth: 3, //目录显示的缺省深度
  logo: none,
  font: none, //"LXGW Wenkai Mono"
  titlefont: none, //"YouSheBiaoTiHei"
  disable-indent: false,
  headerleft: none, //页眉左侧内容
  headerright: none, //页眉右侧内容（缺省 title）
  footerleft: none, //页脚左侧内容
  footerright: none, //页脚右侧内容
  watermark: none, //页面背景水印
  overview-fill: none, //overview 块的默认背景色
  disable-header: false, //是否隐藏页眉
  disable-pagenumber: false, //是否隐藏页码
  body,
) = {
  // Set document metadata.
  set document(title: title, description: description)

  // 设置缺省字体
  // let font = "LXGW Wenkai Mono"
  // let titlefont = "YouSheBiaoTiHei"

  // 设置页面格式
  set page(
    width: 210mm,
    height: 297mm,
    margin: (left: 2.5cm, top: 2.5cm, right: 6.0cm, bottom: 2.5cm),
    background: watermark,
    header: if disable-header {
      none
    } else {
      box(width: 100% + 3.5cm, {
        // 左侧显示 headerleft
        if headerleft != none {
          text(size: 0.7em, headerleft)
        }
        h(1fr)
        // 右侧显示 headerright，缺省 title
        if headerright != none {
          text(size: 0.7em, headerright)
        } else {
          text(size: 0.7em, title)
        }
      })
    },
    footer: context {
      if counter(page).at(here()).first() > 0 {
        set text(size: 9pt)
        box(width: 100% + 3.5cm, {
          grid(
            columns: (1fr, auto, 1fr),
            column-gutter: 0pt,
            align: (left, center, right),
            if footerleft != none {
              footerleft
            } else { [] },
            if not disable-pagenumber {
              move(dx: -1.75cm, counter(page).display("1"))
            } else { [] },
            if footerright != none {
              move(dx: 1.75cm, dy: -0.5cm, box(width: 5.5cm, footerright))
            } else { [] },
          )
        })
      }
    },
  )

  // Set the body font.
  set text(
    lang: "zh",
    font: font,
    size: 12pt,
    alternates: false,
  )

  // Configure headings.
  show heading: set text(font: font, weight: "semibold", fill: rgb("#00008B"))
  show heading.where(level: 1): it => {
    block(above: 3.0em, below: 2.0em, width: 100%, align(left, text(size: 20pt, it.body)))
  }
  show heading.where(level: 2): it => {
    block(above: 3.0em, below: 2.0em, width: 100%, align(left, text(size: 16pt, it.body)))
  }
  show heading.where(level: 3): it => {
    block(above: 3.0em, below: 2.0em, width: 100%, align(left, text(size: 14pt, it.body)))
  }

  show heading.where(level: 4): it => {
    block(above: 3.0em, below: 2.0em, width: 100%, align(left, text(size: 14pt, it.body)))
  }

  // set outline.entry(fill: none)

  set par(
    first-line-indent: if (disable-indent) { 0em } else { (amount: 2em, all: true) },
    leading: 1.2em,
    justify: false,
    spacing: 2.0em,
  )


  show quote: it => {
    set par(
      leading: 1.2em,
      first-line-indent: if (disable-indent) { 0em } else { (amount: 2em, all: true) },
    )

    block(
      above: 2em,
      below: 2em,
      fill: rgb("#E4F6F6"),
      breakable: true,
      radius: 0.5em,
      inset: 2em,
      it.body,
    )
  }

  show <quote>: it => {
    set par(
      leading: 1.2em,
      first-line-indent: if (disable-indent) { 0em } else { (amount: 2em, all: true) },
    )

    block(
      above: 2em,
      below: 2em,
      fill: rgb("#E4F6F6"),
      breakable: true,
      radius: 0.5em,
      inset: 2em,
      it.body,
    )
  }

  set list(
    indent: 2em,
    body-indent: 1em,
  )
  set enum(
    indent: 2em,
    body-indent: 1em,
  )

  // show table: set block(width: 120%)
  show table: set text(size: 10pt)
  show table: it => {
    block(
      width: 140%, // 或其他你需要的宽度
      move(
        dx: 15%,
        it,
      ),
    )
  }


  set image(width: 100%, fit: "contain")

  // Images and figures:
  show figure.caption: it => {
    text(size: 0.8em, it.body) //不显示前面的：“图片1”
  }

  // Code snippets:
  show raw: set block(inset: (left: 2em, top: 0.5em, right: 1em, bottom: 0.5em))
  show raw: set text(font: font, fill: rgb("#116611"), size: 9pt) //green

  // Footnote formatting
  set footnote.entry(indent: 0.5em)
  show footnote.entry: set text(size: 10pt)
  show footnote.entry: set block(width: 50%)

  // URLs
  show link: underline
  // show link: set text(size:10pt, fill: navy)

  show <overview>: it => fullpage-with-fill(it.body, content-to-string(it.body), default-fill: overview-fill)
  show <ending>: it => fullpage(bottom: true, it.body)
  show <fullimage>: it => fullimage(content-to-string(it.body, sep: "").trim())
  show <pagebg>: it => pagebg(it.body, content-to-string(it.body))
  show <pagebgwhite>: it => pagebg-white(it.body, content-to-string(it.body))
  show <topimage>: it => topimage-impl(content-to-string(it.body, sep: "").trim())
  show <bottomimage>: it => bottomimage-impl(content-to-string(it.body, sep: "").trim())

  //comment 集中显示于文档尾部，floatcomment 显示于右侧
  show <comment>: it => comment(it.body)
  show <floatcomment>: it => floatc(it.body)

  body

  // show comments at the end
  context {
    endcomment(comments.final())
  }
} //end of nb
