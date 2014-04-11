#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Must supply number of jobs"
    exit 1
fi
NJOBS="$1"

# location of server_job.sh
JOB="`cwd`/server_job.sh"
LOGDIR="`cwd`/logs"
mkdir -p $LOGDIR
OPTS="-j y -l short=true"

# submit N rendering nodes with ports 5000 + i
# submit 'server_job.sh'
for I in `seq 1 $NJOBS`; do
    PORT=$(( 5000 + $I ))
    NAME="tileviewer_$I"
    # submit job
    qsub -N $NAME -o $LOGDIR/$NAME $OPTS -cwd -V -S /bin/bash $JOB $PORT
done
