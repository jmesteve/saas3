# PARAMS

namefile=$1
commonname=$2
pass=$3
country=$4
city=$5
state=$6
organization=$7
keysize=$8
days=$9

openssl genrsa -aes256 -passout pass:$pass -out private/$namefile.key.pem $keysize
#chmod 400 private/$namefile.key.pem

openssl req -new -x509 -days $days -key private/$namefile.key.pem -extensions v3_ca -subj /C=$country/ST=$state/L=$city/O=$organization/CN="$commonname" -passin pass:$pass -out certs/$namefile.cert.pem
#chmod 444 certs/$namefile.cert.pem
 