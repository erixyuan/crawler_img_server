#!/usr/bin/env python
# coding:utf-8
import Image
import math
import commands
import logging
import hashlib

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='run.log',
                filemode='w')
homedir = os.getcwd()

class ImageResize(object):
    """ 图片尺寸压缩
    """
    
    def download_img(self, url, imagName=''):
        '''
        下载图片
        '''
        ext = url.split('.')[-1]
        image_tmp_path = '%s/../data/tmp_imgae/%s.%s' % (homedir, imagName, ext)
        print image_tmp_path
        urllib.urlretrieve(url, image_tmp_path)
        return image_tmp_path


    def resize_image(self, path, new_width, new_height, image_name, product):
        """ 图片尺寸resize, 而且按照业务一定比原图小, 且图片比例一致
        """
        img = Image.open(path)
        img_width, img_height = img.size

        width_ratio = 1.0 * new_width / img_width
        height_ratio = 1.0 * new_height / img_height
        # 新尺寸比例与原图比例不一致, 保持原图比例且新图尺寸尽量与预期一致
        if not width_ratio == height_ratio:
            ratio = min(width_ratio, height_ratio)
            if ratio < 1:
                if width_ratio < height_ratio:
                    new_height = int(math.ceil(img_height * ratio))
                else:
                    new_width = int(math.ceil(img_width * ratio))
        new_img = img.resize(size=(new_width, new_height),
                             resample=Image.ANTIALIAS)
        ext = path.split('.')[-1]
        img_out = '%s/../data/%s/resize/%s_%dx%d.%s' % (homedir, product, image_name, new_width, new_height, ext)
        new_img.save(img_out)
        return img_out

    def pngquant_compress(self, img_in, img_out, quality='0-100'):
        """ 使用pngquant进行图片压缩
        """
        shell_cmd = "./thirdparty/pngquant-master/pngquant \"%s\" " \
            "-o \"%s\" --quality=%s --force" % (img_in, img_out, quality)
        status, output = commands.getstatusoutput(shell_cmd)
        if status != 0:
            err_str = "fail to use pngquant to compress image. [%s]!" % (img_in)
            logging.warn(err_str, "ERROR")
            raise Exception(err_str)
        return img_out

    def webp_compress(self, img_in, img_out, quality=75):
        """ 图片压缩至webp格式
        """
        shell_cmd = 'cwebp -q %d -o %s %s' % (quality, img_out, img_in)
        status, output = commands.getstatusoutput(shell_cmd)
        if not status == 0:
            err_str = 'fail to do web compress. image=[%s]' % (img_in)
            logging.warn(err_str, "ERROR")
            raise Exception(err_str)
        return img_out



if __name__ == '__main__':
    img_resize = ImageResize()


    product = 'mobomarket'
    token = 'token'
    mode = 0
    url = 'https://lh4.ggpht.com/UAL7o_8LQ9n7d3pFh9q-JYd1bUtC9K7u_LkAjvq64KU-Ik3f2l4x-zhYRksGOEsNWzA=h310-rw'
    images = [{
        width: 100,
        height:100,
    }]

    # 如果是二进制，先保存到一个临时目录下,再处理
    
    imagName = hashlib.md5(url)
    image_tmp_path = image_resize.download_img(url, imagName)
    for item in images:
        resize_path = image_resize.resize_image(image_tmp_path, item['width'], item['height'] ,imagName, product)


        
    # img_resize.resize_image('test.png', 130, 130, 'test_130x130.png')
    # img_resize.pngquant_compress('test_130x130.png', 'test_130x130_100.png', quality='0-100')

