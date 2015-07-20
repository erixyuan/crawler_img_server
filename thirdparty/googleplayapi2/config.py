#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: config.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/01/29 11:17:51
"""
import time
import ctypes
import ConfigParser
from google.protobuf import descriptor
from google.protobuf import text_format

import gp_pb2 as _message

_FieldDescriptor = descriptor.FieldDescriptor

class GlobalConf(object):
    """ Include two types of Configuration.
        1. basic: email, password, androidId, proxies and so. 
        2. device: complex device config items. to make a protobuffer message: AndroidCheckinRequest
    """
    class Basic(object):
        def __init__(self):
            self.email = None
            self.password = None
            self.android_id = None
            self.device_country = None
            self.operator_country = None
            self.sdk = None
            self.device = None
            self.hardware = None
            self.product = None
            self.lang = None
            self.proxies = None

        def load_conf(self, conf_path):
            cp = ConfigParser.SafeConfigParser()
            cp.read(conf_path)
            for key, value in cp.items('basic'):
                key = key.lower()
                if hasattr(self, key):
                    setattr(self, key, value)
            if self.proxies is not None:
                self.proxies = {'http': 'http://%s' % (self.proxies),
                        'https': 'https://%s' % (self.proxies)}

    class Device(object):
        def __init__(self):
            self.request = None

        @property
        def device(self):
            return self.request.deviceConfiguration

        def load_conf(self, conf_path):
            cp = ConfigParser.SafeConfigParser()
            cp.optionxform = str
            cp.read(conf_path)

            self.request = _message.AndroidCheckinRequest()
            self._fill_message(self.request, cp.items('req'))
            self._fill_message(self.request.checkin, cp.items('req.checkin'))
            self._fill_message(self.request.checkin.build, cp.items('req.checkin.build'))
            self.request.checkin.build.timestamp = int(time.time()) / 1000
            self._fill_message(self.request.deviceConfiguration, cp.items('req.device'))

        def _fill_message(self, message, kv_list):
            def _fill_field(field, field_value):
                value = None
                field_type, field_name = field.type, field.full_name
                if field_type in (_FieldDescriptor.TYPE_INT32, _FieldDescriptor.TYPE_SINT32,
                                  _FieldDescriptor.TYPE_SFIXED32, _FieldDescriptor.TYPE_INT64,
                                  _FieldDescriptor.TYPE_SINT64,  _FieldDescriptor.TYPE_SFIXED64):
                    value = int(field_value)
                elif field_type in (_FieldDescriptor.TYPE_UINT32, _FieldDescriptor.TYPE_FIXED32):
                    value = int(ctypes.c_int32(field_value).value)
                elif field_type in (_FieldDescriptor.TYPE_UINT64, _FieldDescriptor.TYPE_FIXED64):
                    value = int(ctypes.c_int64(field_value).value)
                elif field_type in (_FieldDescriptor.TYPE_FLOAT, _FieldDescriptor.TYPE_DOUBLE):
                    value = float(field_value)
                elif field_type in (_FieldDescriptor.TYPE_STRING, _FieldDescriptor.TYPE_BYTES):
                    value = str(field_value)
                elif field_type == _FieldDescriptor.TYPE_BOOL:
                    value = int(field_value)
                else:
                    raise Exception('unknown field[%s], type[%d]' % (field_name, field_type))
                return value

            message_fields = message.DESCRIPTOR.fields_by_name
            for key, value in kv_list:
                field = message_fields.get(key)
                if field is None:
                    continue
                label, type = field.label, field.type
                if type in [_FieldDescriptor.TYPE_GROUP, _FieldDescriptor.TYPE_MESSAGE,
                        _FieldDescriptor.TYPE_ENUM]:
                    raise Exception('cannot handler message[%], field[%]' % (
                        message.name, field.full_name))
                if label == _FieldDescriptor.LABEL_REPEATED:
                    value_list = value.split(';')
                    for value in value_list:
                        value = _fill_field(field, value)
                        getattr(message, key).append(value)
                else:    
                    value = _fill_field(field, value)
                    setattr(message, key, value)


    def __init__(self, basic_conf, device_conf):
        self.basic = GlobalConf.Basic()
        self.device = GlobalConf.Device()

        self.basic.load_conf(conf_path=basic_conf)
        self.device.load_conf(conf_path=device_conf)

    def reload_device_conf(self, device_conf):
        self.device.load_conf(conf_path=device_conf)

    def get_checkin_req(self):
        return self.device.request

    def get_device_config_req(self):
        device_str = self.device.device.SerializeToString()

        device_config_req = _message.UploadDeviceConfigRequest()
        device = device_config_req.deviceConfiguration
        device.MergeFromString(device_str)

        return device_config_req

if __name__ == "__main__":
    g_conf = GlobalConf(basic_conf='./conf/basic.ini',
                        device_conf='./conf/device.ini')
    
