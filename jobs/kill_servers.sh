#!/bin/bash

if [ -z "$TILESERVER_DIR" ]; then
    echo "env variable TILESERVER_DIR must be set"
fi

qdel `qstat | grep tileviewer | awk '{print $1}'`
rm $TILESERVER_DIR/*
