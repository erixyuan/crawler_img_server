# !/usr/bin/python

import image_pb2
import sys

f = open('testfile','rb')
imageObj = image_pb2.Image()
imageObj.ParseFromString(f.read())

print imageObj.url

for item in imageObj.size:
    print item.width
    print item.height
    print item.file_extra_name
    print item.pngquant_quality
    print item.webp_quality