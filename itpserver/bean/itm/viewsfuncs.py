# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-01-24 17:07:12
File Name: viewsfuncs.py @v3.6
"""
import os
import json
import time

from socket import timeout
from redis import ConnectionError
from kombu.exceptions import InconsistencyError
from django.utils.translation import ugettext_lazy as _

from tasks import *
from itm import logger
from config import config
from utils import update_iptables, encrypt, ZodiacClient


__all__ = [
    'device_iptables_mapping',
    'mysql_beat',
    'run_time',
    'update_task',
]


def _check_expression(riskLevel_expression):
    # To do some check for riskLevel_expression later.
    raise DeprecationWarning(_("Use with pd func has some bug."))
    if not isinstance(riskLevel_expression, str):
        raise ValueError(_("riskLevel_expression must be string type, not {}".format(type(riskLevel_expression))))
    return riskLevel_expression.replace("|", "or").replace("&", "and").lower()


def device_iptables_mapping(action, deviceID, logSources):
    """
    Iptables and ucss_mapping

    action: "disable" or "enable"
    """
    try:
        update_iptables(action, deviceID, logSources)

        if action == "disable":
            with open(config.UCSS_MAPPING) as jf:
                ucss_mapping = json.load(jf)
            for i in logSources:
                if i in ucss_mapping:
                    del ucss_mapping[i]

        if action == "enable":
            try:
                with open(config.UCSS_MAPPING) as jf:
                    ucss_mapping = json.load(jf)
            except:
                ucss_mapping = {}
            for i in logSources:
                ucss_mapping[i] = deviceID

        with open(config.UCSS_MAPPING, "w") as jf:
            jf.write(json.dumps(ucss_mapping))
    except:
        logger.exception("Device iptables set and ucss mapping failed.")
    return True


def mysql_beat(use, deviceID='', logSources={}):
    """
    For mysql beat.
    """
    try:
        if use:
            sangfor_conf = []
            for i in logSources:
                if i['vendor'] == 'sangfor':
                    beat_config = i
                    beat_config['deviceID'] = deviceID
                    beat_config['passwd'] = encrypt(i.get('passwd', 'admin'), 'skyguard')
                    sangfor_conf.append(beat_config)

            with open(config.MYSQL_BEAT, 'w') as jf:
                jf.write(json.dumps({"sangfor_config": sangfor_conf}))

            os.system('systemctl restart mysql-beat')
            os.system('systemctl enable mysql-beat')

        else:
            for i in logSources:
                if i['vendor'] == 'sangfor':
                    os.system('systemctl stop mysql-beat')
                    with open(config.MYSQL_BEAT, 'w') as jf:
                        jf.write(json.dumps({}))
        return True
    except:
        logger.exception("Mysql beat action failed.")


def run_time(func):
    """
    Log runtime to log.
    """
    @wraps(func)
    def wrapper(*args, **kw):
        local_time = time.time()
        result = func(*args, **kw)
        logger.warning('current Function [%s] run time is %.2f' % (func.__name__, time.time() - local_time))
        return result
    return wrapper


def notify_zodiac(deviceID, device=None, operate=None, modelID_list=None):
    try:
        res = None
        zodiac = ZodiacClient(config.ZODIAC_URL)
        if operate and modelID_list:
            res = zodiac.update_custom_ers_models(operate, deviceID, modelID_list)
        else:
            if "is_active" in device:
                if device["is_active"]:
                    res = zodiac.add_device(deviceID)
                else:
                    res = zodiac.remove_device(deviceID)

            if "itmConfigs" in device:
                res = zodiac.update_config(deviceID)
    except timeout:
        pass
    except:
        logger.exception("")
    finally:
        logger.info("Receive XMLRPC message result is {}.".format(res))


def update_task(deviceID=None, device=None, pk=None, taskID=None, action=None, groupID=None, filename=None, sourceip=None, modelID_list=None):
    """
    Update task in celery.

    deviceID: deviceID
    pk == 'status' and device = None, do mrs_status_task
    pk == None, do ars/mrs/ers_task
    pk != None, do pk_task
    """
    try:
        if pk == "upload":
            upload_file.delay(**{"filename": filename, "sourceip": sourceip})

        if pk == "custom_models":
            notify_zodiac(deviceID, None, action, modelID_list)

        if pk == "status":
            mrs_status_task = {"type": 2, "deviceID": deviceID, "taskID": taskID, "action": action, "groupID": groupID}
            mrs_task.delay(**mrs_status_task)

        if device:
            notify_zodiac(deviceID, device)

            xrs_task = {"type": 1, "deviceID": deviceID}
            mrs_task.delay(**xrs_task)

        return True
    except ConnectionError:
        logger.error("Get redis connection error, receive celery message failed.")
    except InconsistencyError as e:
        logger.error(e.__dict__)
        logger.error("Cannot route message for exchange 'upload_file': Table empty or key no longer exists."
                     "Probably the key ('_kombu.binding.upload_file') has been removed from the Redis database.")
    except:
        logger.exception('pk:{} deviceID:{}\n'.format(pk, deviceID))
        return False
