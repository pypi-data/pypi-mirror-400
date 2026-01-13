// Wensi Features 文思作文专题
// 特别说明：不可以用 --- 作为分页，因它被用于作为空行
// 分页逻辑要额外处理

#let global-cover = state("global-cover", none)

#let horizontalrule = {
  v(2em)
  line(start: (5%,0%), end: (95%,0%), stroke: 1pt + black)
  v(0em)
}

//=================== create-cover-page =======================
#let create-cover-page(
  cover: none,
  title: none,
  author: none,
  no_title_on_cover: false
) = {
    if(cover == none ) { return }

    set page(margin: -1pt)
    set page(background: image(cover,width: 100%, height: 100%, fit: "cover"))
    set par(leading: 0.8em)

    if no_title_on_cover == false {
      block(
        width: 100%, height: 100%,
        inset: (left: 15%, right: 10%, top:15%, bottom: 10%),
        align(center, {
          text(size: 50pt, weight: "bold", fill: white, font: "YouSHeBiaoTiHei")[#title]
          v(1fr)
          text(size: 30pt, weight: "semibold", fill: white, font: "YouSHeBiaoTiHei")[#author]
        })
      )

      // 封面图添加白色边框
      place(
        top + left,  dx: 5%, dy: 3%,
        rect(
          width: 90%,
          height: 94%,
          stroke: (paint: white, thickness: 2pt),
          radius: 10pt,
          // fill: none
        )
      )    
    }

    place(
        bottom + left, dx: 30pt, dy: -10pt,
        text(fill: white, size: 8pt, "© 张华中小学分级作文")
    )

    pagebreak()
}

//=================== create-section-page =======================
#let create-section-page(
  modulename: none,
  title: none,
  section_number: none
) = {
  context {
    let cover = global-cover.get()  
    if(cover == none ) { return}

    set page(margin: -1pt)
    set page(background: image(cover,width: 100%, height: 100%, fit: "cover"))
    set par(leading: 0.8em)

    // 添加白色边框和蓝色填充
    place(
        top + left, dx: 5%, dy: 3%,
        rect(
          width: 90%,
          height: 94%,
          stroke: (paint: white, thickness: 2pt),
          fill: rgb(255, 255, 255, 15%),
          radius: 10pt
        )
    )    

    block(
      width: 100%, height: 100%,
      inset: (left: 15%, right: 10%, top:15%, bottom: 10%),
      {
        text(size: 50pt, weight: "bold", fill: white, font: "YouSHeBiaoTiHei")[#modulename]
        grid(
          columns: (16%, 84%),
          fill: rgb(0, 0, 0, 20%),
          rect(
            width: 60pt, height: 60pt, radius: 5pt,
            fill: blue,
            align(center+horizon,
              text(size: 60pt, weight: "bold", fill: white, font: "YouSHeBiaoTiHei")[#section_number]
            )
          ),
          align(
            left+horizon,
            text(size: 24pt, weight: "bold", fill: white, font: "YouSHeBiaoTiHei")[#title]
          )
        )
      }
    )

    pagebreak()
  }
}

// =============================================
// MAIN CONF - this block goes almost to the end of this file

#let conf(
  // modulename: none,                         // module name for cover
  title: none,                              // SET BASIC TEMPLATE DEFAULTS:
  // subtitle: none,
  author: none,                             // IF NOT IN METADATA
  // date:none,                                // IF NOT IN METADATA
  cover: none,                              // cover image path
  // sectionnumbering: none,
  // section_number: none,
  no_page_numbers: false,                   // 控制是否显示页码，运行时控制
  no_title_on_cover: false,                 // 控制是否在封面显示标题和作者，运行时控制
  doc,
) = {
  let font = "Source Han Serif SC"  //Sans

  global-cover.update(cover)

  // 设置页面格式
  set page(
    width: 210mm,
    height: 297mm,
    flipped: false,                       // if true = flips to landscape format,   
    margin: (left: 2.5cm, top: 2.5cm, right: 2.5cm, bottom: 2.5cm),
  
    // Header and Footer
    header:                               // A running head: document title
      context {},
    footer-descent: 30%,                  // 30 is default
    footer:                               // A running footer: page numbers
      context {
        if counter(page).at(here()).first() > 0 [     // all pages 
          #if not no_page_numbers [
            #set text(size: 9pt)
            #align(center)[
              // #if counter(page).at(here()).first() == 1 [#date]
              #h(1fr)
              #counter(page).display("1")
            ]
          ]
        ]
     },     
  )  // END set page

  // === BASIC BODY PARAGRAPH FORMATTING ===
  set par(
    first-line-indent: 2em,
    leading: 1.2em, 
    justify: false,
    spacing: 2.0em,
  )

  set text(lang: "zh",
    font: font,                          // set on line 31 above
    size: 12pt,
    alternates: false,
  )

  // Block quotations
  set quote(block: true)
  show quote: set block(
    spacing: 2em, 
    fill: rgb("#E4F6F6"), 
    breakable: false, 
    radius: 0.5em
  )
  show quote: set pad(x: 2em, y: 2em)                 // L&R margins
  show quote: set par(
    leading: 1.2em,
    first-line-indent: 2em
  )
  show quote: set text(style: "normal")

  // Images and figures:
  set image(width: 5.25in, fit: "contain")
  show image: it => {
    align(center, it)
  }
  set figure(gap: 0.5em, supplement: none)
  show figure.caption: set text(size: 9pt) 

  // Code snippets:
  show raw: set block(inset: (left: 2em, top: 0.5em, right: 1em, bottom: 0.5em ))
  show raw: set text(fill: rgb("#116611"), size: 9pt) //green

  // Footnote formatting
  set footnote.entry(indent: 0.5em)
  show footnote.entry: set par(hanging-indent: 1em)
  show footnote.entry: set text(size: 10pt)

  // HEADINGS
  show heading: set text(hyphenate: false)

  show heading.where(level: 1
    ):  it => align(left, block(above: 3.0em, below: 2.0em, width: 100% )[
        #set par(leading: 5em)
        #set text(font: font, weight: "semibold", size: 20pt, fill:rgb("#00008B"))
        #block(it.body) 
      ])

  show heading.where(level: 2
    ): it => align(left, block(above: 3.0em, below: 2.0em, width: 100%)[
        #set text(font: font, weight: "semibold", size: 18pt, fill: rgb("#00008B"))
        #block(it.body) 
      ])

  show heading.where(level: 3
    ): it => align(left, block(above: 2.0em, below: 2.0em, width: 100%)[
        #set text(font: font, weight: "semibold", size: 16pt)
        #box(image("wensi-tpl/star.png", width: 1.0em, height: 1.0em)) #h(0.5em) #it.body
      ])

  // URLs
  show link: underline
  show link: set text(fill: navy)

// =================== LAYOUT =====================
// HERE'S THE DOCUMENT LAYOUT
  // 封面图片：占满全页（包括边距）
  if(cover!=none){
    create-cover-page(
        cover: cover,
        title: title,
        author: author,
        no_title_on_cover: no_title_on_cover
    )
  }
  
  // set outline.entry(fill:none)
  show outline: set text(size:10pt)
  show outline.entry: it =>{
    it.indented(
      it.prefix(),
      if it.level == 1 {  // 一级标题：保留默认内部内容（包括页码）
        it.inner()
      } else {            // 二级及以上标题：仅显示标题内容，不显示填充和页码
        it.body()
      }
    )
  }

  //outline
  {
    set par(leading: 0.8em)
    outline(depth: 3)
  }

  // THIS IS THE ACTUAL BODY:
  doc

  // back cover
  pagebreak()
  {
    set page(fill:navy)
    set text(white)
    v(1fr)
    text("© 张华中小学分级作文")
  }
}  // end of #let conf block


// =============================================
// BOILERPLATE PANDOC TEMPLATE:

#show: doc => conf(
$if(title)$
title: [$title$],
$endif$
$if(author)$
author: [$author$],
$endif$
$if(cover)$
cover: "$cover$",
$endif$
$if(no-page-numbers)$
no_page_numbers: true,
$endif$
$if(no-title-on-cover)$
no_title_on_cover: true,
$endif$
doc,
)

$body$
