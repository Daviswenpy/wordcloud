# -*- coding: utf-8 -*-
'''
User Name: wendong@skyguard.com.cn
Date Time: 11/25/20 4:04 PM
File Name: /
Version: V1.0
'''
import requests
import base64
import datetime
import time
import hashlib
import os
import django
from django.urls import reverse
import pytest
os.environ.setdefault("DJANGO_SETTINGS_MODULE","bean.settings")
django.setup()
from itm.removed import json_loads_byteified

clientIP = "127.0.0.1"
username = "itm-admin"
deviceID_test = "test-deviceID"
deviceID_BJ = "4cc167d1-183d-19e1-eb25-ec655080fb23"
deviceID_CD = "66a84d56-c747-998a-709e-b2b159a4cd86"
filename = "test-filname"
modelID = ""
anomalyID = ""
taskID = ""
base_url = "http://127.0.0.1:8000/ITMCP/v1/"
session_url = base_url + "sessions"
device_url = base_url + "devices/" + deviceID_CD

time_now = time.mktime(datetime.datetime.now().timetuple())
password = hashlib.sha256("itm-admin").hexdigest()
hash_str = hashlib.sha256(username + str(int(time_now)) + password).hexdigest()
passwordHash = base64.b64encode(hash_str)[:12]
login_data = {
        "username": username,
        "timestamp": int(time_now),
        "passwordHash": passwordHash,
        "deviceType": 1,
        "connectionType": 0
    }


# everytime the module run, setup_module run first, for once
def setup_module():
    print "Getting session..."
    response = requests.post(session_url + reverse('check-in'), json=login_data)
    globals()['sessionID'] = response.json().get('sessionID')
    globals()['clientIP'] = response.json().get('clientIP')
    globals()['headers'] = {'Authorization': 'basic ' + base64.b64encode(clientIP + ":" + sessionID)}

# before the module end, teardown_module run, for once
def teardown_module():
    pass


class TestCheckIn:
    """
    checkin,base operation,post
    """

    def post_checkin(self):
        time_now = time.mktime(datetime.datetime.now().timetuple())
        url = session_url
        password = hashlib.sha256(username).hexdigest()
        hash_str = hashlib.sha256(username + str(int(time_now)) + password).hexdigest()
        passwordHash = base64.b64encode(hash_str)[:12]
        body = {
        "username": username,
        "timestamp": int(time_now),
        "passwordHash": passwordHash,
        "deviceType": 1,
        "connectionType": 0
            }
        res = requests.post(url,json=body)
        print "-"*50
        print "POST ", "API: ", "check-in", res.status_code, url
        print "[BODY] ", body
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-"*50
        return data["sessionID"]


class LoginOut:
    """
    keepalive or log-out,get or delete
    """

    def __init__(self,sessionID):
        self.url = session_url + "/" + sessionID

    def keppalive(self):
        res = requests.get(self.url, headers=headers)
        print "-" * 50
        print "GET ", "API: ", "login-out", res.status_code
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50

    def login_out(self):
        res = requests.delete(self.url, headers=self.headers)
        print "-" * 50
        print "DELETE ", "API: ", "login-out", res.status_code, self.url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50

class Register:
    """
    add/delete device,post or delete
    """

    def __init__(self,device_url):
        self.url = device_url

    def post_register(self):
        body = {
        "deviceID": deviceID_CD,
        "deviceName": "test-ucss",
        "logSources": []
            }
        res = requests.post(self.url, headers=headers, json=body)
        print "-" * 50
        print "POST ", "API: ", "register", res.status_code, self.url
        print "[BODY] ", body
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50

    def delete_register(self):
        res = requests.delete(self.url, headers=headers)
        print "-" * 50
        print "DELETE ", "API: ", "register", res.status_code, self.url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50


