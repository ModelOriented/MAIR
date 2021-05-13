#!/bin/bash
SEARCH='strict digraph  {'
REPLACE='strict digraph  {rankdir=LR;node  [style="rounded,filled,bold", shape=box, fixedsize=false, fontname="Arial"];edge  [style=bold, fontname="Arial" weight=2];'

LINE_REPLACE_PATTERN="s/(.*) -> (.*);/\2 -> \1;/"

dvc dag --dot > dot.txt
sed -i -E "$LINE_REPLACE_PATTERN" dot.txt
sed -i "s/$SEARCH/$REPLACE/" dot.txt
dot -Tpng dot.txt > pipeline.png

dvc dag --dot -o > dot.txt
sed -i -E "$LINE_REPLACE_PATTERN" dot.txt
sed -i "s/$SEARCH/$REPLACE/" dot.txt
dot -Tpng dot.txt > artifacts.png

rm dot.txt
