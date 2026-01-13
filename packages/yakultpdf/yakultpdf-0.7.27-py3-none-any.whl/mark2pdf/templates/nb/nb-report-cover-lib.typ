// nb-report-cover-lib.typ - Report 封面库文件
// 基于 nb-cover-lib.typ 修改，版式：
// 上方，标题
// 标题下：description
// 下方：heroimage (四周留空）
// 最下方，左侧：第一行，edition，第二行，publication-info
// 右侧：logo

#let covertitle(
  title: none,
  titlefont: none,
) = {
  set text(font: titlefont, size: 24pt, tracking: -1pt, weight: "semibold", fill: rgb("#00008B"))
  block(
    width: 100%,
    par(
      leading: 0.5em,
      first-line-indent: 0em,
      align(left, text(title)),
    ),
  )
}

// 创建封面页的函数
#let coverpage(
  title: none,
  author: none,
  edition: none,
  hero-image: none,
  description: none,
  publication-info: none,
  date: none,
  logo: none,
  font: none,
  titlefont: none,
  coverbg: none, // 保持接口一致，未使用
) = {
  set page(
    width: 210mm,
    height: 297mm,
    margin: (left: 2.5cm, top: 2.5cm, right: 2.5cm, bottom: 2.0cm),
    header: none,
    background: none,
  )

  set text(
    lang: "zh",
    font: font,
    size: 12pt,
    alternates: false,
  )

  // 1. 上方：标题 和 Description
  v(1cm)
  covertitle(title: title, titlefont: titlefont)

  if description != none {
    v(1em)
    block(width: 80%, text(size: 14pt, description))
  }

  // 2. 中间：Hero Image
  // 下方：heroimage (四周留空）
  if hero-image != none {
    v(1fr)
    align(center + horizon, pad(x: 0cm, y: 0cm, {
      set image(width: 100%)
      hero-image.image
    }))
    v(0.5fr)
  } else {
    v(1fr)
  }

  // 3. 最下方
  // 左侧：第一行，edition，第二行，publication-info
  // 右侧：logo
  place(bottom, {
    grid(
      columns: (1fr, auto),
      gutter: 1em,
      align: (left + bottom, right + bottom),
      {
        if edition != none {
          text(size: 14pt, weight: "bold", edition)
          linebreak()
        }
        if publication-info != none {
          publication-info
        }
      },
      if logo != none {
        move(dy: 1.5em, block(width: 5cm, logo))
      },
    )
  })
}
