#import "./nb-lib.typ": nb, comments
#import "./nb-cover-lib.typ": coverpage as default_cover
#import "./nb-report-cover-lib.typ": coverpage as report_cover
#import "./nb-darkbg-cover-lib.typ": coverpage as darkbg_cover
#import "./nb-backcover-lib.typ": backcoverpage as default_backcover
#import "./nb-backcover-biglogo-lib.typ": backcoverpage as biglogo_backcover

#let horizontalrule = {
  // v(2em)
  // line(start: (30%,0%), end: (70%,0%), stroke: 1pt + black)
  // v(2em)
  pagebreak()
}

// ==========================MAIN CONF=================================
#let conf(
  title: none,            //文章标题
  description: none,      //文章说明
  author: none,           //作者
  date:none,              //日期
  heroimage:none,         //封面图
  edition:none,           //系列名
  publication-info:none,  //出版物信息
  sourcelink: none,        //显示于目录页的来源信息
  tyfont: none,
  tyfont_title: none,
  disables: (),            //禁用项列表
  toc-depth:3,              //目录深度
  logo:none,
  headerleft: none,       //页眉左侧内容
  headerright: none,      //页眉右侧内容（缺省 title）
  footerleft: none,       //页脚左侧内容
  footerright: none,      //页脚右侧内容
  watermark: none,        //页面背景水印
  overview-fill: none,    //overview 块的默认背景色
  coverstyle: "default",  //封面样式: "default" / "report" / "darkbg"
  backcoverstyle: "default",  //封底样式: "default" / "biglogo"
  coverbg: none,          //封面背景图 (for darkbg style)
  doc,                  
) = {
  let disabled(name) = disables.contains(name)
  let disable_cover = disabled("cover")
  let disable_backcover = disabled("backcover")
  let disable_toc = disabled("toc")
  let disable_indent = disabled("indent")
  let disable_pagenumber = disabled("pagenumber")
  let disable_header = disabled("header")

  let font = if(tyfont != none) { (tyfont, "Helvetica", "LXGW Wenkai") } else { ("Helvetica", "LXGW Wenkai") }
  let titlefont = if(tyfont_title!=none) { (tyfont_title, "Source Han Sans SC", "Source Han Sans TC", "Source Han Sans") } else { ("Source Han Sans SC", "Source Han Sans TC", "Source Han Sans", "PingFang SC", "Noto Sans CJK SC", "Noto Sans CJK TC", "SimHei", "Heiti SC") }


  set text(
    lang: "zh",
    font: font,
    size: 12pt,
    alternates: false,
  )

  set par(
    first-line-indent: if (disable_indent) { 0em } else {(amount: 2em, all: true)},
    leading: 1.2em,
    justify: false,
    spacing: 2.0em,
  ) 

  // show: nb.with(
  //   title: [#title],
  //   author: [#author],
  //   description: [#description],
  //   edition: [#edition],
  //   date: [#date],
  //   hero-image: heroimage,    
  //   publication-info: [#publication-info],
  //   toc: toc,
  //   toc-depth: toc-depth,
  //   font: font,
  //   titlefont: titlefont,
  // )


  // 选择封面函数
  let coverpage = if coverstyle == "report" { 
    report_cover 
  } else if coverstyle == "darkbg" or coverstyle == "dark" {
    darkbg_cover
  } else { 
    default_cover 
  }

  // 调用封面页
  if not disable_cover {
    if coverstyle == "darkbg" or coverstyle == "dark" {
      coverpage(
        title: title,
        author: author,
        description: description,
        hero-image: heroimage,
        edition: edition,
        publication-info: publication-info,
        date: date,
        logo: logo,
        font: font,
        titlefont: titlefont,
        coverbg: coverbg
      )
    } else {
      coverpage(
        title: title,
        author: author,
        description: description,
        hero-image: heroimage,
        edition: edition,
        publication-info: publication-info,
        date: date,
        logo: logo,
        font: font,
        titlefont: titlefont,
      )
    }
  }
  
  set page(margin: (left: 2.5cm, top: 2.5cm, right: 6.0cm, bottom: 2.5cm),)

  //toc & content
  {
    set page(fill: luma(98%))
    set outline.entry(fill: none)

    // show outline.entry: it =>{
    //     it.indented(
    //       it.prefix(),
    //       if it.level <= 2 {  // 一级、二级标题：保留默认内部内容（包括页码）
    //         it.inner()
    //       } else {            // 三级及以上标题：仅显示标题内容，不显示填充和页码
    //         it.body()
    //       }
    //     )
    // }

    if not disable_toc and toc-depth > 0 {
      block(above: 4em, below:4em, text(size: 18pt, weight: "bold","目录"))

      outline(title: none, depth: toc-depth)

      if(sourcelink!=none){
        v(1fr)
        text(size:0.7em, sourcelink)
      }
      pagebreak()
    }
  }

  // doc

  nb(
    title: [#title],
    author: [#author],
    description: [#description],
    edition: [#edition],
    date: [#date],
    hero-image: heroimage,    
    publication-info: [#publication-info],
    toc: not disable_toc,
    toc-depth: toc-depth,
    font: font,
    titlefont: titlefont,
    disable-indent: disable_indent,
    headerleft: headerleft,
    headerright: headerright,
    footerleft: footerleft,
    footerright: footerright,
    watermark: watermark,
    overview-fill: overview-fill,
    disable-header: disable_header,
    disable-pagenumber: disable_pagenumber,

    doc
  )

  // 选择封底函数
  let backcoverpage = if backcoverstyle == "biglogo" {
    biglogo_backcover
  } else {
    default_backcover
  }

  // 调用封底页
  if not disable_cover and not disable_backcover {  
    backcoverpage(
      title: title,
      author: author,
      description: description,
      edition: edition,
      publication-info: publication-info,
      date: date,
      logo:logo
    )
  }
}


// ========================PANDOC TEMPLATE=============================
// Note：这是一个对 conf 函数的调用
// 以下是 pandoc 模板，不是语法错误！！！！ 
#show: doc => conf(
$if(title)$
title: [$title$],
$endif$
$if(description)$
description: [$description$],
$endif$
$if(author)$
author: [$author$],
$endif$
$if(date)$
date: [$date$],
$endif$
$if(heroimage)$
heroimage: (
  image: [#image("$heroimage.image$")],
  caption: [$heroimage.caption$],
),
$endif$
$if(pubinfo.logo)$
logo:[#image("$pubinfo.logo$")],
$endif$
$if(pubinfo.edition)$
edition: [$pubinfo.edition$],
$endif$
$if(pubinfo.info)$
publication-info: [$pubinfo.info$],
$endif$
$if(disables)$
disables: ($for(disables)$"$disables$"$sep$, $endfor$),
$endif$
$if(toc-depth)$
toc-depth: $toc-depth$,
$endif$
$if(sourcelink)$
sourcelink: [$sourcelink$],
$endif$
$if(headerfooter.headerleft)$
headerleft: [$headerfooter.headerleft$],
$endif$
$if(headerfooter.headerright)$
headerright: [$headerfooter.headerright$],
$endif$
$if(headerfooter.footerleft)$
footerleft: [$headerfooter.footerleft$],
$endif$
$if(headerfooter.footerright)$
footerright: [$headerfooter.footerright$],
$endif$
$if(pubinfo.watermark)$
watermark: rotate(45deg, text(size: 60pt, fill: rgb("EEEEEE"), weight: "bold", "$pubinfo.watermark$")),
$endif$
$if(theme.overview-fill)$
overview-fill: "$theme.overview-fill$",
$endif$
$if(theme.coverstyle)$
coverstyle: "$theme.coverstyle$",
$endif$
$if(theme.backcoverstyle)$
backcoverstyle: "$theme.backcoverstyle$",
$endif$
$if(theme.coverbg)$
coverbg: "$theme.coverbg$",
$endif$
$if(theme.font)$
tyfont: "$theme.font$",
$endif$
$if(theme.titlefont)$
tyfont_title: "$theme.titlefont$",
$endif$
doc,
)

$body$
