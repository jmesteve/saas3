DIR_SERVICE='/etc/init.d/'
SERVICE_PATTERN='openerp'

DIRECTORY=`ls $DIR_SERVICE | grep $SERVICE_PATTERN`
#echo $DIRECTORY

for D in $DIRECTORY
  do
        $DIR_SERVICE$D start
  done

exit 0
