virtualhost=$1
virtualhostsource=$2
destination=$3

ln -s $virtualhostsource $destination
/usr/sbin/a2ensite $virtualhost
/usr/sbin/service apache2 reload