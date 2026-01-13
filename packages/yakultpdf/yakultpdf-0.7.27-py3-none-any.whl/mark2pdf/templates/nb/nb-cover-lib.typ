// nb-cover-lib.typ - Newsletter 封面库文件
// 提供封面页和封底页的创建函数，包含封面图片、标题、引用、出版信息等元素

//显示封面的图片
#let coverhero(hero-image: none) = {
  context {
    if hero-image == none { return }

    // Measure the image and text to find out the correct line width.
    // The line should always fill the remaining space next to the image. ---NO LINE
    let img = {
      set image(width: 14cm)
      hero-image.image
    }
    let cap = text(size: 25pt, fill: white, hero-image.caption)
    let img-size = measure(img)
    let text-width = measure(cap).width + 12pt
    let line-length = img-size.height - text-width

    grid(
      columns: (img-size.width, 1.5cm),
      column-gutter: 16pt,
      rows: img-size.height,
      img,
      grid(
        rows: (text-width, 1fr),
        move(dx: 16pt, rotate(
          90deg,
          origin: top + left,
          box(width: text-width, cap),
        )),
      ),
    )
  }
}

#let coverquote(description) = {
  box(inset: (x: 0.4em, y: 12pt), width: 100%, {
    grid(
      columns: (1em, auto, 1em),
      column-gutter: 12pt,
      rows: (1em, auto),
      row-gutter: 8pt,
      text(5em)["], line(start: (1.0em, 0.45em), length: 100%), none,

      none, text(1.2em, " "), none,
      none, text(1.2em, align(left, description)), none,
      // v(8pt) + align(right, text()[---#it.attribution]),
    )
  })
}

#let covertitle(
  title: none,
  titlefont: none,
) = {
  set text(font: titlefont, size: 24pt, tracking: -1pt, weight: "semibold", fill: rgb("#00008B"))
  block(
    height: 4em,
    width: 110%,
    par(
      leading: 0.5em,
      first-line-indent: 0em,
      align(left + horizon, text(title)),
    ),
  )
}

#let coverinfo(
  publication-info: none,
  date: none,
) = {
  set par(first-line-indent: 0em)
  set text(0.7em, fill: white)
  block({
    v(1fr) //位于页面底部
    move(dx: 20%, dy: 0%, [#publication-info #v(0.2em) #date])
  })
}

//创建封面页的函数
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
  // 设置首页面格式
  set page(
    width: 210mm,
    height: 297mm,
    margin: (left: 2.5cm, top: 2.5cm, right: 2.5cm, bottom: 2.5cm),
    header: none,
    background: place(right + top, rect(
      fill: red,
      height: 100%,
      width: 7.8cm,
    )),
  )

  set text(
    lang: "zh",
    font: font,
    size: 12pt,
    alternates: false,
  )

  grid(
    columns: (1fr, 7.8cm - 1.6cm - 18pt),
    column-gutter: 36pt,
    row-gutter: 32pt,

    // Title.
    covertitle(
      title: title,
      titlefont: titlefont,
    ),

    // Edition info.
    text(fill: white, weight: "medium", 14pt, align(right + top, edition)),

    // Hero image.
    coverhero(hero-image: hero-image),

    // Nothing next to the hero image.
    none,

    // cover quote
    coverquote(description), none,
  )

  place(
    bottom,
    dy: 1cm,
    grid(
      columns: (1fr, 7.8cm - 1.6cm - 18pt),
      column-gutter: 36pt,
      row-gutter: 32pt,
      //logo
      block(width: 3cm, logo),
      // publication info and date
      coverinfo(publication-info: publication-info, date: date),
    ),
  )
}
