// Math Exercise Template with 2 columns and practice space
// Based on letter.typ template
// For use with md2pdf.py

#let horizontalrule = [
  #v(2em)
  #line(start: (5%,0%), end: (95%,0%), stroke: 1pt + black)
  #v(2em)
]

// ========================================================================================
// MAIN CONF 

#let conf(
  doc,
) = {
  let font = "Source Han Sans SC"

  set page(
    paper: "a4",
    flipped: false,                         
    margin: (left: 1.0cm, top: 1.5cm, right: 1.0cm, bottom: 1.5cm),
    header: none,
    footer-descent: 30%,
    footer:
      context {
        // if counter(page).at(here()).first() > 0 [
        //     #set text(size: 9pt)
        //     #align(center)[
        //       #counter(page).display("1")
        //     ]
        // ]
     },       
  )  

  // === BASIC BODY PARAGRAPH FORMATTING ===
  set par(
    first-line-indent: 0em,
    leading: 0.8em, 
    justify: false,
    spacing: 0em,  // 紧凑间距
  )

  set text(
    lang: "zh",
    font: font,                          
    size: 11pt,
    alternates: false,
  )

  set smartquote(enabled: false)

  // Math equation settings
  set math.equation(numbering: none)
  
  // 创建题号计数器
  let question-counter = counter("question")
  question-counter.step()
  question-counter.step()
  question-counter.step()
  question-counter.step()  
  question-counter.step()

  // 使用 show 规则为每个 display 数学公式添加间距和练习空间，并自动编号
  show math.equation.where(block: true): it => {
    // 在公式前添加题号，后面添加练习空间
    block(
      width: 100%,
      spacing: 0em,
      [
        #question-counter.step()
        #grid(
          columns: (auto, 1fr),
          column-gutter: 0.8em,
          align: (left, left),
          [#question-counter.display().],
          it
        )
        #v(9em)  // 练习空间高度
      ]
    )
  }

  // Block quotations
  set quote(block: true)
  show quote: set block(
    spacing: 1em, 
    fill: rgb("#E4F6F6"), 
    breakable: false, 
    radius: 0.5em
  )
  show quote: set pad(x: 1em, y: 1em)
  show quote: set par(leading: 1.0em)
  show quote: set text(style: "normal")

  set list(
    indent: 0.8em,
    body-indent: 0.8em, 
  )

  // Images and figures:
  set image(width: 100%, fit: "contain")
  show image: it => {
    align(center, it)
  }
  set figure(gap: 0.5em, supplement: none)
  show figure.caption: set text(size: 9pt) 

  // Code snippets:
  show raw: set block(
    width: 90%,
    inset: (left: 1em, top: 1em, right: 1em, bottom: 1em),
    stroke: (0.5pt + rgb("#94c5e2")),
    radius: 4pt,
  )
  show raw: set text(fill: rgb("#116611"), size: 9pt)

  set math.equation(block: true, numbering: none)
  show math.equation: set align(left)

  // 标题设置（简化版，数学题通常不需要复杂标题）
  set heading(numbering: "1.")
  show heading.where(level: 1): it => {
    if counter(heading).get().first() > 1 [
      #pagebreak()
    ]
    align(left, block(above: 2.0em, below: 1.5em, width: 100%)[
      #set text(font: font,  size: 16pt, fill: rgb("#00008B"))
      #block(it.body) 
    ])
  }

  show heading.where(level: 2): it => {
    align(left, block(above: 2.0em, below: 1.5em, width: 100%)[
      #set text(font: font,  size: 14pt, fill: rgb("#00008B"))
      #block(it.body) 
    ])
  }

  show heading.where(level: 3): it => {
    align(left, block(above: 1.5em, below: 1.0em, width: 100%)[
      #set text(font: font,  size: 12pt, fill: rgb("#00008B"))
      #block(it.body) 
    ])
  }

  // URLs
  show link: underline
  show link: set text(fill: navy)

  // ========== LAYOUT =========
  // 两栏布局
  columns(2, gutter: 1.0em, doc)
}  

#show: doc => conf(
  doc,
)

$body$              

