# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-05-17 14:55:56
File Name: admin.py @v1.1
"""
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import *


class ProfileInline(admin.StackedInline):
    model = UserProfile
    verbose_name = 'passwordHash'


admin.site.register(Session)
admin.site.register(UserProfile)


# class UserAdmin(admin.ModelAdmin):
#     inlines = (ProfileInline,)


# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
# admin.site.register(User)
# admin.site.register(Device)
# admin.site.register(Tasks)
