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
//     -o myBeautifulPDF.pdf

#let create-cover-page(
  cover: none,
  title: none,
  author: none,
  no_title_on_cover: false
) = {
    // 只有当封面存在时才执行
    if(cover == none ) {
      return
    }

    set page(margin: -1pt)

    //fit parameters: cover contain stretch
    align(center, image(cover, width: 100%, height: 100%, fit: "cover"))                    
    set par(leading: 0.8em)

    if no_title_on_cover == false {
      place(
        top + center,
        dy: 15%,
        pad(
          left: 15%, 
          right: 15%, 
          text(size: 50pt, weight: "bold", fill: white, font: "YouSHeBiaoTiHei")[#title]
        )
      )
      place(
        top + center,
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
    set par(leading: 1.5em)
    set page(margin: (left: 2.5cm, top: 2.5cm, right: 2.5cm, bottom: 2.5cm))
 
}


#let setpage()={
  // === PAGE ===
  set page(
    width: 210mm,
    height: 297mm,
    flipped: false,                       // if true = flips to landscape format,   
    margin: (left: 2.5cm, top: 2.5cm, right: 2.5cm, bottom: 2.5cm),
  
    // Header and Footer
    header:                               // A running head: document title
      context {
        //        if counter(page).at(here()).first() > 1 [    // after page 1
        //           #set text(size: 10pt, style: "italic")
        //           #align(right)[#title]
        //        ]
    },
    footer-descent: 30%,                  // 30 is default
    footer:                               // A running footer: page numbers
      context {
        if counter(page).at(here()).first() > 0 [     // all pages 
          #if not no_page_numbers [
            #set text(size: 9pt)
            #align(center)[
              #if counter(page).at(here()).first() == 1 [#date]
              #h(1fr)
              #counter(page).display("1")
            ]
          ]
        ]
     },     
  )  // END set page
}


// ========================================================================================
// MAIN CONF - this block goes almost to the end of this file

#let conf(
  title: none,                              // SET BASIC TEMPLATE DEFAULTS:
  subtitle: none,
  author: none,                             // IF NOT IN METADATA
  date:none,                                // IF NOT IN METADATA
  //  date: datetime.today().display(),     // IF NOT IN METADATA
  //  email: "email@example.com",           // IF NOT IN METADATA
  //venue: none,
  //abstract: none,
  cover: none,                              // cover image path
  //lang: "en",
  //region: "GB",
  //font: "Source Han Sans SC",               // sets the "font" variable
  //fontsize: 13pt,                           // likewise
  sectionnumbering: none,
  no_page_numbers: false,                   // 控制是否显示页码，运行时控制
  no_title_on_cover: false,                 // 控制是否在封面显示标题和作者，运行时控制
  doc,
) = {
  let font = "Source Han Sans SC"

  // 设置页面格式
  setpage()

  // === BASIC BODY PARAGRAPH FORMATTING ===
  set par(
    first-line-indent: 2em,
    leading: 1.5em, 
    justify: false,
    spacing: 2.0em,
  )

  set text(lang: "zh",
    font: font,                          // set on line 31 above
    size: 13pt,
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
    leading: 1.3em,
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
        #set text(font: font, weight: "semibold", size: 16pt, fill: rgb("#00008B"))
        #block(it.body) 
      ])

  show heading.where(level: 3
    ): it => align(left, block(above: 2.0em, below: 2.0em, width: 100%)[
        #set text(font: font, weight: "semibold", size: 14pt)
        #block(it.body) 
      ])

  // URLs
  show link: underline
  show link: set text(fill: navy)

// ====================================== LAYOUT =============================================
// HERE'S THE DOCUMENT LAYOUT

  // 封面图片：占满全页（包括边距）
  $if(cover)$
    create-cover-page(
      cover: cover,
      title: title,
      author: author,
      no_title_on_cover: no_title_on_cover
    )
  $endif$

  // 文章标题 
  v(2em)
  align(left, text(size: 24pt)[#title])

  // 作者信息
  $if(author)$
    align(left, [$author$])
  $endif$

  v(1em)

  // THIS IS THE ACTUAL BODY:

  counter(page).update(1)                                       // start page numbering

  doc                                                           // this is where the content goes

}  // end of #let conf block


// ========================================================================================
// BOILERPLATE PANDOC TEMPLATE:

#show: doc => conf(
  $if(title)$
    title: [$title$],
  $endif$

  $if(subtitle)$
    subtitle: [$subtitle$],
  $endif$

  $if(author)$
    author: [$author$],
  $endif$

  $if(venue)$
    venue: [$venue$],
  $endif$

  $if(date)$
    date: [$date$],
  $endif$

  $if(lang)$
    lang: "$lang$",
  $endif$

  $if(region)$
    region: "$region$",
  $endif$

  $if(abstract)$
    abstract: [$abstract$],
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

  $if(margin)$
    margin: ($for(margin/pairs)$$margin.key$: $margin.value$,$endfor$),
  $endif$

  $if(papersize)$
    paper: "$papersize$",
  $endif$

  $if(section-numbering)$
    sectionnumbering: "$section-numbering$",
  $endif$

  doc,
)

$if(toc)$
  #outline(
    title: auto,
    depth: none
  );
$endif$

$body$

$if(citations)$
  $if(bibliographystyle)$
    #set bibliography(style: "$bibliographystyle$")
  $endif$

  $if(bibliography)$
    #bibliography($for(bibliography)$"$bibliography$"$sep$,$endfor$)
  $endif$
$endif$

$for(include-after)$
  $include-after$
$endfor$
