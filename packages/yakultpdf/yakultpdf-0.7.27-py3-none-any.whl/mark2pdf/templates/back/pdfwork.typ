// @ts-ignore
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

  //#pagebreak()
]

// ******************************************************************
// create-cover-page
// ******************************************************************
#let create-cover-page(
  cover: none,
  modulename: none,
  author: none,
  no_title_on_cover: false
) = {
    // 只有当封面存在时才执行
    if(cover == none ) { return }

    set page(margin: -1pt)

    align(center, image(cover, width: 100%, height: 100%, fit: "cover"))                    

    if no_title_on_cover == false {
      place(
        top + left,
        dy: 15%,
        pad(
          left: 15%, 
          right: 15%, 
          text(size: 50pt, weight: "bold", fill: white, font: "YouSHeBiaoTiHei")[#modulename]
        )
      )
      place(
        top + left,
        dy: 85%,
        pad(
          left: 15%, 
          right: 15%, 
          text(size: 30pt, weight: "semibold", fill: white, font: "YouSHeBiaoTiHei")[#author]
        )
      )
      
      // 封面图添加白色边框
      place(
        top + left,
        dx: 5%,
        dy: 3%,
        rect(
          width: 90%,
          height: 94%,
          stroke: (paint: white, thickness: 2pt),
          fill: none
        )
      )    
    }
    
    pagebreak()

    //设置会不出血版面
    //    set par(leading: 1.2em, first-line-indent: 2em)
    set page(margin: (left: 2.5cm, top: 2.5cm, right: 2.5cm, bottom: 2.5cm))
 
}


// ******************************************************************
// setpage
// ******************************************************************

// 函数抽取不行，暂时放回。


// ========================================================================================
// MAIN CONF 

#let conf(
  title: none,                              // SET BASIC TEMPLATE DEFAULTS:
  author: none,                             // IF NOT IN METADATA
  date:none,                                // IF NOT IN METADATA
  cover: none,                              // cover image path
  banner: none,                              // banner image path
  with_pagenumber: false,                   // 控制是否显示页码，运行时控制
  no_title_on_cover: false,                 // 控制是否在封面显示标题和作者，运行时控制
  doc,
) = {
  let font = "LXGW Wenkai Mono"  //Source Han Sans SC

  // 设置页面格式
//  setpage()
  // === PAGE ===
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
        if counter(page).at(here()).first() > 0 and with_pagenumber [     // all pages 
            #set text(size: 9pt)
            #align(center)[
              #counter(page).display("1")
            ]
        ]
     },     
  )  

  // === BASIC BODY PARAGRAPH FORMATTING ===
  set par(
    first-line-indent: (amount: 2em, all: true),
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
    indent: 2em,
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
  show raw: set block(inset: (left: 2em, top: 0.5em, right: 1em, bottom: 0.5em ))
  show raw: set text(fill: rgb("#116611"), size: 9pt) //green

  // Footnote formatting
  set footnote.entry(indent: 0.5em)
  show footnote.entry: set text(size: 10pt)
  //  show footnote.entry: set par(hanging-indent: 1em)

  // HEADINGS
  //  show heading: set text(hyphenate: false)

  show heading.where(level: 1
    ):  it => align(left, block(above: 3.0em, below: 2.0em, width: 100% )[
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
        //给 H3加图标，图片需位于 ./_working/in/star.png
        #box(image("./images/star.png", width: 1.0em, height: 1.0em)) #h(0.5em) #it.body  
      ])

  // URLs
  show link: underline
  show link: set text(fill: navy)

  //show <pagebreak>: set text(rgb("#777"))
  show <pagebreak>: {
    pagebreak()    
  }


  // ========== LAYOUT =========
  // HERE'S THE DOCUMENT LAYOUT

  // 封面图片：占满全页（包括边距）
  $if(cover)$
      create-cover-page(
        cover: cover,
        modulename: title,
        author: author,
        no_title_on_cover: no_title_on_cover
      )
  $endif$

  // 作者信息
  //$if(author)$
  //  align(left, [$author$])
  //  v(1em)
  //$endif$

  counter(page).update(1)                       // start page numbering

  $if(banner)$
    place(
        top + left,
        dx: -1%,
        dy: -12%,
        float: false,
        image(banner, width: 135%, height:40%, fit: "cover")
    )
    block( height: 30%, fill: none, )          //占位
  $endif$

  // THIS IS THE ACTUAL BODY:
  doc                                          // this is where the content goes
}  
// end of #let conf block
// ========================================================================================


// ========================================================================================
// BOILERPLATE PANDOC TEMPLATE:

#show: doc => conf(

  $if(title)$
    title: [$title$],
  $endif$

//  $if(subtitle)$
//    subtitle: [$subtitle$],
//  $endif$

  $if(author)$
    author: [$author$],
  $endif$

  $if(date)$
    date: [$date$],
  $endif$

  $if(cover)$
    cover: "$cover$",
  $endif$

  $if(banner)$
    banner: "$banner$",
  $endif$

  $if(with-pagenumber)$
    with_pagenumber: true,
  $endif$

  $if(no-title-on-cover)$
    no_title_on_cover: true,
  $endif$

//  $if(margin)$
//    margin: ($for(margin/pairs)$$margin.key$: $margin.value$,$endfor$),
//  $endif$

//  $if(papersize)$
//    paper: "$papersize$",
//  $endif$

  doc,


)
//end #show: doc

//$if(toc)$
//  #outline(
//    title: auto,
//    depth: none
//  );
//$endif$

//body 是什么作用？，注释掉，则不显示标题。正文正常。 $--才是注释！
$body$              

//$for(include-after)$
//  $include-after$
//$endfor$
