// Adapted from Letter-size Pandoc-Typst layout template
// Original by John Maxwell, jmax@sfu.ca, July 2024
//
// This template is for Typst with Pandoc
// The assumption is markdown source, with a 
// YAML metadata block (title, author, date...)
//
// Usage:
//      pandoc myMarkdownFile.txt \
//      --wrap=none \
//      --pdf-engine=typst \
//      --template=simplePandocTypst.template  \
//      -o myBeautifulPDF.pdf

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
  let font = "Source Han Sans SC"  //Source Han Sans SC

  set page(
    paper: "us-legal",
    flipped: false,                         
    margin: (left: 3.5cm, top: 2.5cm, right: 3.5cm, bottom: 2.0cm),
    header: none,
    footer-descent: 30%,                  // 30 is default
    footer:  none,                             // A running footer: page numbers
    fill: teal,
    //   context {
    //     if counter(page).at(here()).first() > 0  [     // all pages 
    //         #set text(size: 9pt)
    //         #align(center)[
    //           #counter(page).display("1")
    //         ]
    //     ]
    //  },       
  )  

  // === BASIC BODY PARAGRAPH FORMATTING ===
  set par(
    first-line-indent: (amount: 0em, all: true),
    leading: 1.2em, 
    justify: false,
    spacing: 2.0em,
  )

  set text(
    lang: "zh",
    font: font,                          
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
  show quote: set pad(x: 2em, y: 2em)                 
  show quote: set par(
    leading: 1.2em,
    first-line-indent: 2em,  //不生效
  )
  show quote: set text(style: "normal")

//  set list(block: true)
  set list(
    indent: 1em,
    body-indent:1em, 
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
    inset: (left: 2em, top: 1.5em, right: 2em, bottom: 1.5em ),
    stroke: (0.5pt + rgb("#94c5e2")),
    radius: 4pt,
  )
  show raw: set text(fill: rgb("#116611"), size: 9pt) //green

  set heading(numbering: "1.")
  show heading.where(level: 1): it => {
    // 获取当前 heading 1 的计数，如果不是第一个 heading 1，添加分页符
    if counter(heading).get().first() > 1 [
      #pagebreak()
    ]
    align(center + horizon, block(above: 3.0em, below: 2.0em, width: 100% )[
      #set text(font: font, weight: "bold", size: 800pt, fill:white)
      #block(it.body) 
    ])
  }

  show heading.where(level: 2
    ): it => align(left, block(above: 3.0em, below: 2.0em, width: 100%)[
        #set text(font: font, weight: "semibold", size: 18pt, fill: rgb("#00008B"))
        #block(it.body) 
      ])

  show heading.where(level: 3
    ): it => align(left, block(above: 3.0em, below: 2.0em, width: 100%)[
        #set text(font: font, weight: "semibold", size: 13pt, fill: rgb("#00008B"))
        #block(it.body) 
      ])

  show heading.where(level: 4
    ): it => align(left, block(above: 3.0em, below: 2.0em, width: 100%)[
        #set text(font: font, weight: "semibold", size: 12pt, fill: rgb("#00008B"))
        #block(it.body) 
      ])

  // URLs
  show link: underline
  show link: set text(fill: navy)

  show regex("https://coinmarketcap.com/academy/glossary/.*"): set text(
    size: 10pt,
    fill: rgb("#444444"),
  )

  // ========== LAYOUT =========
  // HERE'S THE DOCUMENT LAYOUT

  // THIS IS THE ACTUAL BODY:
  v(2em)
  doc                                          // this is where the content goes
}  

#show: doc => conf(
  doc,
)

$body$              
