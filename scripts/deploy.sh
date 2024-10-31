#Fully automated the deployement process. ONLY RUN THIS SCRIPT ON THE 
#REMOTE SERVER! If you run this on your local machine, you're gonna 
#have a bad time.


#Build client first...
bash build.sh

#Auto generated vagabond config
echo "
config = {
    'mysql_server': '127.0.0.1',
    'mysql_user': '$USER',
    'mysql_password': 'password',
    'mysql_port': '3306',
    'mysql_database': '$USER',
    'domain': '$USER.teamvagabond.com',
    'api_url': 'https://$USER.teamvagabond.com/api/v1',

    'public_key': '''-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAli4avy7N6GwfPnlWnKPU
+s1ju+f1S4O1wqMthH9885jAZMrErHTBgU2E+9UrSCBSwGaXMihuprc4ANPfTCVj
P+m1EyNGAwiwCdyi0GzJx4q9OyGQjPHPLNfPEwe5t0laVbBcg6bUe9s1FtqwawtU
6A2CDmJKfuZQaobsUtuDMUR6uNqHjV2Mk2meCvOVl7YgIeJBXPRbX4i7jsqXuhur
sEKFi7Lse++rjfEYSaWSTN/RXNyeQH/zF8l9B3WwKgZts99Tb+K2aK5y0bVBcgDL
fGtzXe06lfMVMhi+pHWh+x9NxUofcvF/P11fNnJr+YD3G5tdypeawZcVo1F5iSx+
lASlSV78F6iGWks+xe1A77PlBvinHfN8rx20R1Ft0wib5eGQp8fiK2YRwhOhwrXG
8NXV8nWNDDGTpjJRt6FCoQuSN9/ZeOxOM+Qx4NvOlkSEZAyAL4Abqmza/quDa0N5
7KHEbe4IcXMuuaQz/PhZlIQNSOqj7NRL4LvwLfVHnIT3nEHa9oOhVYmrOQO2tLLz
Qa2BdtEBpy4TVXkcuHx5bJwELFLDvjt9kjuJrwlI3So5PRNTQWGr9XqgBpEFexhs
WdF/ss916GWhqi+qg9JGvwzSUEX47GgQJD0XYSa98jVmy7wqFecChSnr0euLr+oX
fjBJARx1JGEiTAZ3Ad3KbnkCAwEAAQ==
-----END PUBLIC KEY-----''',

    'private_key': '''-----BEGIN RSA PRIVATE KEY-----
MIIJKAIBAAKCAgEAli4avy7N6GwfPnlWnKPU+s1ju+f1S4O1wqMthH9885jAZMrE
rHTBgU2E+9UrSCBSwGaXMihuprc4ANPfTCVjP+m1EyNGAwiwCdyi0GzJx4q9OyGQ
jPHPLNfPEwe5t0laVbBcg6bUe9s1FtqwawtU6A2CDmJKfuZQaobsUtuDMUR6uNqH
jV2Mk2meCvOVl7YgIeJBXPRbX4i7jsqXuhursEKFi7Lse++rjfEYSaWSTN/RXNye
QH/zF8l9B3WwKgZts99Tb+K2aK5y0bVBcgDLfGtzXe06lfMVMhi+pHWh+x9NxUof
cvF/P11fNnJr+YD3G5tdypeawZcVo1F5iSx+lASlSV78F6iGWks+xe1A77PlBvin
HfN8rx20R1Ft0wib5eGQp8fiK2YRwhOhwrXG8NXV8nWNDDGTpjJRt6FCoQuSN9/Z
eOxOM+Qx4NvOlkSEZAyAL4Abqmza/quDa0N57KHEbe4IcXMuuaQz/PhZlIQNSOqj
7NRL4LvwLfVHnIT3nEHa9oOhVYmrOQO2tLLzQa2BdtEBpy4TVXkcuHx5bJwELFLD
vjt9kjuJrwlI3So5PRNTQWGr9XqgBpEFexhsWdF/ss916GWhqi+qg9JGvwzSUEX4
7GgQJD0XYSa98jVmy7wqFecChSnr0euLr+oXfjBJARx1JGEiTAZ3Ad3KbnkCAwEA
AQKCAgBIar73BajAtLJ0O6pqKg4fSj8XcwizezWAP5NJWvhztmq/r48a4coVgb3o
eag/RWbh5BZwV1LUDXFx5Li+TSEIxrdMHSw7dkr81mmkO3EpSVtqUgsUC94s73uo
34bMPRDUVRCnYyD/AHsfJCEB3Rr6MtlN+lOV0ZVhaOI4KiWe8jiDPs0ye7O3uaw9
96tg1q+z5xhBrIsLDDH07vgvA/zMJ6eh74tdT/rXnTRq/u4HJ74bGz8sNwaPp9ck
a7mg6iyoGb5wK1BuNgCj4tVGFeAJhP7CggxIFklYONplD1wmbbfgtJdpo84KTgoF
hTNPwsJli4u0j1pOk34ZnMYQQWZfWB6yF8UPEeOWqyKcZyA3hZEV3eY5oIDLT1UE
igGTKOFNXpDSH3cp0xONFBcfFhzLIM8O+AQIMMczf5j3Y4kEFwYUvNyjtg/ZP3gK
z6UWuZklQoJqLGk0EWdnfk0cAwD2sFTPTnUuJk2Ip21Vk0QEQy3qaqyUZlp3OM4/
2QvldzIgeLInRTlxXePZEGHeatXl7HqNP9pm241Jd8u0a9rUdnUT2psH2Sl+noL3
1FwkJQdLWRUM0i+o2WVqNP7g5k5P88h3k2TdJ7ZTF+ZmC2tE1RfPaevSGefc+2dW
8A03EV1+MUQYr0A6qevvq/YOymuPx/Npr7JjS6hAk8l9qtPcqQKCAQEAtaBYEXba
4vlXdDpexTl6V7U2OFYWJfqt0zymN3vU7nb5QuTd3F2I32axvo1lRQWCGpVDaxyo
Zc24AItHyEAwYfvmJ+mgzp5tlz3wIHj7w5FWIFbG0tdeWrxAzy8m4pewcEPKZP6o
Tumu4MPoTFT5DufowMP4tDh94LO2dCE2XcORk2Nr8O1VJ/pUfYDEkhtviW+sQT/m
wZuEIai5u4t//oYXQzC8Fg9X1H9JbWiSkFLTtcvDZn2OIkfzVXZ+5p3rG5G/MfXo
ZZAPRnYAIZgt7ykP3szGeNqGyK7Fv6RBonUX9XXPsCpZ93PjBqcb664UCVhqHJnL
t38+VPT2gvlUPwKCAQEA061KbGxxOXee3unFe9F8aNXSFoYkkhwVN7xXR2wHcluR
6Jz5mUTSqKXYfRh8onJTpVB3QBL4Y7+LeOE56KgrF8WxwN50kXdViywkIB/w7uTW
tefR1YhW7+P82sCzhRYQ9Q8JapNQvHxD5frB7Q3ctSP4KUy4ya6qMpEMsZQQGRx8
yDTCS4pTkMdnsJYWY/rC6I65KGkGxWF3tMOn+1/Re8PDLlVwYTQIuofC6zcUK7v+
NJ4DU2UCtYAlCOdho4f4U1LgQWxb/N12T1fykyLLX6DjMqtpLEHKmRo4rPno1k4z
Qns6qvgq2w529IePJUrjrv2JrD2A02h3iZpmTrOvRwKCAQAqTU41wxj4BFr6Fx47
kUeNZgda17IQ5nHV4SpVgeH2KH+ltOh3itF2NtTvLL+Jc975kgpByErwaxmQBuCR
I2IhcCoK4b8yYHPl5ecnqQX6Zr9IiO2F7eNr/qyZlMHZxLqzaxaYrzdEKekxMG/K
V4AqmJj9TKeAUif/TdwQ8CtZa1NcoKtjUeOjjAphsLwXy4wO1pOoHtn//diofkPE
CpmlDlYcsB0ehjROqdbQRKreMmxcyziXhma0VU23egHUdLNtmGSPnlaiUQs9vf4J
1QfdzBKGMeuH+l2qIAqut/MRg3QxF19oCHUrzTHzOrimC8Ve59jPEIMCGgDKiMNh
ffDBAoIBAQCJXfHoPs+TfZ9qBccUvTPBTNFTsKXW88aJLv5s6RxECEy96fDImDMl
IstFEzj+qrbBl2BsAmOTR+CZB4BvDYM5oB/ki/iV1h17fZ/MAS53uaXk0pYHvry8
XPXgeCGIAnPqtGFl+kfwqaveeUaUMeTC4J7RHmrk5yaoPh1AuFdiFGyd+C8GmrP0
RpNxs1TAeSE3jjd2lAHC4aevdTF0HhByAu6NCQEu83eepS/HOS0r3InxV4HNAsYp
RwnBp3Zji3+Jg0To8AsaJBX9E5PmDDRy0JPgdACCqgdyJ+QTzPJe8MyvHg1KmlYl
ZlOoCLjKeLkc/If1cMxDZY39jGdMN6tNAoIBAD8aOOMm4b75vGAia5Dp1ki0+Roy
JTkQEvLpSzygAP0wyacIYN7X9NjPXETu5//RCywFb3mDr6Fi2O9upWj4cq+YvXjU
MzUucdzcPQYdVrbtF2W5oO6+8QamDZ3Ym02E8aOsbFwwkI+LHH0FO0cqBUMeKt1B
2tkEs2KuWDwir9L5F1SC6uaJWDcTbPX7BQukBaDJIgqNmkY6v5rEssI8qoxRlY7A
3iZtwEGkDHSCAnmED/wMpfVV5ovLy+bvglNa0qaNj5XNmcJq6k1anzAfAZrrcINM
gHLyUT2ja7yOF3PQT4SkYvvxltwR9UD2JGhkHm0CG4d0GtOvf78YlJpbN08=
-----END RSA PRIVATE KEY-----'''
}
" > ../server/vagabond/config/config.py

#WSGI Config
echo "
#Auto-generated WSGI configuration
import sys
sys.path.insert(0, '/var/www/$USER/')
sys.path.insert(0, '/var/www/$USER/env/lib/python3.8/site-packages')
from vagabond import app as application
" > ../server/wsgi.py

#cd into root directory
cd ..

# Deploy app
rm -dr /var/www/$USER/*
cp -dr server/* /var/www/$USER/

#cd back into scripts folder
cd scripts

sudo service apache2 restart
echo "Application has been deployed. Please restart apache if needed." 
