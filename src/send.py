#!/usr/bin/env/python
# coding:utf-8

import urllib

import image_pb2



def main():

    f = open('testfile','rb')
    data = f.read()


    parmas = urllib.urlencode({'data':data)
    urlret=urllib.urlopen("http://python.org/query",parmas)
    print urlret.read()

if __name__ == '__main__':
    main()