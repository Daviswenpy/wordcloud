# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-04-09 18:26:12
File Name: removed.py @v1.1
"""
import time
import json
import datetime
import signature
import base64 as b64
from functools import wraps

from rest_framework.exceptions import MethodNotAllowed


def replaceAll(old, new, str):
    while str.find(old) > -1:
        str = str.replace(old, new)
    return str


def with_str(str_func):
    def wrapper(f):
        class FuncType:

            def __call__(self, *args, **kwargs):
                return f(*args, **kwargs)

            def __str__(self):
                return str_func()
        return wraps(f)(FuncType())
    return wrapper


def check_time(user_timestamp, time_deviation=600):
    if isinstance(user_timestamp, int):
        timeseconds = time.mktime(datetime.datetime.now().timetuple())
        if timeseconds - time_deviation < user_timestamp < timeseconds + time_deviation:
            return True
        else:
            return False
    else:
        return False


def check_method(*pk_list):
    def decorator(view_func):
        def _wrapper_view(request, deviceID, pk):
            if pk in pk_list:
                return view_func(request, deviceID, pk)
            raise MethodNotAllowed(request.method)
        return _wrapper_view
    return decorator


class ParametersCheck(object):

    @staticmethod
    def typeassert(*types, **typesdict):
        """
        Func Parameters Type assert.
        """
        def decorate(func):
            def wrapper(*args, **kwargs):
                for i, v in enumerate(types):
                    if not isinstance(args[i], v):
                        raise Exception(
                            "Need a {} where {} is not.".format(v.__name__, args[i]))
                for parm in typesdict:
                    if kwargs.get(parm, None) is None:
                        raise Exception("Need parameter {}.".format(parm))
                    if not isinstance(kwargs[parm], typesdict[parm]):
                        raise Exception('Need a {} for {} where {} is not.'.format(
                            typesdict[parm].__name__, parm, kwargs[parm]))
                return func(*args, **kwargs)
            return wrapper
        return decorate


def typeassert(*type_args, **type_kwargs):
    def decorate(func):
        sig = signature(func)
        bound_types = sig.bind_partial(*type_args, **type_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError('Argument {} must be {}'.format(name, bound_types[name]))
            return func(*args, **kwargs)
        return wrapper
    return decorate


def json_load_byteified(file_handle):
    return _byteify(json.load(file_handle, object_hook=_byteify), ignore_dicts=True)


def json_loads_byteified(json_text):
    return _byteify(json.loads(json_text, object_hook=_byteify), ignore_dicts=True)


def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


def decrypt(secret, key):
    """
    decrypt for mysql-beat
    """
    tips = b64.b64decode(secret.encode()).decode()

    lkey = len(key)
    secret = []
    num = 0
    for each in tips:
        if num >= lkey:
            num = num % lkey
        secret.append(chr(ord(each) ^ ord(key[num])))
        num += 1
    return "".join(secret)


class RestrictAdminByIpMiddleware(object):
    """
    This middleware-class will blocked all the /admin request if :
    # not in DEBUG # the client IP is not in settings.INTERNAL_IPS
    # new version for django 1.10.x
    """
    pass
    # def process_request(self, request):
    #     try:
    #         admin_index = reverse('admin:index')
    #     except NoReverseMatch:
    #         return
    #     if not request.path.startswith(admin_index):
    #         return
    #     ip = get_ip(request)
    #     if ip not in settings.INTERNAL_IPS and not settings.DEBUG:
    #         # PermissionDenied(detail='You do not have permission to perform this action.')
    #         raise Http404


# class Input2Kwargs(RestfulMiddlewareMixin):
#     """
#     """
#     def __init__():
#         pass


