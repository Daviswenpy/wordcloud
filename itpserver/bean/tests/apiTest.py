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
os.environ.setdefault("DJANGO_SETTINGS_MODULE","bean.settings")
django.setup()
from itm.removed import json_loads_byteified
from case_api import *

clientIP = "192.168.255.140"
username = "itm-admin"
deviceID_test = "test-deviceID"
deviceID_BJ = "4cc167d1-183d-19e1-eb25-ec655080fb23"
deviceID_CD = "66a84d56-c747-998a-709e-b2b159a4cd86"
deviceID_BJ1 = "6a6887d4-b195-7ceb-f1d3-4d66eaf164a9"
filename = "test-filname"
sessionID = None
modelID = ""
anomalyID = ""
taskID = ""
base_url = "http://127.0.0.1:8000/ITMCP/v1/"
session_url = base_url + "sessions"
device_url = base_url + "devices/" + deviceID_BJ1


def print_info(type, verbose, res, url, body):
    print "+" + "-" * 100 + "+"
    print "%s " % type, "API: ", "%s" % verbose, res.status_code, url
    if type == "POST":
        print "[BODY] ", body
    print "[DATA] ", res.content
    data = json_loads_byteified(res.content)
    if data["status"] == 0:
        print True
    else:
        print False
    print "+" + "-" * 100 + "+"

class CheckIn:
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
        print "+" + "-"*100 + "+"
        print "POST ", "API: ", "check-in", res.status_code, url
        print "[BODY] ", body
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "+" + "-"*100 + "+"
        return data["sessionID"]


class LoginOut:
    """
    keepalive or log-out,get or delete
    """

    def __init__(self,sessionID):
        self.url = session_url + "/" + sessionID

    def keppalive(self,headers):
        res = requests.get(self.url, headers=headers)
        print_info("GET", "login-out", res, self.url, body=None)

    def login_out(self,headers):
        res = requests.delete(self.url, headers=self.headers)
        print_info("DELETE", "login-out", res, self.url, body=None)

class Register:
    """
    add/delete device,post or delete
    """

    def __init__(self):
        self.url = device_url

    def post_register(self, headers):
        body = {
        "deviceID": deviceID_test,
        "deviceName": "test-ucss",
        "logSources": []
            }
        res = requests.post(self.url, headers=headers, json=body)
        print_info("POST", "register", res, self.url, body)

    def delete_register(self, headers):
        res = requests.delete(self.url, headers=headers)
        print_info("DELETE", "register", res, self.url)


class ItmConfigs:
    """
    mainly setup field:interval,xrs-chosenGroup,blacklist with different types,post
    """

    def __init__(self):
        self.url = device_url + "/configurations/itmConfigs"

    def post_itmConfigs(self, headers):
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
        print_info("POST", "itm-configs", res, self.url, body)


class ConfXrs:
    """
    enable/disable ers/mrs models,get or post
    """

    def __init__(self):
        self.url = device_url + "/configurations/itmConfigs/"

    def post_confErs(self, headers):
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
        print_info("POST", "conf-xrs", res, self.url, body)

    def post_confMrs(self, headers):
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
        print_info("POST", "conf-xrs", res, self.url, body)

    def post_confArs(self, headers):
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
        print_info("POST", "conf-xrs", res, self.url, body)

    def post_blacklist(self, headers):
        pass

    def get_blacklist(self, headers):
        """return blacklist info"""
        # e.g. ars/blacklists
        self.url = self.url + "ars/blacklists"
        res = requests.get(self.url, headers=headers)
        print_info("GET", "conf-xrs", res, self.url, body=None)

    def get_version(self, headers):
        self.url = self.url + "versions"
        res = requests.get(self.url, headers=headers)
        print_info("GET", "conf-xrs", res, self.url, body=None)


class Configurations:
    """
    get models config info,get
    """

    def get_configurations(self, headers):
        url = device_url + "/configurations"
        res = requests.get(url, headers=headers)
        print_info("GET", "configurations", res, self.url, body=None)


