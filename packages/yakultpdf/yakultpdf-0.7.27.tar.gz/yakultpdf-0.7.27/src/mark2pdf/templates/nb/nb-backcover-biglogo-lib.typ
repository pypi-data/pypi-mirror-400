// nb-backcover-biglogo-lib.typ - 封底库文件 (大Logo版)
// 提供封底页的创建函数，中心显示大Logo

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

  v(20em)
  align(center + horizon)[
    // 居中显示 logo
    #align(center, pad(left: 2cm, block(width: 10cm, logo)))
  ]
  v(1fr)
  [
    // #title\
    // #author\
    #edition\
    #publication-info\
    #date
  ]
}
