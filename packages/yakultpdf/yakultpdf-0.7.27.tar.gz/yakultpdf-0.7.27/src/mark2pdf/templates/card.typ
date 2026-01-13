
#let horizontalrule = {
  pagebreak()
}

// ==========================MAIN CONF=================================
#let conf(
  title: none,            //文章标题
  logo-image: none,       //logo图（显示于页眉右侧）
  footer-image: none,     //页脚右侧图片
  bg: none,               //背景图片路径
  theme: "light",         //主题："light" 或 "dark"，dark 模式下文字反白
  doc,                  
) = {
  let font = ("Helvetica", "LXGW Wenkai")

  set text(
    lang: "zh",
    font: font,
    size: 13pt,
    alternates: false,
  )

  set par(
    first-line-indent: 0em,
    leading: 1.2em,
    justify: false,
    spacing: 1.4em,
  ) 

  // 根据 theme 设置文字颜色
  let text-color = if theme == "dark" { white } else { black }
  let heading-color = if theme == "dark" { white } else { rgb("#00008B") }

  // 页面设置
  set page(
    width: 210mm,
    height: 297mm,
    margin: (left: 3.5cm, top: 4.0cm, right: 3.5cm, bottom: 6.0cm),
    // 背景图
    background: if bg != none {
      image(bg, width: 100%, height: 100%, fit: "cover")
    } else { none },
    // 页眉：logo 居中
    header: {
      if logo-image != none {
        align(center, image(logo-image, height: 2.0cm, fit: "contain"))
      }
    },
    // 页脚：右侧图片
    footer: context {
      if counter(page).at(here()).first() > 0 {
        set text(size: 9pt, fill: text-color)
        grid(
          columns: (auto, 1fr, auto),
          column-gutter: 0pt,
          [],  // 左侧空占位
          [],  // 中间空白
          // 右侧图片（用 move 推到边距区域）
          if footer-image != none {
            move(dx: 6.0cm, dy: -0.5cm, image(footer-image, height: 1.8cm, fit: "contain"))
          } else { [] },
        )
      }
    },
  )

  // 正文文字颜色
  set text(fill: text-color)

  // 标题样式
  show heading: set text(font: font, weight: "semibold", fill: heading-color)
  show heading.where(level: 1): it => {
    block(above: 2.0em, below: 2.5em, text(size: 19pt, it.body))
  }
  show heading.where(level: 2): it => {
    block(above: 2.0em, below: 1.0em, text(size: 16pt, it.body))
  }

  // 图片默认宽度
  set image(width: 100%, fit: "contain")

  // 图片说明
  show figure.caption: it => {
    text(size: 0.8em, it.body)
  }

  // ==================== pagebg 支持 ====================
  // 辅助函数：从 content 中提取纯文本字符串
  let content-to-string(content, sep: "\n") = {
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
    result.replace("\\_", "_")
  }

  // 带背景图的内容页实现
  let pagebg-impl(body, raw-str, text-color: black) = {
    let lines = raw-str.split("\n")
    let bg-image = none
    for line in lines {
      let trimmed = line.trim()
      if trimmed.starts-with("bg=") {
        bg-image = trimmed.slice(3).trim()
        break
      }
    }
    pagebreak(weak: true)
    set page(
      background: if bg-image != none {
        image(bg-image, width: 100%, height: 100%, fit: "cover")
      } else { none },
    )
    set text(fill: text-color)
    show heading: set text(fill: text-color)
    show regex("bg=.+"): none
    body
    pagebreak(weak: true)
  }

  let pagebg(body, raw-str) = pagebg-impl(body, raw-str, text-color: black)
  let pagebg-white(body, raw-str) = pagebg-impl(body, raw-str, text-color: white)

  // 注册 pagebg 标签
  show <pagebg>: it => pagebg(it.body, content-to-string(it.body))
  show <pagebgwhite>: it => pagebg-white(it.body, content-to-string(it.body))

  doc
}


// ========================PANDOC TEMPLATE=============================
// Note：这是一个对 conf 函数的调用
// 以下是 pandoc 模板，不是语法错误！！！！ 
#show: doc => conf(
$if(title)$
title: [$title$],
$endif$
$if(logo-image)$
logo-image: "$logo-image$",
$endif$
$if(footer-image)$
footer-image: "$footer-image$",
$endif$
$if(bg)$
bg: "$bg$",
$endif$
$if(theme)$
theme: "$theme$",
$endif$
doc,
)

$body$