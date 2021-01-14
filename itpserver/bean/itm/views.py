# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-06-29 10:48:32
File Name: views.py @v1.0
"""
from .views001 import *
from .views002 import *
from .views003 import *
from .views004 import *
from .views005 import *
from .views006 import *


# settings for set attr for request in apifuncs
set_device = {'itm_configs', 'configuration', 'conf_xrs', 'mrs_tasks'}
set_userId = {'xrs_forensics'}
check_pass = {'register': 'POST'}


# __all__ = ['set_device', 'set_userId', 'check_pass', '*']
