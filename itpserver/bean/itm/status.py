# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-03-16 14:13:14
File Name: status.py @v1.3
SOME NOTE: Descriptive HTTP status codes, for code readability.
"""
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _


def is_success(status):
    return status == 0


API_BASE_ERROR = (1, _('Basic error.'))
API_INPUT_ERROR = (2, _('Input error.'))
# API_AUTH_ERROR = (3, _('Authentication failed.'))
API_NOT_RIGISTER = (4, _('Not rigister.'))
API_NULL_FILE_UPLOAD = (5, _('No file upload.'))
API_DATA_NOT_FOUND = (6, _('Data not found.'))
API_ES_CONNECT_ERROR = (7, _('Elasticsearch Connection refused.'))
API_ES_QUERY_ERROR = (8, _('Elasticsearch query error.'))
API_OBJECT_ERROR = (9, _('Object error.'))
API_PASSWORD_ERROR = (10, _('Password error.'))


API_NAME_ERROR = (99, _('Unknown error or Name Error.'))
