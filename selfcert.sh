#!/bin/bash
echo
# step 1 create the key
echo create key ....
echo 
openssl req -newkey rsa:2048 -nodes -keyout private.key -x509 -days 365 -out private.pem

# Review the created certificate
openssl x509 -text -noout -in private.pem
read -p "Press [Enter] key to  continue ..."


# step 2 Create a PKCS12 certificate (.p12)
echo create certs ....
echo 
openssl pkcs12 -export -out ./keystore.p12  -inkey ./private.key -in ./private.pem -name root -passout pass:*****

#Validate the P2 file
openssl pkcs12 -in /keystore.p12 -noout -info

read -p "Press [Enter] key to  continue ..."

# step 3 Convert this file into a Java keystore file (.jks)
echo create keystore....
echo
keytool -importkeystore -v -srckeystore ./keystore.p12  -srcstoretype pkcs12 -srcstorepass toapgi -destkeystore keystore.jks -deststorepass toapgi

# step 4 inspect the keystore file and verify
echo verify keystore...
echo  
# Import Certificate Chain file
# keytool -import -alias root -keystore ./keystore.jks -trustcacerts -file general.chain
keytool -list -v -keystore toapgi-ui-1.jks -storepass *****
read -p "Press [Enter] key to  continue ..."

