#!/usr/local/bin/python

import segno

cart = "f05a2384-438a-45f3-819e-11be411a372e"
lpn = "ZA987AZ"
epan = "02491012010011033016399615"
amount = 1700
url = f'http://192.168.71.164/carts/{cart}?lpn={lpn}&epan={epan}&amount={amount}&currency=EUR'
qrcode = segno.make(url)
print (url)
qrcode.save('./static/img/qr.svg')