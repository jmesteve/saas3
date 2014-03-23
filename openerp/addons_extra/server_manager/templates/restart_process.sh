#!/bin/sh
##########################################
## restart openerp servers
##########################################
DIR_SERVICE='/etc/init.d/'
NAME_PATTERN='${NAME_PATTERN}'
SERVICE_PATTERN='${SERVICE_PATTERN}'

PROCESS=`ps ax | grep $NAME_PATTERN | grep 'python' | awk '{ print $1}'`
for P in $PROCESS
  do
     kill $P
     echo 'kill process '$P
  done
#echo $PROCESS
DIRECTORY=`ls $DIR_SERVICE | grep $SERVICE_PATTERN`
#echo $DIRECTORY

for D in $DIRECTORY
  do
        $DIR_SERVICE$D start
  done

exit 0




