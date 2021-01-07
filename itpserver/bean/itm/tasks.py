# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-01-24 17:07:12
File Name: tasks.py @v2.0
"""
from celery import task
from django.utils.translation import ugettext_lazy as _


__all__ = [
    'mrs_task',
    'upload_file'
]


# @task(name='ers_task')
# def ers_task(**task):
#     return _("Update")


@task(name='mrs_task')
def mrs_task(**task):
    return _("Update")


# @task(name='ars_task')
# def ars_task(**task):
#     return _("Update")


@task(name='upload_file')
def upload_file(**task):
    return _("Update")


# class XrsTask(Task):
#     abstract = True
#     default_retry_delay = 1
#     max_retries = 3
#     ignore_result = True
#     task_time_limit = 15
#     acks_late = True
