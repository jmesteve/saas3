namefile=$1
commonname=$2
pass=$3
begindate=$4
enddate=$5
country=$6
city=$7
state=$8
organization=$9
keysize=${10}
namefileca=${11}
passca=${12}
configfile=${13}

echo $country
echo $city
echo $state
echo $organization
echo $keysize
echo $commonname
echo $namefile
echo $pass

openssl genrsa -out private/$namefile.key.pem $keysize
#chmod 400 private/$namefile.key.pem

openssl req -extensions v3_req -config $configfile -new -key private/$namefile.key.pem -out certs/$namefile.csr.pem -subj /C="$country"/ST="$state"/L="$city"/O="$organization"/CN="$commonname"

openssl ca -batch -config $configfile -startdate $begindate -enddate $enddate -passin pass:$passca -keyfile private/$namefileca.key.pem -cert certs/$namefileca.cert.pem -notext -md sha1 -in certs/$namefile.csr.pem -out certs/$namefile.cert.pem
#chmod 444 certs/$namefile.cert.pem

openssl x509 -in certs/$namefile.cert.pem -noout -text

#openssl verify -CAfile certs/.cert.pem certs/$namefile.cert.pem