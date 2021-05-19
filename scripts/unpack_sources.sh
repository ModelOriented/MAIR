#!/usr/bin/env bash
mkdir data/arxiv_dump/unpacked_sources/
for f in data/arxiv_dump/sources/*;
do
    mkdir data/arxiv_dump/unpacked_sources/$(basename ${f%.tar.gz})
    tar -xvf $f -C data/arxiv_dump/unpacked_sources/$(basename ${f%.tar.gz})
done
