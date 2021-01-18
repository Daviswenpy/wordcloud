#!/bin/bash

if [ ${ITM_CONFIG}x = "testx" ]; then
    LOGDIR="/home/share/itpserver/bean/logs"
else
    LOGDIR="/opt/skyguard/itpserver/logs"
fi

# test
echo $LOGDIR

DATE=`date -d "yesterday" +"%Y-%m-%d"`

BACKUPCOUNT="7"

DELDATE=`date -d "${BACKUPCOUNT} day ago" +"%Y-%m-%d"`

mv ${LOGDIR}/uwsgi.log   ${LOGDIR}/uwsgi.${DATE}.log

rm -f ${LOGDIR}/uwsgi.${DELDATE}.log

touch ${LOGDIR}/.touchforlogrotat
