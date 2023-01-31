#!/usr/local/bin/python

import segno

cart = "4322cbdb-6b1c-45ca-b3dc-4ebab4656ff7"
lpn = "ZA222AZ"
epan = "02491012010011033016399619"
amount = 10000
url = f'http://192.168.71.164/carts/{cart}?lpn={lpn}&epan={epan}&amount={amount}&currency=EUR'
qrcode = segno.make(url)
print (url)
qrcode.save('./static/img/qr.svg')