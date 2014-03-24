virtualhost=$1
virtualhostsource=$2
destination=$3

/usr/sbin/a2dissite $virtualhost
rm $destination
/usr/sbin/service apache2 reload
rm $virtualhostsource