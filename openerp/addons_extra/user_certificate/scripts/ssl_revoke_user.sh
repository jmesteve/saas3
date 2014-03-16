namefile=$1
pass=$2
namefilecrl=$3
namefileca=$4
configfile=$5

cat index.txt

openssl ca -config $configfile -keyfile private/$namefileca.key.pem -passin pass:$pass -cert certs/$namefileca.cert.pem -revoke certs/$namefile.cert.pem

cat index.txt

openssl ca -config $configfile -keyfile private/$namefileca.key.pem -passin pass:$pass -cert certs/$namefileca.cert.pem -gencrl -out crl/$namefilecrl.pem

openssl crl -in crl/$namefilecrl.pem -text
