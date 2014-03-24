#!/bin/sh
##########################################
## restart openerp servers
##########################################
DIR_SERVICE='/etc/init.d/'
NAME_PATTERN='openerp-server'
SERVICE_PATTERN='openerp'

PROCESS=`ps ax | grep $NAME_PATTERN | grep 'python' | awk '{ print $1}'`
echo $PROCESS

for P in $PROCESS
  do
     kill $P
     echo 'kill process '$P
  done

exit 0


