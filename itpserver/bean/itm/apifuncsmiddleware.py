# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-11-13 16:37:11
File Name: apifuncsmiddleware.py @v3.3
SOME NOTE: this is django-restful-framework middleware(handler)
"""
import re
import json

from django.core.cache import cache

from itm import logger
from utils import is_valid_ip
from userinfo import UserInfo
from exceptions import APINotRigister, APIDataNotFound
from views import set_device, set_userId, check_pass
from elasticsearchorm import DeviceORM


class RestfulMiddlewareMixin(object):

    def __init__(self):
        pass


class USDisplayChange(RestfulMiddlewareMixin):
    """
    UserIdDisplayChange as USDC

    API:
        ers forensisc
        ars forensics
        scores
    """
    model = UserInfo

    def __init__(self, request, handler, **kwargs):
        if handler.im_class.__name__ in set_userId:
            data = request.data
            sip = data.get('user')
            if not re.match(r"(\w{8}(-\w{4}){3}-\w{12}?)", sip) and not is_valid_ip(sip):
                user_info = self.model(deviceID=kwargs['deviceID'])
                user_list = user_info.get_user_info(sip)
                if len(user_list) == 1:
                    data['user'] = user_list[0]
                    logger.info('api:USDC body:{}'.format(json.dumps(data)))
                else:
                    raise APIDataNotFound('username:{} parase error with user_list:{}'.format(sip, user_list), 1)


class DeviceIDCheck(RestfulMiddlewareMixin):
    """
    DeviceIDCheckMiddleware as DIDC

    API:
        All views func
    """
    model = DeviceORM

    def __init__(self, request, handler, **kwargs):
        self.deviceID = kwargs.get("deviceID", None)

        if self.deviceID:
            callback = handler.im_class.__name__

            if callback in check_pass and request.method == check_pass[callback]:
                # pass device check with regisiter device
                pass
            else:

                if callback in set_device:
                    # set device attr for some request
                    device = self._generate_cache()
                    setattr(request, "device", device)
                else:
                    is_active = cache.get(self.deviceID)
                    if is_active is None:
                        self._generate_cache()
                    elif is_active is False:
                        raise APINotRigister

    def _generate_cache(self):
        device_orm = self.model()
        device = device_orm.get_obj_or_404(self.deviceID)
        cache.set(self.deviceID, device['is_active'])
        return device


class JsonFormater(RestfulMiddlewareMixin):
    """
    To do json format with admin debug.
    """
    filter_field = ['pretty']

    def __init__(self, request, handler, **kwargs):
        self.default_param = True
        url_params = dict(request._request.GET)

        for param, value in url_params.items():
            if param == 'pretty':
                indent = 4
                try:
                    indent = int(value[0])
                except:
                    pass
                request.accepted_media_type += ';indent={}'.format(indent)


class APIDataCache(RestfulMiddlewareMixin):
    """
    Link cachemanager and caching.
    """
    model = None

    def __init__(self, request, handler, **kwargs):
        if self.model:
            pass

    def cache_manager(self, user, cache_key, cache_value):
        pass

    def caching(self, user, cache_key, cache_value):
        pass


class APIExcCache(RestfulMiddlewareMixin):
    """
    Caching exc info with timeout.
    """
    model = None

    def __init__(self, request, handler, **kwargs):
        if self.model:
            pass

    def cache_exc(self, exc, **kwargs):
        cache.set(exc, **kwargs)
