namefile=$1
commonname=$2
begindate=$3
enddate=$4
country=$5
city=$6
state=$7
organization=$8
keysize=${9}
namefileca=${10}
passca=${11}
configfile=${12}

openssl genrsa -out private/$namefile.key.pem $keysize
#chmod 400 private/$namefile.key.pem

openssl req -extensions v3_req -config $configfile -new -key private/$namefile.key.pem -out certs/$namefile.csr.pem -subj /C="$country"/ST="$state"/L="$city"/O="$organization"/CN="$commonname"

openssl ca -batch -extensions v3_req -config $configfile -startdate $begindate -enddate $enddate -passin pass:$passca -keyfile private/$namefileca.key.pem -cert certs/$namefileca.cert.pem -notext -md sha1 -in certs/$namefile.csr.pem -out certs/$namefile.cert.pem
#chmod 444 certs/$namefile.cert.pem

openssl x509 -in certs/$namefile.cert.pem -noout -text

#openssl verify -CAfile certs/.cert.pem certs/$namefile.cert.pem