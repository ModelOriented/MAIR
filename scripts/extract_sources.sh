#!/usr/bin/env bash
for f in ../data/arxiv_dump/sources/*;
do
    mkdir ${f%.tar.gz}
    tar -xvf $f -C ${f%.tar.gz}
done
