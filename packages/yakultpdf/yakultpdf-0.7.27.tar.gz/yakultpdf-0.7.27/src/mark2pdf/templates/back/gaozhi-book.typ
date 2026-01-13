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

// #import "./gaozhi-lib.typ": *
// #import "@preview/wordometer:0.1.5": word-count, total-words

#import "./gaozhi-lib.typ": *
#import "@preview/wordometer:0.1.5": word-count, total-words

// ========================================================================================
// MAIN CONF 

#let conf(
  title: none,
  subtitle: none,
  edition:none, 
  cover:none, 
  doc,
) = {

  set page(
    margin: (left: 2.5cm , right: 2.5cm,  top: 2.5cm, bottom: 2.5cm),  // 页边距设置
    fill: teal,
  )

  set page(margin: -1pt)
  if cover !=none {
    align(
      center, 
      image(cover, width: 100%, height: 100%, fit: "cover")
    )                    
  }



  set heading(numbering: "1.")
  show heading.where(level: 1): none    //会让目录二字也显示不出来

  set  text(
      font: "LXGW Wenkai Mono",           // 字体
      lang: "zh",           // 语言设置
      )

  //coverpage
  place(
    center + top,
    dy: 200pt,
    {
      text(size:6em,
          weight: "bold",
          fill: white,
        title
      )
      v(2em)
      text(size:4em,
          weight: "bold",
          fill: white,
        subtitle
      )
    }
  )
  
  place(
    right + top,
    dx: -40pt,
    dy: 40pt,
    text(fill: white, weight: "medium", 14pt, edition)
  )  

  // pagebreak()

  //outline page
  set page(
    fill: white,
  )
  set text(
      size: 1em,     // 字体大小调整
      weight: "regular"
  )


  set page(
    margin: (left: 5cm , right: 5cm,  top: 5cm, bottom: 5cm),  // 页边距设置
  )


  set par(spacing: 2em)
  pad(
    right: 20%,
    top: 20%,
    {
      set text(size: 1em,font:"FZFangsong-Z02S")
      text("目录",weight:"bold",size: 14pt)
      v(2em)

      set outline.entry(fill:none)
      show outline.entry.where(level: 1): set text(size: 14pt)  
      show outline.entry: set block(spacing: 2em)
      outline()
    }
  )



  show: word-count
  calligraphy-work(type: "Full")[#doc]

}  

#show: doc => conf(
$if(title)$
title: [$title$],
$endif$
$if(subtitle)$
subtitle: [$subtitle$],
$endif$
$if(pubinfo.edition)$
edition: [$pubinfo.edition$],
$endif$
$if(cover)$
cover: "$cover$",
$endif$
doc,
)

$body$              
