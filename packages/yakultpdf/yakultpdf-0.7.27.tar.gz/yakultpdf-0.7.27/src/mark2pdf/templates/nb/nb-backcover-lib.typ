// nb-backcover-lib.typ - 封底库文件
// 提供封底页的创建函数

#let backcoverpage(
  title: none,
  author: none,
  edition: none,
  description: none,
  publication-info: none,
  date: none,
  logo: none,
) = {
  // pagebreak()
  set page(fill: luma(95%)) //前面有内容，setpage 会自然地进行分页
  set text(0.7em)
  set par(first-line-indent: 0em)

  v(1fr)
  [
    #block(width: 3cm, logo)
    // #title\
    // #author\
    #edition\
    #publication-info\
    #date
  ]
}
