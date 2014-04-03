#!/bin/bash

mkdir -p tiles
for X in `seq 1 10`; do
    for Y in `seq 1 10`; do
        echo "tile ${X}_$Y"
        convert base.tif -pointSize 50 -gravity center -annotate 0 ${X}_$Y tiles/${X}_$Y.tif
    done
done
