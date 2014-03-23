DIR_SERVICE='/etc/init.d/'
SERVICE_PATTERN='${SERVICE_PATTERN}'

DIRECTORY=`ls $DIR_SERVICE | grep $SERVICE_PATTERN`
#echo $DIRECTORY

for D in $DIRECTORY
  do
        service $DIR_SERVICE$D start
  done

exit 0
