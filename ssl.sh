openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365
openssl req -newkey rsa:4096 -keyform PEM -keyout ca.key -x509 -days 3650 -outform PEM -out ca.cer