class UploadFile:
    """
    upload tar file,source from some ip which excludes UCSS,post
    """

    def __init__(self):
        self.url = base_url + "upload/files/"

    def post_file(self, headers):
        body = {
            "filename": filename
        }
        res = requests.post(self.url, headers=headers, json=body)
        print_info("POST", "upload-file", res, self.url, body)


class DownloadFile:
    """
    download file
    """

    def __init__(self):
        self.url = base_url + "download/files/"

    def get_file(self, headers):
        res = requests.get(self.url, headers=headers)
        print_info("GET", "download-file", res, self.url, body=None)


class ErsModels:
    """
    get ers models list info or add/delete model,get or post
    """

    def __init__(self):
        self.url = device_url + "/models/ers"

    def get_ersModels(self, headers):
        res = requests.get(self.url, headers=headers)
        print_info("GET", "ers-models", res, self.url)

    def post_ersModels(self, headers):
        """upload ers model,add"""
        body = {
        "filename": "filename.zip"
            }
        res = requests.post(self.url, headers=headers, json=body)
        print_info("POST", "ers-models", res, self.url, body)

    def delete_ersModels(self, headers):
        """delete ers model"""
        body = {
            "modelID_list": []
        }
        res = requests.delete(self.url, headers=headers, json=body)
        print_info("DELETE", "ers-models", res, self.url, body)

    def get_ersVersion(self, headers):
        self.url = self.url + "/version"
        res = requests.get(self.url, headers=headers)
        print_info("GET", "ers-models", res, self.url)


class MrsTasks:
    """
    train specific mrs task,post
    """

    def __init__(self):
        self.url = device_url + "/tasks/mrs/{}".format(taskID)

    def post_mrs_tasks(self, headers):
        body = {
            "chosenGroups": [],
            "action": 5
        }
        res = requests.post(self.url, headers=headers, json=body)
        print_info("POST", "mrs-tasks", res, self.url, body)


class TaskStatus:
    """
    get mrs tasks list info,get
    """

    def __init__(self):
        self.url = device_url + "/tasks/mrs"

    def get_taskStatus(self, headers):
        res = requests.get(self.url, headers=headers)
        print_info("GET", "tassks-status", res, self.url)


class EasAnomaly:
    """
    get eas anomaly info,all or specific anomalyID info,get
    """

    def get_easAnomaly(self, headers, anomalyID=None):
        url = device_url + "/anomalies"
        print "+" + "-"*100 + "+"
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
        print "+" + "-"*100 + "+"


class EasParameters:
    """
    get eas params setup info or setup params,get or post
    """

    def __init__(self):
        self.url = device_url + "/eas/parameters"

    def get_easParameters(self, headers,paramID=None):
        print "+" + "-" * 100 + "+"
        if not paramID:
            res = requests.get(self.url, headers=headers)
            print "GET ", "API: ", "eas-parameters", res.status_code, self.url
        else:
            self.url = self.url + '/' + paramID
            res = requests.get(self.url, headers=headers)
            print "GET ", "API: ", "eas-parameters", res.status_code, self.url
        print "[DATA] ", res.content
        data = json_loads_byteified(res.content)
        if data["status"] == 0:
            print True
        else:
            print False
        print "+" + "-"*100 + "+"

    def post_easParameters(self, headers, paramID=None):
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
                    "zh": "对于需要对外提供服务的设备可设置白名单过滤"
                }
            }
                }
            }
        res = requests.post(self.url, headers=headers, json=body)
        print_info("POST", "anomaliesSummary", res, self.url, body)
        if not paramID:
            pass


class DataInfo:
    """
    get eas_threats info,get
    """
    def __init__(self):
        self.url = device_url + "/data/info"

    def get_easThreats(self, headers):
        res = requests.get(self.url, headers=headers)
        print_info("GET", "data-info", res, self.url, body=None)



