// Term Lib - 术语文档样式库
#let source-state = state("source", none)
#let cn-state = state("cn", false)

#let termitem(
  term: none,
  cn: false
)={
  let img = "./images/aiterm/"+term.image+".png"
  let title = if cn { [#term.term #term.term_zh] } else { [#term.term] }
  let description = if cn { term.description_zh } else { term.description }

  stack(
    spacing: 1em,
    align(center+horizon, text(weight: "bold", size: 0.9em)[#title]),
    image(img, width: 80%),
    align(left, text(size: 0.8em)[#description])
  )
}

// 读取 CSV 数据，过滤指定category的数据
#let termgrid(
  category: none,
  source: none,
  cn: false,
)={
  context [
    #let actual-source = if source != none { source } else { source-state.get() }
    #let actual-cn = if cn != false { cn } else { cn-state.get() }
    #if actual-source == none { text("No source provided")}
    #if category == none { text("No category provided") }

    #let data = csv(actual-source, row-type: dictionary)
    #let filtered-data = data.filter(term => term.category == category)
      
    #set align(center+horizon)
    #show: grid(
      columns: 3,
      column-gutter: 2.0em,
      row-gutter: 1.5em,
      ..filtered-data.map(term => {
        rect(
          width: 100%,
          height: 16.2em,
          fill: rgb(248, 250, 252),
          stroke: (0.5pt + blue),
          radius: 8pt,
          inset: 0.5em,
          termitem(term: term, cn: actual-cn)            //termitem card
        )
      })
    )
    #show: v(1fr)
  ]
}

// term document
#let term-doc(
  title: none,
  source: none,
  cn: false,
  body
) = {
  // 设置状态 - 必须在文档内容中调用才能生效
  source-state.update(source)
  cn-state.update(cn)
  
  set page(
    width: 210mm,
    height: 297mm,
    margin: (left: 2.0cm, top: 1.5cm, right: 2.0cm, bottom: 1.5cm),
    header: none,
    footer: none,
    // fill: gradient.linear(..color.map.viridis)
  )

  set par(leading: 0.8em, spacing: 0.8em)  
  set text( lang: "en", font: "Helvetica Neue", size: 10pt)
  show heading.where(level: 1): it => {
    set text(size: 16pt, weight: "bold", fill: black)
    align(center, block(above: 2em, below: 1.5em, width: 100%)[#it.body])
  }
  
  body
}
