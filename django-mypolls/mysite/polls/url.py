# -*- coding: utf-8 -*-
'''
User Name: wendong@skyguard.com.cn
Date Time: 12/30/20 10:47 AM
File Name: /
Version: /
'''

# polls/url.py

from django.conf.urls import include,url
from django.contrib import admin
from .views import *


app_name = 'polls'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name="polls-index"),
    url(r'^(?P<pk>[0-9]+)/$', DetailView.as_view(), name='detail'),
    # ex: /polls/5/results/
    url(r'^(?P<pk>[0-9]+)/results/$', ResultsView.as_view(), name='results'),
    # ex: /polls/5/vote/
    url(r'^(?P<question_id>[0-9]+)/vote/$', vote, name='vote'),
]