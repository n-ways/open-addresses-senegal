#!/bin/sh
# Builds the paper's PDFs from docs/paper.md and its translations (docs/paper.<lang>.md) with pandoc and LaTeX (tectonic).
#   sh docs/paper/build.sh            # every language
# Needs pandoc 3, tectonic and pdftocairo. Figures are compiled from docs/figures/*.tex first
# (their data files, in docs/figures/data, are written by tools/paper-figures.py).
set -e
here=$(cd "$(dirname "$0")" && pwd)
docs=$(dirname "$here")
for f in "$docs"/figures/*.tex; do
  [ -e "$f" ] || continue
  b=${f%.tex}
  t=${b%.fr}.tikz   # the drawing shared by the language wrappers
  if [ ! -e "$b.pdf" ] || [ ! -e "$b.svg" ] || [ "$f" -nt "$b.pdf" ] || [ "$t" -nt "$b.pdf" ] \
     || [ "$docs/figures/common.sty" -nt "$b.pdf" ] || [ -n "$(find "$docs/figures/data" -newer "$b.pdf" -type f 2>/dev/null)" ]; then
    (cd "$docs/figures" && tectonic -X compile "$(basename "$f")" 2>&1 | grep -v "^note:") || true
    pdftocairo -svg "$b.pdf" "$b.svg"
  fi
done
build() { # $1 source, $2 output, $3 language
  bib="$here/references.bib"
  [ -e "$here/references.$3.bib" ] && bib="$here/references.$3.bib"
  pandoc "$docs/$1" --from markdown+tex_math_dollars+raw_tex --template "$here/template.tex" \
    --citeproc --bibliography "$bib" --csl "$here/ieee.csl" --lua-filter "$here/figures.lua" \
    -H "$here/style.tex" -H "$here/colours.tex" --resource-path "$docs:$here" --number-sections --toc --pdf-engine=tectonic -o "$docs/$2"
}
base=n-ways-addressing-senegal
for src in "$docs"/paper.md "$docs"/paper.*.md; do
  [ -e "$src" ] || continue
  name=$(basename "$src")
  case $name in paper.md) lang=en ;; *) lang=${name#paper.}; lang=${lang%.md} ;; esac
  build "$name" "$base-$lang.pdf" "$lang"
done
