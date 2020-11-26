#!/usr/bin/env bash
for f in ./sources/*;
do
    mkdir ${f%.tar.gz}
    tar -xvf $f -C ${f%.tar.gz}
done