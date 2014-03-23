#!/bin/sh
##########################################
## restart openerp servers
##########################################
DIR_SERVICE='/etc/init.d/'
NAME_PATTERN=${NAME_PATTERN}

PROCESS=`ps ax | grep $NAME_PATTERN | grep 'python' | awk '{ print $1}'`
echo PROCESS