class XrsScores:
    """
    get models's scores, default get all types of models's scores,get
    """
    def __init__(self):
        self.url = device_url + "/scores"

    def get_scores(self, headers,xrs=None):
        if not xrs:
            pass
        elif xrs == "ars":
            self.url = self.url + "/arsScores"
        elif xrs == "ers":
            self.url = self.url + "/ersScores"
        elif xrs == "mrs":
            self.url = self.url + "/mrsScores"
        elif xrs == "riskLevel":
            self.url = self.url + "/riskLevel"
        elif xrs == "weights":
            self.url = self.url + "/weights"
        res = requests.get(self.url, headers=headers)
        print_info("GET", "xrs-scores", res, self.url, body=None)


class XrsForensics:
    """get forensics,post ars|ers|eas"""

    def __init__(self):
        self.url = device_url + "/forensics"

    def post_xrsForensics(self, headers, xrs=None, pk=None, ID=None):
        # body_ars = {"timestamp":1608220800,"user":"22e4b124-ebaa-d84e-b2b5-27b278196225","pageSize":20}
        # body_exs = {"timestamp":1608220800,"user":"skyguardmis.com\\yuhongyan","pageSize":1}
        body ={"timestamp":1608890400,"pageSize":1,"user":"skyguardmis.com\\qatest"}
        if xrs == "ars":
            self.url = self.url + "/ars"
            res = requests.post(self.url, headers=headers, json=body)
        elif xrs == "ers":
            if not pk: # /ers
                self.url = self.url + "/ers"
                res = requests.post(self.url, headers=headers, json=body)
            else: # ers/model/ID
                self.url = self.url + "/ers/model/" + ID
                res = requests.post(self.url, headers=headers, json=body)
        elif xrs == "eas":
            if pk == "threat":
                self.url = self.url + "/eas/threat/" + ID
                res = requests.post(self.url, headers=headers, json=body)
            else:
                self.url = self.url +  "/eas/anomaly/" + ID
                res = requests.post(self.url, headers=headers, json=body)
        print_info("POST", "xrs-forensics", res, self.url, body)


class EasReport:
    """anomaly actions report,post """

    def post_eas(self, headers, anomalyID=None):
        body = {"filter":[{"type":3,"value":["*"]}],"startTimestamp":1607702400,"endTimestamp":1608307200,"top":5}
        self.url = device_url + "/report/eas"
        if not anomalyID:
            res = requests.post(self.url, headers=headers, json=body)
        else:
            self.url = self.url + "/" + anomalyID
            res = requests.post(self.url, headers=headers, json=body)
        print_info("POST", "eas-report", res, self.url, body)


class AnomaliesSummary:
    """anomaly actions report,post"""

    def post_anomalies(self, headers):
        body = {"filter":[{"type":3,"value":["*"]}],"startTimestamp":1607702400,"endTimestamp":1608307200,"page":1,"pageSize":20}
        self.url = device_url + "/anomaliesSummary/eas"
        if not anomalyID:
            res = requests.post(self.url, headers=headers, json=body)
        else:
            self.url = self.url + "/" + anomalyID
            res = requests.post(self.url, headers=headers, json=body)
        print_info("POST", "anomaliesSummary", res, self.url, body)


class TestApi:
    """run api test"""

    def __init__(self):
        checkin = CheckIn()
        sessionID = checkin.post_checkin()
        self.headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ":" + sessionID)}

    def test_configs(self):
        register = Register()
        register.post_register(self.headers)

    def test_scores(self):
        scores = XrsScores()
        scores.get_scores(self.headers, "ers")

    def test_forensics(self):
        forensics = XrsForensics()
        # forensics.post_xrsForensics(self.headers,"eas", "anomaly", "02bd8546-5d95-59aa-9287-1eee1aaca6c3")
        forensics.post_xrsForensics(self.headers,"ers", "model", "1e2b5108-34df-45e2-9e48-3e1e516434c5")

    def test_report(self):
        eas_report = EasReport()
        eas_report.post_eas(self.headers)
        anomaliesSummary = AnomaliesSummary()
        anomaliesSummary.post_anomalies(self.headers)

    def run_else(self):
        pass



if __name__ == '__main__':
    print "-"*45 + "Testing now" + "-"*46
    test = TestApi()
    # test.test_configs()
    # test.test_scores()
    test.test_forensics()
    # test.test_report()


