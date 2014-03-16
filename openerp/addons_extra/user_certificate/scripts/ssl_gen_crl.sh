namefilecrl=$1
namefileca=$2
passca=$3
configfile=$4

openssl ca -config $configfile -md sha1 -passin pass:$passca -keyfile private/$namefileca.key.pem -cert certs/$namefileca.cert.pem -gencrl -out crl/$namefilecrl.pem

openssl crl -in crl/$namefilecrl.pem -text
