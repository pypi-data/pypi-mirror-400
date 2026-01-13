
// 前置流程组合页面时，每页间增加了“---”
#let horizontalrule = {
  pagebreak()
}

#let sectioncover(titlealpha)={
  
  set page(fill: teal)

  place(center+horizon, text(
    size:500pt, 
    weight:"bold", 
    fill:white, 
    titlealpha))
    
  pagebreak()
  set page(fill: white)
  outline(depth: 1)
  pagebreak()

}

#let termtag(tag)={
place(
    top + right, 
    dx: -0.5em,  
    dy: 0.0em, 
    block(
        outset: 0.2em,inset: 0.2em,
        radius: 0.2em,
        fill: navy,
        text(white, size:8pt, tag) 
    )
  )
}

#let conf(
  section: none,
  doc,
) = {
  let font = "Source Han Sans SC"  //Source Han Sans SC

  set page(
    paper: "us-legal",
    flipped: false,
    margin: (left: 1cm, top: 1.5cm, right: 1cm, bottom: 2.0cm),
    header: none,
    footer-descent: 30%,                  // 30 is default
    footer:                               // A running footer: page numbers
      context {
        if counter(page).at(here()).first() > 2  [     // all pages 
            #set text(size: 9pt)
            #align(center)[
              #counter(page).display("1")
            ]
        ]
     },       
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
    size: 19pt,
    alternates: false,
  )

  set smartquote(enabled: false)

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

  show outline: it => {
    columns(2, it)
  }
  show outline: set text(size:14pt)
  set outline.entry(fill: none)


  // Code snippets:
  show raw: set block(
    width: 90%,
    inset: (left: 2em, top: 1.5em, right: 2em, bottom: 1.5em ),
    stroke: (0.5pt + rgb("#94c5e2")),
    radius: 4pt,
  )
  show raw: set text(font:font,fill: rgb("#116611"), size: 9pt) //green

  set heading(numbering: "1.")
  show heading.where(level: 1): it => {
    // 获取当前 heading 1 的计数，如果不是第一个 heading 1，添加分页符
    // if counter(heading).get().first() > 1 [
    //   #pagebreak()
    //   #v(1.0em)
    // ]
    
    align(left, block(above: 3.0em, below: 2.0em, width: 100% )[
      #set text(font: font, weight: "bold", size: 24pt, fill:rgb("#00008B"))
      #block(it.body)
    ])
  }

  show heading.where(level: 2
    ): it => align(left, block(above: 3.0em, below: 2.0em, width: 100%)[
        #set text(font: font, weight: "semibold", size: 20pt, fill: rgb("#00008B"))
        #block(it.body) 
      ])

  show heading.where(level: 3
    ): it => align(left, block(above: 2.5em, below: 2.0em, width: 100%)[
        #set text(font: font, weight: "semibold", size: 19pt, fill: rgb("#00008B"))
        #block(it.body) 
      ])

  show heading.where(level: 4
    ): it => align(left, block(above: 2.5em, below: 2.0em, width: 100%)[
        #set text(font: font, weight: "semibold", size: 19pt, fill: rgb("#00008B"))
        #block(it.body) 
      ])

  // URLs
  show link: underline
  show link: set text(fill: navy)

  show regex("https://coinmarketcap.com/academy/glossary/.*"): it => {
    v(1fr)
    text(size: 8pt, fill: rgb("#444444"),it)
  }

  // 处理长字符串（超过40个字符且仅包含数字和字母）
  show regex("[a-zA-Z0-9]{41,}"): set text(size: 8pt)
  show regex("[a-zA-Z0-9]{41,}"): set text(fill: navy)

  // 处理说明文字（括号内以"说明："开头）
  show regex("[（(]说明：[^）)]*[）)]"): set text(fill: aqua)



  // ========== LAYOUT =========
  // HERE'S THE DOCUMENT LAYOUT

  // THIS IS THE ACTUAL BODY:

  if(section !=none){
    if(section=="1"){
      sectioncover("#")
    }else{
      sectioncover(section)
    }
  }

  doc                                          // this is where the content goes
}  

#show: doc => conf(
  doc,
$if(section)$
section: "$section$",
$endif$
)

$body$              
