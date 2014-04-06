#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Must supply number of jobs"
    exit 1
fi
NJOBS="$1"

JOB="/groups/visitors/home/hackathon/graham/server_job.sh"
#JOB="/groups/visitors/home/hackathon/graham/alignment_hackathon/serve/run.py"
OPTS="-j y -l short=true"

# submit N rendering nodes with ports 5000 + i
# submit 'server_job.sh'
#/groups/visitors/home/hackathon/graham/server_job.sh $PORT
for I in `seq 1 $NJOBS`; do
    PORT=$(( 5000 + $I ))
    NAME="graham_$I"
    # submit job
    qsub -N $NAME -o /groups/visitors/home/hackathon/graham/logs/$NAME $OPTS -cwd -V -S /bin/bash $JOB $PORT
    #qsub -N $NAME -o /groups/visitors/home/hackathon/graham/$NAME $OPTS -cwd -V /usr/bin/env python $JOB $PORT
    #qsub -N $NAME -o /groups/visitors/home/hackathon/graham/$NAME $OPTS -cwd -V /usr/bin/env python $JOB $PORT
done
