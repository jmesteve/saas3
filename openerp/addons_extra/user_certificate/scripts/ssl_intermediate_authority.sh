# INTERMEDIATE AUTHORITY

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
namefilechain=${12}
configfile=${13}

echo $keysize

openssl genrsa -aes256 -passout pass:$pass -out private/$namefile.key.pem $keysize
#chmod 400 private/$namefile.key.pem
openssl req -config $configfile -new -key private/$namefile.key.pem -subj /C="$country"/ST="$state"/L="$city"/O="$organization"/CN="$commonname" -passin pass:$pass -out certs/$namefile.csr.pem

# Poner la hora con python
# import datetime
# begin_date = datetime.date.today() or another
# end_date = begin_date + datetime.timedelta(days=3650)
# begin_date.strftime("%y%m%d%H%M%S") + 'Z'
# end_date.strftime("%y%m%d%H%M%S") + 'Z'

openssl ca -batch -config $configfile -startdate $begindate -enddate $enddate -passin pass:$pass -keyfile private/$namefileca.key.pem -cert certs/$namefileca.cert.pem -extensions v3_ca -notext -md sha1 -in certs/$namefile.csr.pem -out certs/$namefile.cert.pem
#chmod 444 certs/$namefile.cert.pem

openssl verify -CAfile certs/$namefileca.cert.pem certs/$namefile.cert.pem

cat certs/$namefile.cert.pem certs/$namefileca.cert.pem > certs/$namefilechain.cert.pem
#chmod 444 certs/$namefilechain.cert.pem

# Verify other file certificates
# openssl verify -CAfile certs/ca-chain.cert.pem certs/www.example.com.cert.pem