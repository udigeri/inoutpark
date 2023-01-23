#!/usr/local/bin/python

import segno

qrcode = segno.make('http://192.168.1.149:5547/a56dfd2f-1216-4d74-b4a0-798e12286469')
qrcode.save('./img/qr.svg')