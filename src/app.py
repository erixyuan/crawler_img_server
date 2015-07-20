#!/usr/bin/env/python
# coding:utf-8

import image_pb2
import sys
import json
import urllib
import hashlib  
import os
#图片解析模块
from img_resize import ImageResize

from flask import Flask
from flask import request
app = Flask(__name__)
homedir = os.getcwd()

@app.route('/')
def hello_world():
    return 'Hello World!'


def resize_compress_image(src_image, resolution, pngquant_quality, webp_quality, 
        pngquant_dest_image=None, webp_dest_image=None):
    """ resize图片并且进行压缩
        Args: 
            src_image: 原图本地地址
            resolution: resize尺寸, (width, height)
            pngquant_quality: pngquant压缩质量度
            webp_quality: webp压缩质量度
            pnguqnt_dest_image: pngquant压缩生成的文件
            webp_dest_image: webp压缩生成的文件
    """
    # resize
    width, height = resolution
    src_dir, src_name = os.path.split(src_image)
    src_file_name, src_file_ext = os.path.splitext(src_name)
    resize_image = os.path.join(src_dir, 
        '%s_%dx%d%s' % (src_file_name, width, height, src_file_ext))
    image_resize = ImageResize()
    image_resize.resize_image(src_image, width, height, resize_image)

    # pngquant_compress
    if pngquant_dest_image is None:
        pngquant_dest_image = os.path.join(src_dir, 
            '%s_%dx%d_pngquant%s' % (src_file_name, width, height, src_file_ext))
    try:
        if not src_file_ext == '.png':
            raise Exception
        image_resize.pngquant_compress(img_in=resize_image, img_out=pngquant_dest_image,
            quality=pngquant_quality)
    except:
        pngquant_dest_image = resize_image

    # webp_compress
    if webp_dest_image is None:
        webp_dest_image = os.path.join(src_dir, 
            '%s_%dx%d.webp' % (src_file_name, width, height))
    try:
        image_resize.webp_compress(img_in=resize_image, img_out=webp_dest_image,
            quality=webp_quality)
    except:
        log('fail to webp compress. local_img=[%s], webp_img=[%s]' % (
            resize_image, webp_dest_image), 'WARNING')
        webp_dest_image = None
    return (pngquant_dest_image, webp_dest_image)

def download_img(url):
    '''
        下载图片
        这边还要加上代码重试
    '''
    ext = url.split('.')[-1]
    imagName = hashlib.md5(url)
    tmpUrl = '%s/tmpImgae/%s.%s' % (homedir, imagName, ext)
    print tmpUrl
    urllib.urlretrieve(url, tmpUrl)
    return tmpUrl


@app.route('/api/imageResize')
def imageResize():
    '''
        图片处理模块
    '''
    #1 解析参数，获取post过来的值
    data = request.args.get('data', '')
    if data == '':
        retData = {
            'retCode': 0,
            'retMsg': '参数错误',
            'retCode': '',

        }
        return json.dumps(data)
    img = image_pb2.Image()
    img.ParseFromString(data)
    url = img.url
    if count(image.size) < 1:
        retData = {
            'retCode': 0,
            'retMsg': '参数错误',
            'retCode': '',

        }
        return json.dumps(data)


    return json.dumps(data)
    
    #2 下载图片
    local_image = download_img(url)
    image_dir, image_name, image_ext = self._os_path_split(local_image)
    imgHandler = img_resize()
    for item in image.size:
        width = item.width
        height = item.height
        file_extra_name = item.file_extra_name
        pngquant_quality = item.pngquant_quality
        webp_quality = item.webp_quality
        pngquant_dest_image = os.path.join(image_dir,
                '%s_%dx%d_pngquant%s%s' % (image_name, width, height, file_extra_name, image_ext))
        pngquant_image, webp_image = resize_compress_image(local_image, 
                (width, height), pngquant_quality, webp_quality, pngquant_dest_image)

    #2 压缩，resize 图片
    

    #3 上云平台
    

if __name__ == '__main__':
    app.debug = True
    app.run(port=8300)





'''
screenshot_resolutions = (
    (155, 204, '_15', '0-15', 50),
    (192, 341, '', '0-100', 50),
    (144, 256, '', '0-100', 50),
    (155, 204, '', '0-100', 50))

width, height, file_extra_name, pngquant_quality, webp_quality = resolution

'''