# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-05-17 16:23:43
File Name: itm_user.py @v1.0
"""
import os
import sys
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bean.settings")
django.setup()


from itm.models import *
from django.contrib.auth.models import User


def add_user(username, password):
    user = User.objects.create_user(username)
    userpro = UserProfile.objects.create(user=user)
    userpro.set_passwordHash(password)


username = sys.argv[1]
password = sys.argv[2]
add_user(username, password)
