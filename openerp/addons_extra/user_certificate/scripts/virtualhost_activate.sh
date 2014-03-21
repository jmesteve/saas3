virtualhost=$1
virtualhostsource=$2
destination=$3

ln -s $virtualhostsource $destination
a2ensite $virtualhost
service apache2 reload