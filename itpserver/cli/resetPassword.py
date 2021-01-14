#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
sys.path.append("/opt/skyguard/www/app")
sys.path.append("/opt/skyguard/app/modules/cli")

import json
import utils
from common import *
from sps_client import SPS_CLIENT, SPS_ADDR, SPS_PORT_SSL

password_re = "^(?=.{10,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\\W).*$"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "/opt/skyguard/app/modules/cli/resetPassword.py <username> <unlock/passwd>"
        sys.exit(0)
    username = sys.argv[1]
    action = sys.argv[2]
    if action == "unlock":
        client = SPS_CLIENT(SPS_ADDR, SPS_PORT_SSL)
        ret = client.unlock_admin(username)
        if isinstance(ret, str):
            ret = json.loads(ret)
        if ret.has_key("responseCode"):
            if ret["responseCode"] == 0:
                print u'解锁成功'.encode("utf-8")
            elif ret["responseCode"] == -1:
                print u'参数错误，用户名未输入'.encode("utf-8")
            elif ret["responseCode"] == -2:
                print u'用户名不存在'.encode("utf-8")
            elif ret["responseCode"] == -3:
                print u'解锁失败'.encode("utf-8")
            else:
                print u'内部错误'.encode("utf-8")
        else:
            print u'内部错误'.encode("utf-8")
        sys.exit(0)
    elif action == "passwd":
        password = input_password(u'请输入新密码：'.encode("utf-8"), 32)
        ret = re.match(password_re, password)
        while ret == None:
            print u'密码强度弱，10-32位字符，数字、字母、大小写、特殊字符各一'.encode("utf-8")
            password = input_password(u'请输入新密码：'.encode("utf-8"), 32)
            ret = re.match(password_re, password)
        password_confirm = input_password(u'请再次输入密码：'.encode("utf-8"), 32)
        while password != password_confirm:
            print u'两次密码输入不同，请重新输入'.encode("utf-8")
            password = input_password(u'请输入新密码：'.encode("utf-8"), 32)
            ret = re.match(password_re, password)
            while ret == None:
                print u'密码强度弱，10-32位字符，数字、字母、大小写、特殊字符各一'.encode("utf-8")
                password = input_password(u'请输入新密码：'.encode("utf-8"), 32)
                ret = re.match(password_re, password)
            password_confirm = input_password(u'请再次输入密码：'.encode("utf-8"), 32)
        client = SPS_CLIENT(SPS_ADDR, SPS_PORT_SSL)
        ret = client.reset_password(username, password)
        if isinstance(ret, str):
            ret = json.loads(ret)
        if ret.has_key("responseCode"):
            if ret["responseCode"] == 0:
                print u'密码重置成功'.encode("utf-8")
            elif ret["responseCode"] == -1:
                print u'参数错误，用户名或密码未输入'.encode("utf-8")
            elif ret["responseCode"] == -2:
                print u'用户名不存在'.encode("utf-8")
            elif ret["responseCode"] == -3:
                print u'密码重置失败'.encode("utf-8")
            else:
                print u'内部错误'.encode("utf-8")
        else:
            print u'内部错误'.encode("utf-8")
        sys.exit(0)

