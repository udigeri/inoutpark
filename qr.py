#!/usr/local/bin/python

import segno

cart = "aabe00d3-8db9-43af-8854-f27c1b82b9db"
lpn = "ZA940BB"
lpn = "ZA210LM"
lpn = "ZA181KR"
epan = "548510884433006888"
epan = "678451920077884111"
epan = "964557475522339666"
amount = 700
url = f'http://192.168.71.164/carts/{cart}?lpn={lpn}&epan={epan}&amount={amount}&currency=EUR'
qrcode = segno.make(url)
print (url)
qrcode.save('./static/img/qr.svg')