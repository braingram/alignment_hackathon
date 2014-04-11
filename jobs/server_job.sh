#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Must supply serving port"
    exit 1
fi
PORT="$1"

# setup path, etc
cd /groups/visitors/home/hackathon/graham
. sourceme
cd alignment_hackathon/serve

# run server
echo "running server"
touch /groups/visitors/home/hackathon/graham/servers/`hostname`:$PORT
python run.py 0.0.0.0 $PORT

# cleanup
echo "cleaning up"
rm /groups/visitors/home/hackathon/graham/servers/`hostname`:$PORT

# kill port forward
echo "finished"
exit 0
