#import "./term-lib.typ": term-doc, termgrid

// ==========================MAIN CONF=================================
#let conf(
  title: none,
  source: none,
  cn: false,
  doc,
) = {
  show: term-doc.with(
    title: [#title],
    source: source,
    cn: cn,
  )

  doc                                          
}  

// ========================PANDOC TEMPLATE=============================
#show: doc => conf(
$if(title)$
title: [$title$],
$endif$
$if(source)$
source: "$source$",
$endif$
$if(cn)$
cn: $cn$,
$endif$
doc,
)

$body$
