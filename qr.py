#!/usr/local/bin/python

import segno

qrcode = segno.make('http://192.168.1.9/carts/5141e5e5-f30d-4707-bffa-b89abf958081?lpn=ZA321AZ&epan=02491012010011033016399611&amount=1480&currency=EUR&entry=20230226131545&authorize=20230318152535')
qrcode.save('./static/img/qr.svg')