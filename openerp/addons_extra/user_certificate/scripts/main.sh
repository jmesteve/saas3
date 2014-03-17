sh initialize.sh

sh ssl_root_authority.sh ca "erpandcloud CA" kvmpdu2010 ES Valencia Valencia erpandcloud 2048 3650

sh ssl_intermediate_authority.sh intermediate "erpandcloud CA1" kvmpdu2010 140315000000Z 240312000000Z ES Valencia Valencia erpandcloud 2048 ca cachain openssl.cnf

sh ssl_gen_server.sh esgeno.com *.esgeno.com kvmpdu2010 140315000000Z 240312000000Z ES Valencia Valencia erpandcloud 2048 intermediate kvmpdu2010 openssl_server.cnf

sh ssl_gen_user.sh pepe pepe kvmpdu2010 140315000000Z 240312000000Z ES Valencia Valencia erpandcloud 2048 ca kvmpdu2010 openssl_client.cnf

ssl_gen_p12.sh pepe ca kvmpdu2010 kvmpdu2010 openssl.cnf

sh ssl_gen_crl.sh crl ca kvmpdu2010 openssl.cnf
