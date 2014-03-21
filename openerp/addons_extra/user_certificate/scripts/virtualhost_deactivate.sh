virtualhost=$1
destination=$2

a2dissite $virtualhost
rm $destination
service apache2 reload