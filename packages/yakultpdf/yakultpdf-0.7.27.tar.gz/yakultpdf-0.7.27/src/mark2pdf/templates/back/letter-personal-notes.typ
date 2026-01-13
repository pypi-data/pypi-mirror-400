//用于处理来自 markdown 的 ---
#let horizontalrule = {
  v(2em)
  line(start: (5%,0%), end: (95%,0%), stroke: 1pt + black)
  v(2em)
}

//自定义函数，用于显示封面或封底
#let cover_or_back(
  title,
  author,
  date,
  version,
  iscover: false) = {
    set page(fill: teal)                          //仅在本函数生效
    set text(fill: white)

    if(iscover){
      v(3em)
      text(size:50pt, weight: "bold", title)
      v(1em)
      text(size:20pt, weight:"bold", author)
    }
  
    v(1fr)  
    grid(
      columns: (auto, 1fr, auto), 
      text(size:12pt, date),
      [], 
      text(size:12pt, version)
    )

    if iscover {
      pagebreak()
    }
}

#let myfooter = {
  context {
    let page-num = counter(page).at(here()).first()
    let total-pages = counter(page).final().first()
    if page-num > 1 and page-num < total-pages  {     // exclude first and last page
      set text(size: 9pt)
      align(center)[#counter(page).display("1")]
    }
  }
}

// ========================================================================================
// MAIN CONF 

#let conf(
  title: none,
  author: none,
  date: none,
  version: none,
  doc,
) = {
  let defaultfont = ("Helvetica","LXGW Wenkai") //"Source Han Sans SC"
  // let codefont = "Consolas"
  set page(
    paper: "us-legal",
    flipped: false,                         
    margin: (left: 3.5cm, top: 2.5cm, right: 3.5cm, bottom: 2.0cm),
    header: none,
    footer-descent: 30%,                  // 30 is default
    footer: myfooter                              // A running footer: page numbers
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
    font: defaultfont,                          
    size: 13pt,
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
    first-line-indent: { 0em },  //不生效
  )
  show quote: set text(style: "normal")

  show <quote>: it =>{
    set par(
        leading: 1.2em,
        first-line-indent: { 0em } ,
    )

    block(
      above: 2em,
      below: 2em,
      fill: rgb("#E4F6F6"),
      breakable: true,
      radius: 0.5em,
      inset: 2em,
      it.body
    )
  } 

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

  // show raw: set text(font:(codefont,defaultfont),size:14pt) 
  show raw: set text(font:defaultfont,size:13pt) 

  // show raw.where(block: true): set par(leading: 0.7em)
  show raw: set block(
    width: 100%,
    inset: (left: 1em, top: 0.50em, right: 1em, bottom: 0.5em ),
    stroke: (left: 1pt + rgb("#94c5e2")),
    // radius: 4pt,
  )
  show raw.where(block: true): set text(size:11pt)
  // show raw.where(block: true): set par(leading:10pt)

  // set heading(numbering: "1.")

  show heading.where(level: 1): it => {
    // heading 1 前面添加分页符
    pagebreak()

    set text(weight: "bold", size: 24pt, fill:rgb("#00008B"))
    block(above: 3.0em, below: 2.0em, width: 100%,
      // counter(heading).display() + " " + it.body
      it.body
    )
  }

  show heading.where(level: 2): it =>{
    set text(weight: "semibold", size: 18pt, fill: rgb("#00008B"))
    block(above: 3.0em, below: 2.0em, width: 100%, 
      // counter(heading).display() + " " + it.body)
      it.body)
  }

  show heading.where(level: 3): it =>{
    set text(weight: "semibold", size: 13pt, fill: rgb("#00008B"))
    block(above: 3.0em, below: 2.0em, width: 100%, it.body)
  }

  show heading.where(level: 4): it =>{
    set text(weight: "semibold", size: 13pt, fill: rgb("#00008B"))
    block(above: 3.0em, below: 2.0em, width: 100%, it.body)
  }

  // set heading(numbering: "1.")
  set outline.entry(fill:none)

  // URLs
  show link: underline
  show link: set text(fill: navy, size:11pt)

  show regex("https://.*"): set text(size: 11pt, fill: navy)

  // 处理长字符串（超过40个字符且仅包含数字和字母或=）
  show regex("[a-zA-Z0-9=]{41,}"): set text(size: 8pt)

  // ========== LAYOUT =========
  // HERE'S THE DOCUMENT LAYOUT

  cover_or_back(title, author, date, version, iscover: true)

  text("目录")
  outline(depth:2, title: none)
  // pagebreak()

  doc                                          // this is where the content goes
  
  cover_or_back(title, author, date, version)
}

#show: doc => conf(
$if(title)$
title: [$title$],
$endif$
$if(author)$
author: [$author$],
$endif$
$if(date)$
date: [$date$],
$endif$
$if(version)$
version: [$version$],
$endif$
doc,
)

$body$              
