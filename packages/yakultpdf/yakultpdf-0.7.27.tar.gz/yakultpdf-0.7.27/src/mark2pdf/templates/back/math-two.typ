// Math Exercise Template for use with md2pdf.py

#let horizontalrule = [
  #colbreak()
]

#let conf(
  doc,
) = {
  let font = "Source Han Sans SC"

  set page(
    paper: "a4",
    flipped: false,                         
    margin: (left: 1.0cm, top: 2.5cm, right: 1.0cm, bottom: 1.5cm),
    header: {
      set text(size: 12pt)
      align(center)[\_\_\_ 月 \_\_\_ 日]
    },
    footer-descent: 30%,
    footer: none
  )  

  set par(
    first-line-indent: 0em,
    leading: 1.5em,  // 增加行高，确保行内数学公式中的分数有足够空间正确显示
    justify: false,
    spacing: 12em,  // 段落间距，确保每道题单独一行
  )

  set text(
    lang: "zh",
    font: font,                          
    size: 11pt,
    alternates: false,
  )
  
  // 只对块级数学公式应用左对齐，不影响行内数学公式
  show math.equation.where(block: true): set align(left)

  columns(2, gutter: 0.8cm)[
    #doc
  ]
}  

#show: doc => conf(
  doc,
)

$body$              

