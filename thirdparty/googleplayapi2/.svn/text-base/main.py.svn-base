#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: main.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/02/05 11:17:51
"""

import sys

import config
import googleplay

def usage():
    usage = """
Usage: Interfaces for commnuniating with Googleplay [Commands]
Commands:
     details              - Get package's details. param: package name
     download             - Download package's APK. param: package name
     
     checkin              - Get a NEW android_id. Please configure items in conf/device.ini
                                param: device config file. default: ./conf/device.ini
     uploadDeviceConf     - Update device's configuration. Please configure "device" in conf/device.ini
                                param: device config file. default: ./conf/device.ini
    """
    print usage
    sys.exit(1)
    
    
def get_args():
    command, param = None, None 
    args = sys.argv
    if len(args) <= 1:
        usage()
    command = args[1].strip()
    param = None if len(args) <= 2 else args[2]
        
    COMMANDS = ['details', 'download', 'checkin', 'uploadDeviceConf']
    if command not in COMMANDS:
        print 'Unknown Command [%s]' % (command)
        usage()
    return (command, param)


def main():
    command, param = get_args()

    g_conf = config.GlobalConf(basic_conf='./conf/basic.ini',
                               device_conf='./conf/device.ini')

    api = googleplay.GooglePlayAPI(email=g_conf.basic.email,
                                   password=g_conf.basic.password,
                                   android_id=g_conf.basic.android_id,
                                   device_country=g_conf.basic.device_country,
                                   operator_country=g_conf.basic.operator_country,
                                   sdk=g_conf.basic.sdk,
                                   device=g_conf.basic.device,
                                   hardware=g_conf.basic.hardware,
                                   product=g_conf.basic.product,
                                   lang=g_conf.basic.lang,
                                   proxies=g_conf.basic.proxies)
    api.login(add_account=0)

    if command == 'details':
        assert param is not None, 'Please input package name'
        details = api.details(package_name=param)
        assert details is not None, 'Get details failed'
        api.print_message(details)
    elif command == 'download':
        assert param is not None, 'Please input package name'
        api.download(package_name=param)
    elif command == 'checkin':
        if param is not None:
            g_conf.reload_device_conf(conf_path=str(param))
        api.checkin(checkin_req=g_conf.get_checkin_req())
    elif command == 'uploadDeviceConf':
        if param is not None:
            g_conf.reload_device_conf(conf_path=str(param))
        api.upload_device_config(device_config_req=g_conf.get_device_config_req())
    else:
        print 'Unknown Command [%s]' % (command)
        usage()

if __name__ == "__main__":
    main()
