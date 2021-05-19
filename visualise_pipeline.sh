#!/bin/bash

dvc dag --dot > dot.txt
sed -i -E "s/(.*) -> (.*);/\2 -> \1;/" dot.txt
dot -Tpng dot.txt > pipeline.png
rm dot.txt

dvc dag --dot -o > dot.txt
sed -i -E "s/(.*) -> (.*);/\2 -> \1;/" dot.txt
dot -Tpng dot.txt > artifacts.png
rm dot.txt
