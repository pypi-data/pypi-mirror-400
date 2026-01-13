# How To
```
openssl req -subj '/CN=Relukko CA' -x509 -sha256 -days 7300 -noenc -newkey rsa:2048 -keyout rootCA.key -out rootCA.crt -addext keyUsage=critical,cRLSign,digitalSignature,keyCertSign

ln -s rootCA.crt "$(openssl x509 -hash -noout -in rootCA.crt).0"

openssl req -subj '/CN=relukko' -newkey rsa:2048 -noenc -keyout relukko.key -out relukko.csr -addext keyUsage=critical,digitalSignature,keyEncipherment,keyAgreement -addext extendedKeyUsage=critical,serverAuth

openssl x509 -req -CA rootCA.crt -CAkey rootCA.key -in relukko.csr -out relukko.crt -days 7299 -CAcreateserial
openssl x509 -inform PEM -in rootCA.crt  -outform DER -out rootCA.der
```
