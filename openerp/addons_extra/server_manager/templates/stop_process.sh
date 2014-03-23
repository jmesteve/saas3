#!/bin/sh
##########################################
## restart openerp servers
##########################################
DIR_SERVICE='/etc/init.d/'
NAME_PATTERN=${NAME_PATTERN}
SERVICE_PATTERN='openerp'

PROCESS=`ps ax | grep $NAME_PATTERN | awk '{ print $1}' | sed '$d'`
echo $PROCESS

for P in $PROCESS
  do
     kill $P
     echo 'kill process '$P
  done

exit 0


