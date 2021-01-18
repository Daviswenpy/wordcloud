# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-01-25 12:53:22
File Name: apibasicmiddleware.py @v3.2
SOME NOTE: this is django middleware
"""
import sys
import json
import logging
from urlparse import parse_qs

from django.http import Http404
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.views.debug import technical_500_response
from django.core.urlresolvers import reverse, NoReverseMatch

from utils import get_ip


logger = logging.getLogger(__name__)


def debuglog(request, response):
    LOG_SKIP = {'static-files'}
    try:
        ip = get_ip(request)
        if request.path_info.startswith('/static/'):
            viewname = 'static-files'
        else:
            try:
                viewname = request.resolver_match.url_name
            except:
                viewname = 'URLParseError'

        if viewname not in LOG_SKIP:
            key = 'JSONAPI'
            if request.method in {'GET', 'DELETE'}:
                data = body = ""
            elif request.FILES == {}:
                data = '[BODY] '
                body = 'NO FILENAME'
                if hasattr(request, 'body'):
                    try:
                        body = json.dumps(json.loads(request.body))
                    except:
                        body = request.body
            else:
                data = '[FILE] '
                body = 'FILE instance'
            message = data + body
            message = message + "\n" if message != "" else message
            if viewname == 'x-scores' and not response.exception:
                try:
                    user_size = len(json.loads(getattr(response, 'content', '{"status": response.status_code}')).get('riskLevel', {}).get('scores', {}))
                    resp_data = {"user_size": user_size}
                except:
                    resp_data = {"detail": "Get scores info failed."}
            elif viewname == 'xrs_forensics' and not response.exception:
                resp_data = {"log_pass": True}
            else:
                if hasattr(response, 'accepted_media_type') and 'text' not in response.accepted_media_type and 'html' not in response.accepted_media_type:
                    resp_data = getattr(response, 'content', {"status": response.status_code})
                else:
                    try:
                        resp_data = json.dumps(getattr(response, 'data', {"status": response.status_code}))
                        key = 'BrowsableAPI'
                    except:
                        resp_data = getattr(response, 'content', {"status": response.status_code})

            logger.debug('{}:{} {} {} {}\n{}[DATA] {}\n'.format(key, viewname, request.method, request.path, ip, message, resp_data))
    except:
        logger.exception('Error for debuglog.\n')


class WebAppDebugLogMiddleware(MiddlewareMixin):# debug log, before return response
    """
    Middleware to debug log.
    """

    def init(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):

        hasattr(request, 'body')

        response = self.get_response(request)

        debuglog(request, response)

        return response


class RestrictAdminByIpMiddleware(MiddlewareMixin):
    """
    This middleware-class will blocked all the /admin request if :
    # not in DEBUG # the client IP is not in settings.INTERNAL_IPS
    # new version for django 1.10.x
    """

    def init(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        try:
            admin_index = reverse('admin:index')

            if request.path.startswith(admin_index):
                ip = get_ip(request)
                admin_string = parse_qs(request.META.get('QUERY_STRING')).get('ip', None)

                if admin_string:
                    admin_string = admin_string[0]
                    ip = admin_string

                if ip not in settings.INTERNAL_IPS:
                    raise Http404
        except NoReverseMatch:
            pass

        response = self.get_response(request)

        return response


class AdminExceptRaiseMiddleware(MiddlewareMixin): # is_superuser?
    """
    Raise except for admin user with django technical 500 response.
    """

    def process_exception(self, request, exception):
        """
        Middleware displays bug information when the request comes from an superuser or INTERNAL_IPS user.
        """
        # print(request.user.is_superuser or get_ip(request) in settings.INTERNAL_IPS)
        if request.user.is_superuser or get_ip(request) in settings.INTERNAL_IPS:
            return technical_500_response(request, *sys.exc_info())


class IpForbitMiddleWare(MiddlewareMixin):
    """
    Middleware to prevent access to the server if the user IP isn't in the network.
    """

    def process_request(self, request):
        ip = get_ip(request)
        if not ip.startswith('172.') and not ip.startswith('10.'):
            # PermissionDenied(detail='You do not have permission to perform this action.')
            raise Http404
