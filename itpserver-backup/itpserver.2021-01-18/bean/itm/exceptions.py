# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-03-18 10:20:38
File Name: exceptions.py @v2.0
"""
import logging
import traceback

from django.conf import settings
from django.utils.encoding import force_str
from django.utils.translation import ugettext_lazy as _
from elasticsearch.exceptions import ConnectionError, TransportError, ConnectionTimeout, RequestError

from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, AuthenticationFailed, ValidationError, NotAuthenticated, MethodNotAllowed

import status


logger = logging.getLogger(__name__)


class APIBaseError(APIException):
    status_code = 200
    default_status, default_detail = status.API_BASE_ERROR

    def __init__(self, detail=None, status=None):
        # super(APIBaseError, self).__init__(self.detail, self.status)
        self.detail = detail or self.default_detail
        self.status = status or self.default_status

    def __str__(self):
        return force_str(self.detail)


class APINotRigister(APIBaseError):
    default_status, default_detail = status.API_NOT_RIGISTER


class APIINPUTERROR(APIBaseError):
    default_status, default_detail = status.API_INPUT_ERROR


class APINULLFileUpload(APIBaseError):
    default_status, default_detail = status.API_NULL_FILE_UPLOAD


class APIDataNotFound(APIBaseError):
    default_status, default_detail = status.API_DATA_NOT_FOUND


class APIESCONNERROR(APIBaseError):
    default_status, default_detail = status.API_ES_CONNECT_ERROR


class APIESQUERYERROR(APIBaseError):
    default_status, default_detail = status.API_ES_QUERY_ERROR


class APIOBJECTERROR(APIBaseError):
    default_status, default_detail = status.API_OBJECT_ERROR


class APIPASSWORDERROR(APIBaseError):
    default_status, default_detail = status.API_PASSWORD_ERROR


class APINAMEERROR(APIBaseError):
    default_status, default_detail = status.API_NAME_ERROR


def get_exc_attr(exc, attr1, attr2):
    return getattr(exc, attr1, getattr(exc, attr2))


def api_exception_handler(exc, context):
    if isinstance(exc, (ValidationError, APIBaseError, NotAuthenticated, AuthenticationFailed, MethodNotAllowed)):
        trace = 'No traceback.'
        if settings.DEBUG or settings.USE_DEBUG_LOG:
            print("-------------------------------------------")
            print("This is exc handler print exc info in debug")
            traceback.print_exc()
            print("-------------------------------------------")
    else:
        if isinstance(exc, (ConnectionError)):
            trace = "ES is not ready!!!"
        else:
            trace = '\n' + traceback.format_exc()
    logger.error("Framework_exception:{} str:{} {}".format(type(exc), exc, trace))

    if isinstance(exc, ConnectionError):
        # Caught exc for es conncetion error.
        return Response({"status": APIESCONNERROR.default_status, "detail": APIESCONNERROR.default_detail})

    elif isinstance(exc, (TransportError, RequestError)):
        # Caught exc for es transport error.
        return Response({"status": APIESQUERYERROR.default_status, "detail": exc.error})

    elif isinstance(exc, ConnectionTimeout):
        # Caught exc for es transport error.
        return Response({"status": APIESQUERYERROR.default_status, "detail": exc.error})

    elif isinstance(exc, NameError):
        # Caught exc for python name error.
        return Response({"status": APINAMEERROR.default_status, "detail": exc.message})

    elif isinstance(exc, TypeError):
        # Caught exc for python type error.
        return Response({"status": APIBaseError.default_status, "detail": APIINPUTERROR.default_detail})

    elif isinstance(exc, APIBaseError):
        # Caught exc for api base error.
        return Response({"status": exc.status, "detail": exc.detail})

    elif isinstance(exc, (AuthenticationFailed, ValidationError, ValueError, IndexError)):
        # Caught exc for api auth error.
        return Response({"status": APIBaseError.default_status, "detail": get_exc_attr(exc, 'detail', 'message')})

    response = exception_handler(exc, context)

    if response:
        # Return response for unknow error.
        response.data['status'] = getattr(exc, "status", 1)
    else:
        traceback.print_exc()
        logger.error(_("Uncaught exception: {}".format(exc)))

    return response
