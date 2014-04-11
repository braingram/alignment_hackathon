#!/bin/bash

## qsub options

# need to port forward, a seperate port per host
#REMOTE="graham@10.101.30.79" # set this by command line?
#RPORT="5000"  # set this per host

if [ $# -lt 1 ]; then
    echo "Must supply serving port"
    exit 1
fi
#REMOTE="$1" # set this by command line?
#RPORT="$2"  # set this per host
#echo "Setting up server forwarding to $REMOTE:$RPORT"
PORT="$1"

# setup path, etc
cd /groups/visitors/home/hackathon/graham
. sourceme
cd alignment_hackathon/serve

# port forward
#echo "forwarding 5000:localhost to $REMOTE:$RPORT"
#ssh -R 5000:localhost:$RPORT $REMOTE -N &
#SSHPID=$!

# run server
echo "running server"
touch /groups/visitors/home/hackathon/graham/servers/`hostname`:$PORT
python run.py 0.0.0.0 $PORT

# cleanup
echo "cleaning up"
rm /groups/visitors/home/hackathon/graham/servers/`hostname`:$PORT
# kill port forward
#kill $!
echo "finished"
exit 0
