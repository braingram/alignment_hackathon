#!/bin/bash

mkdir -p tiles

for X in `seq 1 10`; do
    for Y in `seq 1 10`; do
        echo "tile ${X}_$Y"
        composite -pointsize 50 label:"${X}_$Y" base.tif tiles/${X}_$Y.tif
        #convert base.tif -pointSize 50 -gravity center -annotate 0 ${X}_$Y -colorspace Gray tiles/${X}_$Y.tif
    done
done
