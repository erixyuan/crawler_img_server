#!/usr/bin/env/python
# coding:utf-8
import image_pb2
import sys


f = open('testfile', "rb")


imageObj = image_pb2.Image()
imageObj.ParseFromString(f.read())
f.close()

imageObj.url = "http://www.baidu.com"
size = imageObj.size.add()
size.width = 155
size.height = 204
size.file_extra_name = '_15'
size.pngquant_quality = '0-15'
size.webp_quality = 50

data = imageObj.SerializeToString()
print data
f = open('testfile', "wb")
f.write(data)




'''
screenshot_resolutions = (
    (155, 204, '_15', '0-15', 50),
    (192, 341, '', '0-100', 50),
    (144, 256, '', '0-100', 50),
    (155, 204, '', '0-100', 50))

width, height, file_extra_name, pngquant_quality, webp_quality = resolution

'''