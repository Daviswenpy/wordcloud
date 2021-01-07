# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-05-17 16:25:50
File Name: uwsgi_test.py @v1.0
"""


def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ["Hello World"]
