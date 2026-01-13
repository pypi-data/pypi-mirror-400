#import "@preview/wordometer:0.1.5": word-count, total-words

// #show: word-count

#let calligraphy-paper(
  cols: 20,                     // 列数 (用于中文)
  rows: 20,                     // 行数
  color: red,                   // 线条颜色
  size: 2em,                    // 大小（字体尺寸）
  blank-row: 2,                 // 底部留空的行数
  blank-col: 0,                 // 右侧留空的列数
  // type: "Normal", // 类型：Normal（默认）、AllH（全留空行）、AllV（全留空列）、Full（无留白）
  spacing: 1.2em,               // 内部线条的间距，用不上
  row-gap: 0.5em,               // 行间空隙大小
) = {

  // 计算新的行配置：每两行之间插入空隙
  // 原始行数20 -> 新行数39 (20*2-1)
  // 奇数行(1,3,5...): 正常高度size，绘制边框
  // 偶数行(2,4,6...): 空隙高度row-gap，不绘制边框
  let total-rows = rows * 2 - 1
  let row-sizes = ()
  
  // 构建行大小数组：交替使用size和row-gap
  for i in range(1, rows + 1) {
    row-sizes = row-sizes + (size,)  // 正常行
    if i < rows {
      row-sizes = row-sizes + (row-gap,)  // 空隙行（除了最后一行）
    }
  }

  // 设置网格布局
  set grid(
    columns: (size * 85%,) * cols,                     // 定义网格列数及尺寸
    rows: row-sizes,                                   // 使用新的行配置
    stroke: (paint: color, thickness: 0.8pt),          // 默认网格线颜色
  )

  // 渲染
  // rotate(0deg)[
  //   #figure(
  block(
      inset: 1em,
      grid(
        // grid.hline(stroke: 1pt, y: 0), // 顶部边界线
        // grid.vline(stroke: 1pt, x: 0), // 左侧边界线
        // grid.vline(stroke: 1pt, x: cols), // 右侧边界线
        // grid.hline(stroke: 1pt, y: rows), // 底部边界线

        // 渲染右侧空列
        // ..(grid.cell(rowspan: rows)[],) * blank-col,

        // 渲染底部空行
        // ..(grid.cell(
        //     colspan: if 2.bit-and(1) == 0 { cols } else { 1 }
        //   )[],) * 5,


        
        // 渲染剩余区域
        // ..(
        //   grid.cell()[ 
        //     ],
        // ) * (cols - 1) * rows 
      )
  )
  //   )
  // ]
}

#let calligraphy-work(
  font: "FZQingFangsongs",    // 默认字体 STFangsong
  size: 2em,                  // 字体大小
  cols: 20,                   // 列数
  rows: 20,                   // 行数
  color: rgb("#dddddd"),   // 颜色
  blank-row: 0,              // 底部空行数，不生效
  blank-col: 0,              // 右侧空列数，不生效
  type: "full",              // 纸张类型
  row-gap: 0.5em,            // 行间空隙大小
  body,                      // 实际内容
) = {
  let spacing = 1em * 120.0%                  // 文字行间距 122 for STFangsong
                                            // 121.5 FZFangsong-Z02S 
                                            // 120 FZQingFangsongs

  let x = (21cm - size * 85% * cols) / 2          // 水平边距计算

  let total-height = size * rows + row-gap * (rows - 1)  
                                           // 总高度 = 行高*行数 + 空隙*(行数-1)

  let y = (29.7cm - total-height) / 2      // 垂直边距计算
  let tracking = 1em * 60% * 69.5%          // 字符间距调整

  set page(
    margin: (left: x , right: x - 1.2em,  top: y, bottom: y),  // 页边距设置
    background: calligraphy-paper(
      spacing: spacing,
      cols: cols,
      rows: rows,
      color: color,
      blank-row: blank-row,
      blank-col: blank-col,
      // type: type,
      size: size,
      row-gap: row-gap,
    ),
  )

  // 行距设置
  set par(
    leading: spacing, 
    spacing: spacing,
    linebreaks: "simple",
    )  

  pad(
    left: 3pt,
    right: 0pt,
    top: 6pt,
    bottom: 0pt,
    text(
      size: size * 60%,     // 字体大小调整
      font: font,           // 字体
      lang: "zh",           // 语言设置
      tracking: tracking,   // 字符间距
      weight: "bold"
      )[
        #body                 // 渲染实际内容
      // 使用绝对定位将字数统计显示在框线之外
      #place(
        bottom + right, 
        dx: -12pt,
        dy: 16pt,
        text(size: 10pt, fill: gray)[
          （共 #total-words 字）
        ]
      )
      ]
      

  )
}