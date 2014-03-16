# GENERATE P12
namefile=$1
namefilecaroot=$2
pass=$3
passcaroot=$4

openssl pkcs12 -export -in certs/$namefile.cert.pem -inkey private/$namefile.key.pem -certfile certs/$namefilecaroot.cert.pem -out certs/$namefile.p12 -passin pass:$passcaroot -passout pass:$pass