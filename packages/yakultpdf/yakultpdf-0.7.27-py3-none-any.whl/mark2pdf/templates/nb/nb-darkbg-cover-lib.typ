// nb-darkbg-cover-lib.typ - Dark Background Cover Library
// Based on nb-report-cover-lib.typ, adapted for dark theme

#let covertitle(
  title: none,
  titlefont: none,
) = {
  set text(font: titlefont, size: 24pt, tracking: -1pt, weight: "bold", fill: white)
  block(
    width: 100%,
    par(
      leading: 0.5em,
      first-line-indent: 0em,
      align(center, text(title)),
    ),
  )
}

// Function to create the cover page
#let coverpage(
  title: none,
  author: none,
  edition: none,
  hero-image: none,
  description: none,
  publication-info: none,
  date: none,
  logo: none,
  font: none,
  titlefont: none,
  coverbg: none,
) = {
  // Determine background
  let bg = if coverbg != none {
    image(coverbg, width: 100%, height: 100%, fit: "cover")
  } else {
    rect(width: 100%, height: 100%, fill: gradient.linear(angle: 135deg, rgb("#1a1a1a"), rgb("#000000")))
  }

  set page(
    width: 210mm,
    height: 297mm,
    margin: (left: 2.5cm, top: 2.5cm, right: 2.5cm, bottom: 2.0cm),
    header: none,
    background: bg,
    fill: white, // Default text fill for the page
  )

  set text(
    lang: "zh",
    font: titlefont,
    size: 12pt,
    alternates: false,
    fill: white,
  )
  set align(center)

  // 1. Top: Title and Description
  v(1cm)
  covertitle(title: title, titlefont: titlefont)

  if description != none {
    v(1em)
    block(width: 80%, text(size: 14pt, fill: white, description))
  }

  // 2. Middle: Hero Image (optional) - 固定位置，从垂直中间开始
  if hero-image != none {
    place(center + horizon, dy: 4.1cm, {
      set image(width: 100%)
      hero-image.image
    })
  }
  v(1fr)

  // 3. Bottom
  // Left: Edition, Publication Info
  // Right: Logo
  place(bottom, dy: 0.5cm, {
    grid(
      columns: (1fr, auto),
      gutter: 1em,
      align: (left + bottom, right + bottom),
      {
        if edition != none {
          text(size: 14pt, weight: "bold", fill: white, edition)
          linebreak()
        }
        if publication-info != none {
          text(fill: white, publication-info)
        }
      },
      if logo != none {
        move(dy: 0.5em, block(width: 3.5cm, logo))
      },
    )
  })
}
