#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: googleplay.py
Author: Rui Li(lirui05@baidu.com)
Date: 2015/01/27 23:31:53
"""

import sys
import time
import urllib
import requests
import base64
import StringIO
import gzip
from google.protobuf import text_format

import gp_pb2 as _message
import config


class GooglePlayAPI(object):
    """ APIs to connect with googleplay server
    """
    URL_PREFIX = 'https://android.clients.google.com'
    FDFE_URL = '%s/fdfe' % (URL_PREFIX)

    LOGIN_URL = '%s/auth' % (URL_PREFIX)
    CHECKIN_URL = '%s/checkin' % (URL_PREFIX)
    PURCHASE_URL = '%s/purchase' % (FDFE_URL)

    API_REQUEST_URL = '%s/market/api/ApiRequest' % (URL_PREFIX)

    def __init__(self, email=None, password=None, android_id=None, device_country=None, 
                 operator_country=None, sdk=None, device=None, hardware=None, product=None,
                 lang=None, proxies=None):
        self.email = email
        self.password = password
        self.android_id = android_id
        self.device_country = device_country
        self.operator_country = operator_country
        self.sdk = sdk
        self.device = device
        self.hardware=hardware
        self.product = product
        self.lang = lang
        self.proxies = proxies

        self.token = None
        self.auth_token = None

    def execute_request(self, url, data=None, headers=None, proxies=None, cookies=None, timeout=20):
        """ execute request
        """
        if proxies is None:
            proxies = self.proxies
        const_headers = {
            'Accept-Language': self.lang,
            'User-Agent': 'Android-Finsky/5.1.11 (api=3,versionCode=80310011,sdk=%s,device=%s,hardware=%s,product=%s)' % (
                self.sdk, self.device, self.hardware, self.product),
            'Authorization': 'GoogleLogin auth=%s' % (self.auth_token),
            'X-DFE-Client-Id': 'am-google',
            'X-DFE-Device-Id': self.android_id,
            'X-DFE-Filter-Level': '3',
            "X-DFE-Enabled-Experiments": "cl:billing.select_add_instrument_by_default",
            'X-DFE-Unsupported-Experiments': 'nocache:billing.use_charging_poller,market_emails,buyer_currency,prod_baseline,checkin.set_asset_paid_app_field,shekel_test,content_ratings,buyer_currency_in_app,nocache:encrypted_apk,recent_changes',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'android.clients.google.com'
        }
        if headers is not None:
            const_headers.update(headers)
        if data is not None:
            response = requests.post(url, data=data, headers=const_headers, 
                proxies=proxies, verify=False, cookies=cookies, timeout=20)
        else:
            response = requests.get(url, headers=const_headers, proxies=proxies, 
                timeout=20, cookies=cookies, verify=False)
        return (response.status_code, response.content)

    def login(self, add_account=0):
        """ login.
            Args:
                add_account: account bind to a new mobile device
        """
        if self.email is None or self.password is None or self.android_id is None:
            raise Exception('login error. email or password or android_id is None')
        
        if add_account == 1:
            self.auth(service='ac2dm', add_account=1)
        else:
            self.auth(service='androidmarket')

    def auth(self, service, **kwargs):
        """ authenticate with googleplay server. There are three types of services:
            1. ac2dm: for register
            2. androidsecure: auth to ensure operations from real mobile device
            3. androidmarket: login
        """
        if self.email is None  or self.android_id is None:
            raise Exception('login error. email or token or android_id is None')

        params = {'accountType': 'HOSTED_OR_GOOGLE',
                  'Email': self.email,
                  'androidId': self.android_id,
                  'has_permission': 1,
                  'service': service,
                  'source': 'android',
                  'app': 'com.android.vending',
                  'client_sig': '38918a453d07199354f8b19af05ec6562ced5788',
                  'device_country': self.device_country,
                  'operator_country': self.operator_country,
                  'lang': self.lang,
                  'RefreshServices': 1}
        if self.token is not None:
            params.update({'Token': self.token})
        else:
            params.update({'Passwd': self.password})
        params.update(kwargs)
        headers = {'User-Agent': 'GoogleLoginService/1.2 (%s)' % (self.device)}
        status_code, content = self.execute_request(url=GooglePlayAPI.LOGIN_URL,
                                                    data=urllib.urlencode(params),
                                                    headers=headers)

        if status_code == 200:
            res = {}
            for temp_content in content.split('\n'):
                index = temp_content.find('=')
                if index == -1:
                    continue
                res.update({temp_content[:index]: temp_content[index + 1:]})
            self.auth_token = res.get('Auth', None)
            self.token = res.get('Token', None)
        else:
            raise Exception('login error. code=%d, content="%s"' % (status_code, content))

    def checkin(self, checkin_req):
        """ Create a new AndroidId
        """
        def _checkin(data):
            headers = {'User-Agent': 'Android-Checkin/2.0 (%s); gzip' % (self.device),
                       'Content-Type': 'application/x-protobuffer',
                       'Accept-Encoding': 'gzip'
                       }
            status_code, content = self.execute_request(url=GooglePlayAPI.CHECKIN_URL,
                                                        data=data,
                                                        headers=headers)
            if not status_code == 200:
                return
            checkin_res = _message.AndroidCheckinResponse()
            checkin_res.MergeFromString(content)
            return checkin_res
        checkin_res = _checkin(checkin_req.SerializeToString())

        android_id = hex(checkin_res.androidId)
        security_token = hex(checkin_res.securityToken)
        self.token, self.auth_token = None, None
        self.auth(service='ac2dm')

        checkin_req.id = checkin_res.androidId
        checkin_req.securityToken = checkin_res.securityToken
        checkin_req.checkin.lastCheckinMsec = checkin_res.timeMsec
        checkin_req.accountCookie.append('[%s]' % (self.email))
        checkin_req.accountCookie.append(self.auth_token)
        _checkin(checkin_req.SerializeToString())

        print 'A NEW AndroidId has been created: %s' % (android_id)

    def upload_device_config(self, device_config_req):
        """ Update Device's Config. u must upload ALL config items
        """
        url = '%s/uploadDeviceConfig' % (GooglePlayAPI.FDFE_URL)
        config_data = device_config_req.SerializeToString()
        status_code, content = self.execute_request(url=url,
                                                    data=config_data)
        res = _message.ResponseWrapper()
        res.MergeFromString(content)
        print 'Update Succeed'
        print text_format.MessageToString(res)

    def sync_content(self):
        """ Same with Mobomarket's CheckUpdate
        """
        self.auth(service='androidsecure')
        req = _message.RequestProto()
        req_pro = req.requestProperties
        req_pro.userAuthToken = self.auth_token
        req_pro.userAuthTokenSecure = 1
        req_pro.softwareVersion = 80310011
        req_pro.aid = self.android_id
        req_pro.productNameAndVersion = '%s:%s' % (self.device, self.sdk)
        req_pro.userLanguage = 'en'
        req_pro.userCountry = 'GB'
        req_pro.operatorName = ''
        req_pro.operatorNumericName = ''
        req_pro.simOperatorName = 'INDOSAT'
        req_pro.simOperatorNumericName = '51001'
        req_pro.clientId = 'am-google'
        req_pro.loggingId = '6b83526ea91946db'

        request = req.request.add()
        purchase = request.purchaseMetadataRequest
        purchase_proto = _message.PurchaseMetadataRequestProto()
        purchase.MergeFromString(purchase_proto.SerializeToString())

        content_sync = request.contentSyncRequest
        req_str = req.SerializeToString()

        data = 'version=2&request=%s&' % (base64.b64encode(req_str))

        headers = {'User-Agent': 'Android-Market/2',
                   'X-Account-Ordinal': '1',
                   'X-Public-Android-Id': '7ab53a10834ed7dd',
                   }
        status_code, content = self.execute_request(url=GooglePlayAPI.API_REQUEST_URL, 
                                                    data=data, 
                                                    headers=headers)
        if status_code == 200:
            res = _message.ResponseProto()
            res.MergeFromString(gzip.GzipFile(fileobj=StringIO.StringIO(content)).read())
            print text_format.MessageToString(res)

    def details(self, package_name):
        """ Get a package's details
        """
        url = '%s/details?doc=%s' % (GooglePlayAPI.FDFE_URL, requests.utils.quote(package_name))
        status_code, content = self.execute_request(url=url)
        if status_code == 200:
            res = _message.ResponseWrapper()
            res.MergeFromString(content)
            return res.payload.detailsResponse

    def download(self, package_name, output_file=None):
        """ Download Apk
        """
        details = self.details(package_name=package_name)
        assert details is not None, 'Get details failed'
        version_code = details.docV2.details.appDetails.versionCode
        offer_type = details.docV2.offer[0].offerType
        url = '%s/purchase' % (GooglePlayAPI.FDFE_URL)
        data = 'doc=%s&ot=%d&vc=%d' % (requests.utils.quote(package_name), offer_type, version_code)
        headers = {
                   'X-DFE-Enabled-Experiments': 'cl:details.hide_download_count_in_title',
                   'X-DFE-Logging-Id': '6b83526ea91946db',
                   'X-Public-Android-Id': '7ab53a10834ed7dd'
                   }
        status_code, content = self.execute_request(url=url, data=data, headers=headers)
        if not status_code == 200:
            return 
        res = _message.ResponseWrapper()
        res.MergeFromString(content)

        url = res.payload.buyResponse.purchaseStatusResponse.appDeliveryData.downloadUrl
        cookie = res.payload.buyResponse.purchaseStatusResponse.appDeliveryData.downloadAuthCookie[0]
        cookies = {
            cookie.name : str(cookie.value)
        }
        headers = {'User-Agent': 'AndroidDownloadManager'}
        res = requests.get(url=url, headers=headers, cookies=cookies, verify=False, proxies=self.proxies,
                           timeout=30)
        if not res.status_code == 200:
            return
        if output_file is None:
            output_file = package_name
        with open(output_file, 'wb') as fd:
            fd.write(res.content)

    def replicate_library(self):
        req = _message.LibraryReplicationRequest()
        library_state = req.libraryState.add()
        library_state.corpus = 6
        library_state.serverToken = ''
        library_state.hashCodeSum = 0
        library_state.librarySize = 0
        library_state.libraryId = '6'

        data = req.SerializeToString()
        url = '%s/replicateLibrary' % (GooglePlayAPI.FDFE_URL)
        headers = {'Content-Type': 'application/x-protobuf'}
        status, content = self.execute_request(url=url, data=data, headers=headers)

    def toc(self):
        url = '%s/toc' % (GooglePlayAPI.FDFE_URL)
        headers = {'X-DFE-Device-Config-Token': '1422351243946'}
        status_code, content = self.execute_request(url=url, headers=headers)

    def plus_profile(self):
        url = '%s/api/plusProfile' % (GooglePlayAPI.FDFE_URL)
        headers = {'User-Agent': 'Android-com.android.vending/5.1.11(api=4,sdk=%s,device=%s,hardware=%s,product=%s)' % (self.sdk, self.device, self.hardware, self.product)}
        status_code, content = self.execute_request(url=url, headers=headers)
        res = _message.ResponseWrapper()
        res.MergeFromString(content)
        self.print_message(res)

    def print_message(self, message):
        print text_format.MessageToString(message)


if __name__ == "__main__":
    pass