class ItmConfigs:
    """
    mainly setup field:interval,xrs-chosenGroup,blacklist with different types,post
    """

    def __init__(self):
        self.url = device_url + "/configurations/itmConfigs"

    def post_itmConfigs(self):
        body = {
            "ars": {
                "subsystems": [],
                "interval": 7200,
                "chosenGroups": [],
                "blacklist": [
                    {
                        "type": 1,
                        "value": []
                    },
                    {
                        "type": 2,
                        "value": []
                    },
                    {
                        "type": 3,
                        "value": []
                    },
                    {
                        "type": 4,
                        "value": []
                    },
                    {
                        "type": 5,
                        "value": []
                    }
                ],
                "topN": 0,
                "version": 0
            },
            "mrs": {
                "chosenDLPPolicies": [],
                "interval": 7200,
                "blacklist": [
                    {
                        "type": 1,
                        "value": []
                    },
                    {
                        "type": 2,
                        "value": []
                    },
                    {
                        "type": 3,
                        "value": []
                    },
                    {
                        "type": 4,
                        "value": []
                    },
                    {
                        "type": 5,
                        "value": []
                    }
                ],
                "topN": 0,
                "version": 0,
                "uploadToLab": True,
                "retrospectiveDays": 7
            },
            "ers": {
                "interval": 7200,
                "ChosenModels": [],
                "modelParameterMap": [],
                "blacklist": [
                    {
                        "type": 1,
                        "value": []
                    },
                    {
                        "type": 2,
                        "value": []
                    },
                    {
                        "type": 3,
                        "value": []
                    },
                    {
                        "type": 4,
                        "value": []
                    },
                    {
                        "type": 5,
                        "value": []
                    }
                ],
                "topN": 0,
                "version": 1
            }
            }
        res = requests.post(self.url, headers=headers, json=body)
        print "-" * 50
        print "POST ", "API: ", "itm-configs", res.status_code, self.url
        print "[BODY] ", body
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50


class ConfXrs:
    """
    enable/disable ers/mrs models,get or post
    """

    def __init__(self):
        self.url = device_url + "/configurations/itmConfigs/"

    def post_confErs(self):
        body = {
            "interval": 7200,
            "ChosenModels": [],
            "modelParameterMap": [],
            "blacklist": [
                {
                    "type": 1,
                    "value": []
                },
                {
                    "type": 2,
                    "value": []
                },
                {
                    "type": 3,
                    "value": []
                },
                {
                    "type": 4,
                    "value": []
                },
                {
                    "type": 5,
                    "value": []
                }
            ],
            "topN": 0,
            "version": 1
            }
        self.url = self.url + "ers"
        res = requests.post(self.url, headers=headers, json=body)
        print "-" * 50
        print "POST ", "API: ", "conf-xrs", res.status_code, self.url
        print "[BODY] ", body
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50

    def post_confMrs(self):
        body = {
            "chosenDLPPolicies": [],
            "interval": 7200,
            "blacklist": [
                {
                    "type": 1,
                    "value": []
                },
                {
                    "type": 2,
                    "value": []
                },
                {
                    "type": 3,
                    "value": []
                },
                {
                    "type": 4,
                    "value": []
                },
                {
                    "type": 5,
                    "value": []
                }
            ],
            "topN": 0,
            "version": 0,
            "uploadToLab": True,
            "retrospectiveDays": 7
            }
        self.url = self.url + "mrs"
        res = requests.post(self.url, headers=headers, json=body)
        print "-" * 50
        print "POST ", "API: ", "conf-xrs", res.status_code, self.url
        print "[BODY] ", body
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50

    def post_confArs(self):
        body = {
            "subsystems": [],
            "interval": 7200,
            "chosenGroups": [],
            "blacklist": [
                {
                    "type": 1,
                    "value": []
                },
                {
                    "type": 2,
                    "value": []
                },
                {
                    "type": 3,
                    "value": []
                },
                {
                    "type": 4,
                    "value": []
                },
                {
                    "type": 5,
                    "value": []
                }
            ],
            "topN": 0,
            "version": 0
            }
        self.url = self.url + "ars"
        res = requests.post(self.url, headers=headers, json=body)
        print "-" * 50
        print "POST ", "API: ", "conf-xrs", res.status_code, self.url
        print "[BODY] ", body
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50

    def post_blacklist(self):
        pass

    def get_blacklist(self):
        """return blacklist info"""
        # e.g. ars/blacklists
        self.url = self.url + "ars/blacklists"
        res = requests.get(self.url, headers=headers)
        print "-" * 50
        print "GET ", "API: ", "conf-xrs", res.status_code, self.url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50

    def get_version(self):
        self.url = self.url + "versions"
        res = requests.get(self.url, headers=headers)
        print "-" * 50
        print "GET ", "API: ", "conf-xrs", res.status_code, self.url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50


class Configurations:
    """
    get models config info,get
    """

    def get_configurations(self):
        url = device_url + "/configurations"
        res = requests.get(url, headers=headers)
        print "-" * 50
        print "GET ", "API: ", "configurations", res.status_code, url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50


class UploadFile:
    """
    upload tar file,source from some ip which excludes UCSS,post
    """

    def __init__(self):
        self.url = base_url + "upload/files/"

    def post_file(self):
        body = {
            "filename": filename
        }
        res = requests.post(self.url, headers=headers, json=body)
        print "-" * 50
        print "POST ", "API: ", "upload-file", res.status_code, self.url
        print "[BODY] ", body
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50