# def get_all(self, start=None, deviceID=None, sip=None, histdays=0):
#     """
#     Simple abstraction on top of the scroll() api - a simple iterator that yields all hits as returned by underlining scroll requests.
#     """
#     start = start or simple_datetime(None, int)
#     data = {
#         "query": {
#             "bool": {
#                 # "must": [{"exists": {"field": "sourceIp"}}],
#                 "filter": [
#                     {
#                         "range": {
#                             "timestamp": {
#                                 "gte": (start - histdays * 24 * 60 * 60) * 1000,
#                                 "lte": start * 1000
#                             }
#                         }
#                     },
#                     # {"term": {"timestamp": start*1000}},
#                     {
#                         "term": {
#                             "deviceID.keyword": deviceID
#                         }
#                     },
#                     {
#                         "term": {
#                             "sip.keyword": sip
#                         }
#                     }
#                 ],
#                 # "must_not": must_not,
#             }
#         }
#     }
#     es_result = scan(client=self.es_client, index=self.index, doc_type=self.doc_type, query=data)
#     return es_result

# def get_arsf_data(scores_orm, deviceID, pk, timestamp, user, **kwargs):
#     es_result = scores_orm
#     # try:
#     #     data = {}
#     #     es_result = scores_orm.get_all(timestamp, deviceID, user)
#     #     df = pd.DataFrame(es_result)
#     #     df = pd.DataFrame(df.ix[:, "_source"].values.tolist())
#     #     hist_list = [simple_datetime(i, str, True) for i in range(timestamp - 24 * 3600 * 7, timestamp, 24 * 3600)]  # [::-1]]
#     #     df['hist_timestamp'] = [hist_list] * df.index.size
#     #     df = df.drop(['deviceID'], axis=1)
#     #     df['history_dests'].apply(lambda x: _refun(x))
#     #     df['history_bytes'].apply(lambda x: _refun(x))
#     #     df['history_flow'].apply(lambda x: _refun(x))
#     #     df = df.fillna(0)
#     #     data[pk] = df.set_index('sip').to_dict('records')
#     #     return data
#     # except KeyError:
#     #     return {pk: []}
#     # except:
#     #     logger.exception('deviceID:{} timestamp:{} user: {}\n'.format(deviceID, timestamp, user))
#     #     return {}


def set_value(dictionary, keys, value):
    """
    Similar to Python's built in `dictionary[key] = value`,
    but takes a list of nested keys instead of a single key.

    set_value({'a': 1}, [], {'b': 2}) -> {'a': 1, 'b': 2}
    set_value({'a': 1}, ['x'], 2) -> {'a': 1, 'x': 2}
    set_value({'a': 1}, ['x', 'y'], 2) -> {'a': 1, 'x': {'y': 2}}
    """
    if not keys:
        dictionary.update(value)
        return

    for key in keys[:-1]:
        if key not in dictionary:
            dictionary[key] = {}
        dictionary = dictionary[key]

    dictionary[keys[-1]] = value


# def update_task(deviceID=None, device=None, pk=None, taskID=None, action=None, groupID=None, filename=None, sourceip=None, modelID_list=None):
#     """
#     Update task in celery.

#     deviceID: deviceID
#     pk == 'status' and device = None, do mrs_status_task
#     pk == None, do ars/mrs/ers_task
#     pk != None, do pk_task
#     """
#     try:
#         if pk == "upload":
#             upload_file.delay(**{"filename": filename, "sourceip": sourceip})

#         if pk == "custom_models":
#             notify_zodiac(deviceID, None, action, modelID_list)

#         if pk == "status":
#             mrs_status_task = {"type": 2, "deviceID": deviceID, "taskID": taskID, "action": action, "groupID": groupID}
#             mrs_task.delay(**mrs_status_task)

#         if device:
#             notify_zodiac(deviceID, device)

#             xrs_task = {"type": 1, "deviceID": deviceID}
#             if pk == "mrs" or pk is None:
#                 mrs_task.delay(**xrs_task)
#             # if pk == "ars" or pk is None:
#             #     xrs_task = {"type": 1, "deviceID": deviceID, "interval": device["itmConfigs"]["ars"]['interval'], "is_active": device["is_active"]}
#             #     ars_task.delay(**xrs_task)
#         return True
#     except ConnectionError:
#         logger.error("Get redis connection error, receive celery message failed.")
#     except:
#         logger.exception('pk:{} deviceID:{}\n'.format(pk, deviceID))
#         return False
