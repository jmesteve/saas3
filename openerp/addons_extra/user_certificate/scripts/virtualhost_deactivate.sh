virtualhost=$1
destination=$2

/usr/sbin/a2dissite $virtualhost
rm $destination
/usr/sbin/service apache2 reload