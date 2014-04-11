#!/bin/bash

if [ -z "$TILESERVER_DIR" ]; then
    echo "env variable TILESERVER_DIR must be set"
fi

if [ $# -lt 1 ]; then
    echo "Must supply serving port"
    exit 1
fi
PORT="$1"

# setup path, etc
#. sourceme

# run server
echo "running server"
touch $TILESERVER_DIR/`hostname`:$PORT
python -m tileserver 0.0.0.0 $PORT

# cleanup
echo "cleaning up"
rm $TILESERVER_DIR/`hostname`:$PORT

# kill port forward
echo "finished"
exit 0
