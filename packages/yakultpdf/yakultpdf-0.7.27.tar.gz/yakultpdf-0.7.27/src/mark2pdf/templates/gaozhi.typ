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

#import "./gaozhi-lib.typ": *
#import "@preview/wordometer:0.1.5": total-words, word-count

#let horizontalrule = colbreak()



// ========================================================================================
// MAIN CONF

#let conf(
  doc,
) = {
  show: word-count
  calligraphy-work(type: "Full")[#doc]
}

#show: doc => conf(
  doc,
)

$body$
