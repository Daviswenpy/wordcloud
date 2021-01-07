# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-05-17 16:25:03
File Name: test_v1.py @v1.0
"""
# test funcs added by wendong with func-doc-descriptions, GET or POST
import requests
import base64
import datetime
import time
import hashlib
import json
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bean.settings")
django.setup()
# modified by wendong,the old's path was wrong
from itm.removed import json_loads_byteified

# clientIP = "172.22.118.99"
# modified by wendong
clientIP = "127.0.0.1"
username = "itm-admin"
deviceID = "test-deviceID"
deviceID_BJ = "4cc167d1-183d-19e1-eb25-ec655080fb23"
deviceID_CD = "66a84d56-c747-998a-709e-b2b159a4cd86"
deviceID_33 = "6a6887d4-b195-7ceb-f1d3-4d66eaf164a9"
# added by wendong
filename = "/home/ubuntu/workspace/skyguard/itpserver/bean/download/test_wen_20201203.zip"
# data source: ers_models
modelID = "b553c9f4-40b1-11e9-877e-701ce75b9b44"
# ers_interval_results说明, policyID is nodeID
nodeID = "fc89677c-68f5-4e5d-ae63-694dd9e40289"


'''
# def checkin(): 
# coded by lian
def _checkin():
    time_now = time.mktime(datetime.datetime.now().timetuple())
    username = passwd = "itm-admin"
    passwordHash = base64.b64encode(hashlib.sha256(username + str(int(time_now)) + hashlib.sha256(passwd).hexdigest()).hexdigest())[:12]
    data = {"username": username, "timestamp": int(time_now), "passwordHash": passwordHash}
    return json.dumps(data)
'''
'''
test: views001.py  
function: session management
include: checkin login_out
'''
def checkin():
    '''
    time_now = time.mktime(datetime.datetime.now().timetuple())
    # url = "http://172.22.118.99:8080/ITMCP/v1/sessions"
    # modified by wendong, change host
    url = "http://127.0.0.1:8000/ITMCP/v1/sessions"
    username = "itm-admin"
    password = hashlib.sha256("itm-admin").hexdigest()
    # hash_str = hashlib.sha256(username + str(int(time_now)) + password).hexdigest()
    hash_str = hashlib.sha256(username + str(int(time_now)-4000) + password).hexdigest()
    passwordHash = base64.b64encode(hash_str)[:12]
    data = {
        "username": username,
        "timestamp": int(time_now),
        # "timestamp": 1579417202,
        "passwordHash": passwordHash,
        # "passwordHash": "MjAyNzQ0Njxx",
        "deviceType": 1,
        "connectionType": 0
    }
    r = requests.post(url, json=data)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: password error"
    print "\t", "POST:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 1:
        print True
    else:
        print False
    print

    time_now = time.mktime(datetime.datetime.now().timetuple()) + 8000
    # url = "http://172.22.118.99:8080/ITMCP/v1/sessions"
    url = "http://127.0.0.1:8000/ITMCP/v1/sessions"
    username = "itm-admin"
    password = hashlib.sha256("itm-admin").hexdigest()
    # print password
    hash_str = hashlib.sha256(username + str(int(time_now)) + password).hexdigest()
    passwordHash = base64.b64encode(hash_str)[:12]
    data = {
        "username": username,
        "timestamp": int(time_now),
        "passwordHash": passwordHash,
        "deviceType": 1,
        "connectionType": 0
    }
    r = requests.post(url, json=data)
    print "case 2: timestamp error"
    print "\t", "POST:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 2:
        print True
    else:
        print False
    print
    '''
    time_now = time.mktime(datetime.datetime.now().timetuple())
    # url = "http://172.22.118.99:8080/ITMCP/v1/sessions"
    url = "http://127.0.0.1:8000/ITMCP/v1/sessions"
    # url = "https://172.30.3.57:9443/ITMCP/v1/sessions" # ucss itpserver ver 3.6,测试时，用日志参数-body测试特定机器
    username = "itm-admin"
    password = hashlib.sha256("itm-admin").hexdigest()
    hash_str = hashlib.sha256(username + str(int(time_now)) + password).hexdigest()
    passwordHash = base64.b64encode(hash_str)[:12]
    data = {
        "username": username,
        "timestamp": int(time_now),
        "passwordHash": passwordHash,
        "deviceType": 1,
        "connectionType": 0
    }
    # data = {"username": "itmadmin", "timestamp": 1608086100, "passwordHash": "ZmEwMDdhZDRm", "deviceType": 1, "connectType": 0}
    r = requests.post(url, json=data, verify=False)
    print "case 1: normal"
    print "\t", "POST:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0 and dat["sessionTimeout"] == 3600 and dat["clientIP"] == clientIP and dat.has_key("sessionID"):
        print True
    else:
        print False
    print "checkin done!"

    return dat["sessionID"]

sessionID = checkin()
headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}


def login_out(sessionID):
    # url = "http://172.22.118.99:8080/ITMCP/v1/sessions/" + sessionID
    url = "http://127.0.0.1:8000/ITMCP/v1/sessions/" + sessionID
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ":" + sessionID)}
    r = requests.get(url, headers=headers)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: keeplive-normal"
    print "\t", "GET:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0 and dat["sessionTimeout"] == 3600:
        print True
    else:
        print False
    print

    # url = "http://172.22.118.99:8080/ITMCP/v1/sessions/" + sessionID
    url = "http://127.0.0.1:8000/ITMCP/v1/sessions/" + sessionID
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ":" + sessionID)}
    r = requests.delete(url, headers=headers)
    print "case 2: checkout"
    print "\t", "DELETE:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0 and dat["username"] == username and dat["sessionID"] == sessionID:
        print True
    else:
        print False

    print "keeplive done!"

# login_out(sessionID)

'''
test: views002.py  
function: devices management
include: register itm_configs configuration conf_xrs
'''
def register(sessionID):
    # url = "http://172.22.118.99:8080/ITMCP/v1/devices/" + deviceID + "-v2"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ":" + sessionID)}
    print "case 1: register for test"
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_BJ
    data = {
        "deviceID": deviceID_BJ,
        "deviceName": "ucss",
        "logSources": [],
        # "itmConfigs": {"nothing": 0} # required=False
    }
    r = requests.post(url, headers=headers, json=data)
    print "\t", "POST:"
    print "\t", r.status_code, r.content

    '''
    print "case 2: disregister"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_CD
    r = requests.delete(url, headers=headers)
    print "\t", "DELETE:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print
    '''

    print "register done!"

# register(sessionID)


def configurations(sessionID):
    # url = "http://172.22.118.99:8080/ITMCP/v1/devices/" + deviceID + "/configurations"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_CD + "/configurations"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    r = requests.get(url, headers=headers)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: normal"
    print "\t", "GET:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print "configurations done!"

# configurations(sessionID)

def itmconfigs(sessionID):
    # url = "http://172.22.118.99:8080/ITMCP/v1/devices/" + deviceID + "/configurations/itmConfigs"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_CD + "/configurations/itmConfigs"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    # data = {
    #     "ars": {
    #         "version": 1,
    #         "blacklist": ["192.168.1.1", "192.168.2.1-192.168.2.32", "name123"],
    #         "interval": 3600,
    #         "subsystems": [1, 2, 3],
    #         "topN": 0
    #     },
    #     "mrs": {
    #         "version": 1,
    #         "blacklist": ["192.168.1.1", "192.168.2.1-192.168.2.32", "name123"],
    #         "interval": 3600,
    #         "uploadToLab": True,
    #         "chosenDLPPolicies": ["daba56c8-73ec-11df-a475-002264764cea1"],
    #         "retrospectiveDays": 7,
    #         "topN": 0
    #     },
    #     "ers": {
    #         "version": 1,
    #         "blacklist": ["192.168.1.1", "192.168.2.1-192.168.2.32", "name123"],
    #         "interval": 3600,
    #         "ChosenModels": ["daba56c8-73ec-11df-a475-002264764cab", "daba56c8-73ec-11df-a475-002264764cac"],
    #         "modelParameterMap": [{
    #             "modelID": "aba56c8-73ec-11df-a475-002264764cab",
    #             "parameterMap": [
    #                 {
    #                     "parameterID": "daba56c8-73ec-11df-a475-002264764cea",
    #                     "policyID": "caba51c8-22ec-11ae-a475-002264764537"
    #                 },
    #                 {
    #                     "parameterID": "d244ad76-65ac-11df-a475-0022647643de",
    #                     "policyIDs": ["daba56c8-1234-11df-1234-00226476459a", "daba56c8-1234-11df-1234-00226476450e"]
    #                 }
    #             ]
    #         }],
    #         "topN": 0
    #     }
    # }
    # r = requests.post(url, headers=headers, json=data)
    # print "------------------------------------------------------"
    # print "api:", url
    # print
    # print "case 1: normal"
    # print "\t", "POST:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print

    # no specified data test
    # data = {
    #     "ars": {
    #         "version": 0,
    #         "blacklist": [],
    #         "interval": 3600,
    #         "subsystems": [],
    #         "topN": 0
    #     },
    #     "mrs": {
    #         "version": 0,
    #         "blacklist": [],
    #         "interval": 3600,
    #         "uploadToLab": True,
    #         "chosenDLPPolicies": [],
    #         "retrospectiveDays": 7,
    #         "topN": 0
    #     },
    #     "ers": {
    #         "version": 0,
    #         "topN": 0,
    #         "blacklist": [],
    #         "interval": 3600,
    #         "ChosenModels": [],
    #         "modelParameterMap": []
    #     }
    # }
    data = {
        "ars": {
            "subsystems": [1,1,1],
            "interval": 7200,
            "chosenGroups": [],
            "blacklist": [
                {
                    "type": 1,
                    "value": ["1.1.1.1"]
                },
                {
                    "type": 2,
                    "value": []
                },
                {
                    "type": 3,
                    "value": ["QiaoJioLiuROu","QingSunTiao","MaoDu"]
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
    r = requests.post(url, headers=headers, json=data)
    print "case 1: normal"
    print "\t", "POST:"
    print "\t", r.status_code, r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print
    print "itmconfigs done!"

# itmconfigs(sessionID)

def conf_xrs(sessionID):
    # GET/POST ars|ers|mrs/blacklists
    # url = "http://172.22.118.99:8080/ITMCP/v1/devices/" + deviceID + "/configurations/itmConfigs/ars/blacklists"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_CD + "/configurations/itmConfigs/ars/blacklists"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    data = {
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
                "value": ["ARS","menu today","WanZaMian","DanDan noodles","odd taste noodles"]
            },
            {
                "type": 4,
                "value": []
            },
            {
                "type": 5,
                "value": []
            }
        ]
    }
    r1 = requests.post(url, headers=headers, json=data)
    r2 = requests.get(url, headers=headers)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: blacklist"
    print "\t", "POST:", r1.status_code
    print "\t", r1.content
    dat = json_loads_byteified(r1.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print
    print "\t", "GET:", r2.status_code
    print "\t", r2.content
    dat = json_loads_byteified(r2.content)
    if dat["status"] == 0 and dat["blacklist"] == data["blacklist"]:
        print True
    else:
        print False
    print

    # GET/POST  ars|ers|mrs
    # GET version
    # url = "http://172.22.118.99:8080/ITMCP/v1/devices/" + deviceID + "/configurations/itmConfigs/ars"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID + "/configurations/itmConfigs/ars"
    # headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    # data = {
    #     "subsystems": [],
    #     "interval": 7200,
    #     "chosenGroups": [],
    #     "blacklist": [
    #         {
    #             "type": 1,
    #             "value": []
    #         },
    #         {
    #             "type": 2,
    #             "value": []
    #         },
    #         {
    #             "type": 3,
    #             "value": []
    #         },
    #         {
    #             "type": 4,
    #             "value": []
    #         },
    #         {
    #             "type": 5,
    #             "value": []
    #         }
    #     ],
    #     "topN": 0,
    #     "version": 1
    # }
    # r1 = requests.post(url, headers=headers, json=data)
    # r2 = requests.get(url, headers=headers)
    # print "case 2: xrs"
    # print "\t", "POST:", r1.status_code
    # print "\t", r1.content
    # dat = json_loads_byteified(r1.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print
    # print "\t", "GET:", r2.status_code
    # print "\t", r2.content
    # dat = json_loads_byteified(r2.content)
    # if dat == {"status": 0, "ars": data}:
    #     print True
    # else:
    #     print False
    # print "case 3: versions"
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID + "/configurations/itmConfigs/versions"
    # r = requests.get(url, headers=headers)
    # print "\t", "GET:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    print "conf_xrs done!"

# conf_xrs(sessionID)

'''
test: views003.py  
function: files transform
include: upload_file download_file
'''
def upload_file(sessionID):
    '''POST'''
    # url = "http://127.0.0.1:8000/ITMCP/v1/upload/files/(?P<filename>([^/]+))"
    url = "http://127.0.0.1:8000/ITMCP/v1/upload/files/"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID),'content-type': 'application/json'}
    data = {
        "filename": filename
    }
    r = requests.post(url, headers=headers, json=data)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: upload"
    print "\t", "POST:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print "upload_file done!"

# upload_file(sessionID)

def download_file(sessionID):
    '''GET'''
    # url = "http://127.0.0.1:8000/ITMCP/v1/download/files/(?P<filename>([^/]+))"
    url = "http://127.0.0.1:8000/ITMCP/v1/download/files/"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    r = requests.get(url, headers=headers)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: download/files/"
    print "\t", "GET:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print
    r = requests.get(url+filename, headers=headers)
    print "api:", url
    print
    print "case 2: download/files/filaname"
    print "\t", "GET:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print "download_file done!"

# download_file(sessionID)

'''
test: views004.py  
function: models management
include: mrs_tasks tasks_status ers_models eas_anomaly
'''
def mrs_tasks(sessionID):
    # url = "http://172.22.118.99:8080/ITMCP/v1/devices/" + deviceID + "/tasks/mrs/mrs-task-id"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_CD + "/tasks/mrs/04a38d73-d3eb-4e39-9278-284ab8e700c3"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    data = {
        "chosenGroups": ["all"],
        "action": 5
    }
    r = requests.post(url, headers=headers, json=data)
    print "api:", url
    print
    print "case 1: mrs_tasks"
    print "\t", "POST:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    # if dat["status"] == 0 and dat["sessionTimeout"] == 3600:
    if dat["status"] == 0:
        print True
    else:
        print False
    print "mrs_tasks done!"

# mrs_tasks(sessionID)


def tasks_status(sessionID):
    '''GET'''
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID + "/tasks/mrs"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_BJ + "/tasks/mrs"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    r = requests.get(url, headers=headers)
    print "-"*50
    print "api:", url
    print
    print "case 1: tasks_status"
    print "\t", "GET:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    # if dat["status"] == 0 and dat["sessionTimeout"] == 3600:
    if dat["status"] == 0:
        print True
    else:
        print False
    print "task_status done!"

# tasks_status(sessionID)

def ers_models(sessionID):
    # url = "http://172.22.118.99:8080/ITMCP/v1/devices/(?P<deviceID>([^/]+))/models/ers"
    # url = "http://172.22.118.99:8080/ITMCP/v1/devices/deviceID/models/ers/version"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_BJ + "/models/ers"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}

    r = requests.get(url, headers=headers)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: ers"
    print "\t", "GET:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    '''
    data = {
        "filename": filename
    }
    files = {
        "filename": (filename, "application/x-zip-compressed")
        # 'img':(('demo',open('D:/demo.jpg')),'image/jpeg')
    }

    r = requests.post(url, headers=headers, files=files)
    print "case 2: ers"
    print "\t", "POST:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    '''
    data = {
        "modelID_list": [
            "a0501bc1-1d0e-31aa-892e-2f2ed1cbbc1f"
            # custom model
        ]
    }
    r = requests.delete(url, headers=headers, json=data)
    print "case 3: ers"
    print "\t", "DELETE:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    
    
    # r = requests.get(url + "/version", headers=headers)
    # print "case 4: ers/version"
    # print "\t", "GET:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False

    print "ers_models done!"

# ers_models(sessionID)

def eas_anomaly(sessionID):
    '''GET'''
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID + "/anomalies/(?P<anomalyID>([^/]+))"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_BJ + "/anomalies"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    r = requests.get(url, headers=headers)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: anomalies"
    print "\t", "GET:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print
    anomalyID = "a1075029-e5b9-4e9c-a009-1381b70f1637"
    r = requests.get(url + "/" + anomalyID, headers=headers)
    print "api:", url
    print
    print "case 2: anomalies/anomalyID"
    print "\t", "GET:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print "eas_anomaly done!"

# eas_anomaly(sessionID)

def eas_parameters(sessionID):
    '''GET/POST'''
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID + "/eas/parameters/(?P<paramID>([^/]+))"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_CD + "/eas/parameters"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    data = {
        "parameters": {
            "66a84d56-c747-998a-709e-b2b159a4cd86_86eb7d08-3cf5-4455-9f05-12fed955e142": {
                "name": {
                    "en": "TEST-PARAMETER",
                    "zh": "测试"
                },
                "values": ["172.22.118.1", "1.1.1.1"],
                "key": "TEST",
                "type": "user-set",
                "inputType": 1,
                "description": {
                    "en": "Define remote service applications. You can add multiple applications, use a comma to separate multiple items.",
                    "zh": "测试"
                }
            }
        }
    }
    # r1 = requests.get(url, headers=headers)
    r2 = requests.post(url, headers=headers,json=data)
    # print "------------------------------------------------------"
    # print "api:", url
    # print
    # print "case 1: eas/parameters"
    # print "\t", "GET:", r1.status_code
    # print "\t", r1.content
    # dat = json_loads_byteified(r1.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False

    print "api:", url
    print "case 2: eas/parameters"
    print "\t", "POST:", r2.status_code
    print "\t", r2.content
    dat = json_loads_byteified(r2.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print

    # paramID = "66a84d56-c747-998a-709e-b2b159a4cd86_0789df06-3aad-4bd3-9c6e-6c9086d025dd"
    # r = requests.post(url + "/" + paramID, headers=headers)
    # print "api:", url
    # print
    # print "case 3: eas/paramID"
    # print "\t", "GET:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print "eas_parameters done!"

# eas_parameters(sessionID)

'''
test: views005.py  
function: scores 
include: x_scores data_info 
'''
def x_scores(sessionID):
    '''
    GET
    default: all scores, 1
    specify pk, return the corresponding pk-score, 5
    '''
    # no specific
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID + "/scores/(?P<pk>(arsScores)|(mrsScores)|(ersScores)|(weights)|(riskLevel))"
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID + "/scores"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_BJ + "/scores"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}

    r = requests.get(url, headers=headers)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: x_scores"
    print "\t", "GET:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    # if dat["status"] == 0 and dat["sessionTimeout"] == 3600:
    if dat["status"] == 0:
        print True
    else:
        print False
    print

    # specific pk
    # r = requests.get(url+"/arsScores", headers=headers)
    # print "api:", url
    # print
    # print "case 2: arsScores"
    # print "\t", "GET:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # # if dat["status"] == 0 and dat["sessionTimeout"] == 3600:
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print
    # r = requests.get(url+"/mrsScores", headers=headers)
    # print "api:", url
    # print
    # print "case 3: mrsScores"
    # print "\t", "GET:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # # if dat["status"] == 0 and dat["sessionTimeout"] == 3600:
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print
    # r = requests.get(url+"/ersScores", headers=headers)
    # print "api:", url
    # print
    # print "case 4: ersScores"
    # print "\t", "GET:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # # if dat["status"] == 0 and dat["sessionTimeout"] == 3600:
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print
    # # r = requests.get(url+"/riskLevel", headers=headers)
    # # print "api:", url
    # # print
    # # print "case 5: riskLevel"
    # # print "\t", "GET:", r.status_code
    # # print "\t", r.content
    # # dat = json_loads_byteified(r.content)
    # # # if dat["status"] == 0 and dat["sessionTimeout"] == 3600:
    # # if dat["status"] == 0:
    # #     print True
    # # else:
    # #     print False
    # # print
    # # r = requests.get(url+"/weights", headers=headers)
    # # print "api:", url
    # # print
    # # print "case 6: weights"
    # # print "\t", "GET:", r.status_code
    # # print "\t", r.content
    # # dat = json_loads_byteified(r.content)
    # # # if dat["status"] == 0 and dat["sessionTimeout"] == 3600:
    # # if dat["status"] == 0:
    # #     print True
    # # else:
    # #     print False
    # print "x_scores done!"

# x_scores(sessionID)

def data_info(sessionID):
    '''GET'''
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID + "/data/info"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_BJ + "/data/info"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    r = requests.get(url, headers=headers)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: data_info"
    print "\t", "GET:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print "data_info done!"

# data_info(sessionID)

'''
test: views006.py  
function: forensics 
include: xrs_forensics eas_report anomaliesSummary
'''
def xrs_forensics(sessionID):
    '''POST'''
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/(?P<deviceID>([^/]+))/forensics/(?P<xrs>(ers|ars))"
                                                                                    # (?P<xrs>(ers))/(?P<pk>(model|param))/(?P<ID>([^/]+))
                                                                                    # (?P<xrs>(eas))/(?P<pk>(threat|anomalyGroup|anomaly))/(?P<ID>([^/]+))
                                                                                    # (?P<xrs>(ars))/(?P<pk>(protocols|network))
    # time_now = time.mktime(datetime.datetime.now().timetuple())
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_BJ + "/forensics/ers"
    # headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    # data = {"timestamp":1607423400,"pageSize":1,"user":"172.22.73.210"}
    # r = requests.post(url, headers=headers, json=data)
    # print "------------------------------------------------------"
    # print "api:", url
    # print
    # print "case 1: xrs_forensics/ers"
    # print "\t", "POST:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    #
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print
    # anomalyID in modelParameters(type list)
    #
    # data = {"timestamp":1607659200,"user":"172.30.4.50","pageSize":20}
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_CD + "/forensics/ars"
    # r = requests.post(url, headers=headers, json=data)
    # print "api:", url
    # print
    # print "case 2: xrs_forensics/ars"
    # print "\t", "POST:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print
    #
    # # data = {timestamp: 1607061600, pageSize: 1, user: "skyguardmis.com\liuqi"}
    data = {"timestamp": 1608616800, "user": "eptest111111\\itptest1", "pageSize": 1}
    # data = {"timestamp":1607493600,"pageSize":1,"user":"skyguardmis.com\\hulizhong"}
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_BJ + "/forensics/ers/model/" + "a2994f5e-a3a6-4e58-935e-8c93525ec512"
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_33 + "/forensics/ers/model/" + "85c01018-d507-4e57-958e-6426aac08d8c"
    r = requests.post(url, headers=headers, json=data)
    print "api:", url
    print
    print "case 3: xrs_forensics/ers/model/modelID"
    print "\t", "POST:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print
    '''
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_1 + "/forensics/ers/param/" + nodeID
    r = requests.post(url, headers=headers, json=data)
    print "api:", url
    print

    print "case 4: xrs_forensics/ers/param/nodeID" #
    print "\t", "POST:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print
    '''

    # data = {"timestamp": 1607061600, "user": "skyguardmis.com\duanhui", "pageSize": 1}
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_CD + "/forensics/eas/threat/" + "0ca37e75-246a-4beb-8e26-af6ad0c2604a"
    # r = requests.post(url, headers=headers, json=data)
    # print "api:", url
    # print
    # print "case 5: xrs_forensics/eas/threat/ID"
    # print "\t", "POST:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print

    #
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_1 + "/forensics/eas/anomalyGroup/" + "6830b50e-6cd6-48b6-ba25-f6d4105fccd0"
    # r = requests.post(url, headers=headers, json=data)
    # print "api:", url
    # print
    # print "case 6: xrs_forensics/eas/anomalyGroup/ID"
    # print "\t", "POST:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print

    # data_liuqieas = {
    #     "timestamp": 1605801600,
    #     "user": "skyguardmis.com\leihuaijin",
    #     "pageSize": 1
    # }
    # data = {"timestamp":1608192000,"user":"skyguardmis.com\\hulizhong","pageSize":1} # fix bug,1209
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_33 + "/forensics/eas/anomaly/" + "8978dd19-b948-4fb4-a771-f2f80e827402"
    # r = requests.post(url, headers=headers, json=data)
    # print "api:", url
    # print
    # print "case 7: xrs_forensics/eas/anomaly/ID"
    # print "\t", "POST:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print


    
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_1 + "/forensics/ars/protocols"
    # data = {
    #     "timestamp": int(time_now),
    #     "user": "d2ba046c-67c6-467c-b7ce-15015e6f0436",
    #     "pageSize": 1
    # }
    # r = requests.post(url, headers=headers, json=data)
    # print "api:", url
    # print
    # print "case 8: xrs_forensics/ars/protocols"
    # print "\t", "POST:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print
    #
    # url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_1 + "/forensics/ars/network"
    # r = requests.post(url, headers=headers, json=data)
    # print "api:", url
    # print
    # print "case 9: xrs_forensics/ars/network"
    # print "\t", "POST:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    #
    print "xrs_forensics done!"

xrs_forensics(sessionID)

def eas_report(sessionID):
    '''POST'''
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_BJ + "/report/eas"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    data = {"filter":[{"type":3,"value":["*"]}],"startTimestamp":1607616000,"endTimestamp":1608220800,"top":5}
    r = requests.post(url, headers=headers, json=data)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: report/eas"
    print "\t", "POST:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print

    ID = "cc9e52e6-39b4-4b03-819b-0dcbeac5c5af"
    r = requests.post(url+"/"+ID, headers=headers, json=data)
    print "api:", url
    print
    print "case 2: report/eas/ID"
    print "\t", "POST:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print "eas_report done!"

# eas_report(sessionID)

def anomaliesSummary(sessionID):
    '''POST'''
    time_now = time.mktime(datetime.datetime.now().timetuple())
    url = "http://127.0.0.1:8000/ITMCP/v1/devices/" + deviceID_BJ + "/anomaliesSummary/eas"
    headers = {'Authorization': 'basic ' + base64.b64encode(clientIP + ':' + sessionID)}
    data = {"filter":[{"type":3,"value":["*"]}],"startTimestamp":1607097600,"endTimestamp":1607702400,"page":1,"pageSize":20}
    r = requests.post(url, headers=headers, json=data)
    print "------------------------------------------------------"
    print "api:", url
    print
    print "case 1: anomaliesSummary/eas"
    print "\t", "POST:", r.status_code
    print "\t", r.content
    dat = json_loads_byteified(r.content)
    if dat["status"] == 0:
        print True
    else:
        print False
    print
    # ID = "fc1e5c7c-612a-45fb-8f46-b276e7fe95f5"
    # ID = "a7cd4cda-af84-11e9-ac89-144f8a006a90"
    # r = requests.post(url+"/"+ID, headers=headers, json=data)
    # print "api:", url
    # print
    # print "case 2: anomaliesSummary/eas/ID"
    # print "\t", "POST:", r.status_code
    # print "\t", r.content
    # dat = json_loads_byteified(r.content)
    # if dat["status"] == 0:
    #     print True
    # else:
    #     print False
    # print "anomaliesSummary done"

# anomaliesSummary(sessionID)