class DownloadFile:
    """
    download file
    """

    def __init__(self):
        self.url = base_url + "download/files/"

    def get_file(self):
        res = requests.get(self.url, headers=headers)
        print "-" * 50
        print "GET ", "API: ", "download-file", res.status_code, self.url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50


class ErsModels:
    """
    get ers models list info or add/delete model,get or post
    """

    def __init__(self):
        self.url = device_url + "/models/ers"

    def get_ersModels(self):
        res = requests.get(self.url, headers=headers)
        print "-" * 50
        print "GET ", "API: ", "ers-models", res.status_code, self.url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50

    def post_ersModels(self):
        """upload ers model,add"""
        body = {
        "filename": "filename.zip"
            }
        res = requests.post(self.url, headers=headers, json=body)
        print "-" * 50
        print "POST ", "API: ", "ers-models", res.status_code, self.url
        print "[BODY] ", body
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50

    def delete_ersModels(self):
        """delete ers model"""
        body = {
            "modelID_list": []
        }
        res = requests.delete(self.url, headers=headers, json=body)
        print "-" * 50
        print "DELETE ", "API: ", "ers-models", res.status_code, self.url
        print "[BODY] ", body
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50

    def get_ersVersion(self):
        self.url = self.url + "/version"
        res = requests.get(self.url, headers=headers)
        print "-" * 50
        print "GET ", "API: ", "ers-models", res.status_code, self.url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50



class MrsTasks:
    """
    train specific mrs task,post
    """

    def __init__(self):
        self.url = device_url + "/tasks/mrs/{}".format(taskID)

    def post_mrs_tasks(self):
        body = {
            "chosenGroups": [],
            "action": 5
        }
        res = requests.post(self.url, headers=headers, json=body)
        print "-" * 50
        print "POST ", "API: ", "mrs-tasks", res.status_code, self.url
        print "[BODY] ", body
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50


class TaskStatus:
    """
    get mrs tasks list info,get
    """

    def __init__(self):
        self.url = device_url + "/tasks/mrs"

    def get_taskStatus(self):
        res = requests.get(self.url, headers=headers)
        print "-" * 50
        print "GET ", "API: ", "tasks-status", res.status_code, self.url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50


class EasAnomaly:
    """
    get eas anomaly info,all or specific anomalyID info,get
    """

    def get_easAnomaly(self, anomalyID=None):
        url = device_url + "/anomalies"
        print "-" * 50
        if not anomalyID:
            res = requests.get(url, headers=headers)
            print "GET ", "API: ", "eas-anomaly", res.status_code, url
        else:
            res = requests.get(url + "/" + anomalyID, headers=headers)
            print "GET ", "API: ", "eas-anomaly", res.status_code, url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50


class EasParameters:
    """
    get eas params setup info or setup params,get or post
    """

    def __init__(self):
        self.url = device_url + "/eas/parameters"

    def get_easParameters(self):
        res = requests.get(self.url, headers=headers)
        print "-" * 50
        print "GET ", "API: ", "eas-parameters", res.status_code, self.url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "-" * 50

    def post_easParameters(self, paramID=None):
        body = {
        "parameters": {
            "4cc167d1-183d-19e1-eb25-ec655080fb23_ca6481f4-1996-4400-8a83-8856772a504c": {
                "name": {
                    "en": "WHITE_LIST",
                    "zh": "WHITE_LIST"
                },
                "values": ["172.22.118.1", "1.1.1.1"],
                "key": "WHITE_LIST",
                "type": "user-set",
                "inputType": 1,
                "description": {
                    "en": "Define remote service applications. You can add multiple applications, use a comma to separate multiple items.",
                    "zh": "对于需要对外提供服务的设备可设置白名单过滤for email spam"
                }
            }
                }
            }
        if not paramID:
            pass


class DataInfo:
    """
    get eas_threats info,get
    """

    def get_easThreats(self):
        pass


class XrsScores:
    """
    get models's scores, default get all types of models's scores,get
    """

    def get_scores(self):
        pass

    def get_arsScore(self):
        pass

    def get_ersScore(self):
        pass

    def get_mrsScore(self):
        pass

    def get_risklevel(self):
        pass

    def get_weights(self):
        pass


class XrsForensics:
    """
    get forensics,post ars|ers|eas
    """

    def post_ars(self):
        pass

    def post_ers(self):
        pass

    def post_ers_model(self):
        pass

    def post_eas_threat(self):
        pass

    def post_eas_anomaly(self):
        pass


class EasReport:
    """
    anomaly actions report,post
    """

    def post_eas(self):
        pass

    def post_eas_anomalyID(self):
        pass


class AnomaliesSummary:
    """"
    anomaly actions report,post
    """

    def post_anomalies(self):
        pass

    def post_anomalyID(self):
        pass

if __name__ == '__main__':
    pass



