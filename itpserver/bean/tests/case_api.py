# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-06-14 13:35:14
File Name: case_api.py @v1.0
"""
import os
import json
import time
import base64
import hashlib
import unittest
import datetime
import requests as req


username = 'itm-admin'
password = 'itm-admin'
# deviceID = "deviceID-lian"
deviceID = "deviceID-wen"
deviceID_1 = "4cc167d1-183d-19e1-eb25-ec655080fb23" # added by wendong, GET
filename = 'json_error.zip' # added by wendong
anomalyID = "a1075029-e5b9-4e9c-a009-1381b70f1637" # added by wendong
paramID = "6a6887d4-b195-7ceb-f1d3-4d66eaf164a9_91840212-f491-11e9-a861-9a17b6b6610c" # added by wendong
anomaliesSummaryID = "a7cd4cda-af84-11e9-ac89-144f8a006a90"
eas_reportID = "a7cd4cda-af84-11e9-ac89-144f8a006a90"
# data source: ers_models
modelID = "b553c9f4-40b1-11e9-877e-701ce75b9b44"
# ers_interval_results说明, policyID is nodeID
nodeID = "fc89677c-68f5-4e5d-ae63-694dd9e40289"
threatID = "0ca37e75-246a-4beb-8e26-af6ad0c2604a"
anomalyGroupID = "6830b50e-6cd6-48b6-ba25-f6d4105fccd0"


# uri = "http://0.0.0.0:8080"
uri = "http://0.0.0.0:8080" # added by wendong
# test_URL = "http://172.22.118.1:9200/"
test_URL = 'http://172.22.149.230:9200/'
# broker_url_deve = "redis://172.238.238.238:6379/0"
broker_url_deve = "redis://127.0.0.1:6379/0"
broker_url_test = "redis://0.0.0.0:6379/0"

time_now = time.mktime(datetime.datetime.now().timetuple())
_passwordHash = base64.b64encode(hashlib.sha256(username + str(int(time_now)) + hashlib.sha256(password).hexdigest()).hexdigest())[:12]
login_data = {"username": username, "timestamp": int(time_now), "passwordHash": _passwordHash}

# device_data = {"deviceID": deviceID, "deviceName": "lian-test-ucss", "logSources": ["1.1.1.1", "2.2.2.2", "3.3.3.3"]}
device_data = {"deviceID": deviceID, "deviceName": "wen-test-ucss", "logSources": []}

# device_configuration = {
#     # u'status': 0, u'deviceName': u'lian-test-ucss', u'is_active': True, u'deviceID': u'deviceID-lian',
#     # u'logSources': [u'1.1.1.1', u'2.2.2.2', u'3.3.3.3'],
#     u'logSources': [],
#     u'itmConfigs': {
#         u'ers': {u'interval': 7200, u'ChosenModels': [], u'modelParameterMap': [], u'blacklist': [], u'topN': 0, u'version': 0},
#         u'ars': {u'subsystems': [], u'interval': 7200, u'chosenGroups': [], u'blacklist': [], u'topN': 0, u'version': 0},
#         u'mrs': {u'chosenDLPPolicies': [], u'interval': 7200, u'blacklist': [], u'topN': 0, u'version': 0, u'uploadToLab': True, u'retrospectiveDays': 7}
#     }
# }
# added by wendong
device_configuration = {
	"status": 0,
	"deviceName": "wen-test-ucss",
	"is_active": True,
	"deviceID": "deviceID-wen",
	"logSources": [],
	"itmConfigs": {
		"ers": {
			"interval": 7200,
			"ChosenModels": [],
			"modelParameterMap": [],
			"blacklist": [{
				"type": 1,
				"value": []
			}, {
				"type": 2,
				"value": []
			}, {
				"type": 3,
				"value": []
			}, {
				"type": 4,
				"value": []
			}, {
				"type": 5,
				"value": []
			}],
			"topN": 0,
			"version": 1
		},
		"ars": {
			"subsystems": [],
			"interval": 7200,
			"chosenGroups": [],
			"blacklist": [{
				"type": 1,
				"value": []
			}, {
				"type": 2,
				"value": []
			}, {
				"type": 3,
				"value": []
			}, {
				"type": 4,
				"value": []
			}, {
				"type": 5,
				"value": []
			}],
			"topN": 0,
			"version": 0
		},
		"mrs": {
			"chosenDLPPolicies": [],
			"interval": 7200,
			"blacklist": [{
				"type": 1,
				"value": []
			}, {
				"type": 2,
				"value": []
			}, {
				"type": 3,
				"value": []
			}, {
				"type": 4,
				"value": []
			}, {
				"type": 5,
				"value": []
			}],
			"topN": 0,
			"version": 0,
			"uploadToLab": True,
			"retrospectiveDays": 7
		}
	}
}

device_itmconfigs_data = {
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

ers_models_data = {
        "modelID_list": [
            # # "17e02e9c-0e6b-4515-ab68-5289c300236c",
            # "17e02e9c-0e6b-4515-ab68-5289c300236d",
            # # "74b5d421-09c5-49ba-ba94-fbbe954f64b5",
            # "74b5d421-09c5-49ba-ba94-fbbe954f64b6",
            # # "88350800-a94f-11ea-bb37-0242ac130002"
            # "88350800-a94f-11ea-bb37-0242ac130003"
        ]
    }

ers_models_file = {
        "filename": filename
    }

mrs_tasks_data = {
        "chosenGroups": [],
        "action": 5
    }
taskID ="689a80b4-cc24-4f4c-95cf-63f9c12441ad"

eas_parameters_data = {
        "parameters": {
            "6a6887d4-b195-7ceb-f1d3-4d66eaf164a9_91840212-f491-11e9-a861-9a17b6b6610c": {
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

anomaliesSummary_data = {
        # "startTimestamp": 1549764000,
        "startTimestamp": 1570896000,
        "endTimestamp": int(time_now),
        # "pageSize": 3,
        "pageSize": 20,
        "page": 1,
        # "page": 1,
        # "filter":[{"type":3, "value":["*lianpengcheng", "*"]},{
        #             "type": 5,
        #             "value": [
        #                 "f023d38e-27ed-3443-b3b5-695556fb21e6"
        #             ]
        #         }]
        "filter": [{"type": 3, "value": ["*"]}]
    }
eas_report_data = {
        "startTimestamp": 1570896000,
        "endTimestamp": int(time_now),
        "top": 5,
        # "filter": [
        #     {
        #         "type": 3,
        #         "value": [
        #             "*lianpengcheng",
        #             "*zhao*"
        #         ]
        #     },
        #     {
        #         "type": 5,
        #         "value": [
        #             "f023d38e-27ed-3443-b3b5-695556fb21e6"
        #         ]
        #     }
        # ]
        "filter": [{"type": 3, "value": ["*"]}]
    }

ers_forensics_data = {
    "timestamp": int(time_now),
    # "user": "d2ba046c-67c6-467c-b7ce-15015e6f0436",
    "user": "5fe5bc26-3ea4-4904-a95c-f9fce9bf0705",
    "pageSize": 1
}

ars_forensics_data = {
    "timestamp": int(time_now),
    "user": "d2ba046c-67c6-467c-b7ce-15015e6f0436",
    "pageSize": 1
}


device_ars_conf = {u'status': 0, u'ars': device_configuration['itmConfigs']['ars']}
device_mrs_conf = {u'status': 0, u'mrs': device_configuration['itmConfigs']['mrs']}
device_ers_conf = {u'status': 0, u'ers': device_configuration['itmConfigs']['ers']}

device_versions = {u'status': 0, u'version': {u'ars': device_ars_conf['ars']['version'], u'mrs': device_mrs_conf['mrs']['version'], u'ers': device_ers_conf['ers']['version']}}

# added by wendong
device_ars_blacklists_conf = {u'status': 0, u'blacklist': device_configuration['itmConfigs']['ars']['blacklist']}
device_mrs_blacklists_conf = {u'status': 0, u'blacklist': device_configuration['itmConfigs']['mrs']['blacklist']}
device_ers_blacklists_conf = {u'status': 0, u'blacklist': device_configuration['itmConfigs']['ers']['blacklist']}

post_ars_conf = {u'subsystems': [], u'interval': 7200, u'chosenGroups': [], u'blacklist': [], u'topN': 0, u'version': 1}
post_ers_conf = {u'interval': 7200, u'ChosenModels': [], u'modelParameterMap': [], u'blacklist': [], u'topN': 0, u'version': 1}
post_mrs_conf = {u'chosenDLPPolicies': [], u'interval': 7200, u'blacklist': [], u'topN': 0, u'version': 1, u'uploadToLab': True, u'retrospectiveDays': 7}

x_scores = {
    u'status': 0,
    u'arsScores': {u'order': [], u'defaults': 0.2, u'scores': {}},
    u'ersScores': {u'order': [], u'defaults': 0.2, u'scores': {}},
    u'mrsScores': {u'order': [], u'defaults': 0.2, u'scores': {}},
    u'weights': {u'aWeight': 0.333, u'mWeight': 0.333, u'eWeight': 0.333}
}

ars_scores = {u'status': 0, u'arsScores': {u'order': [], u'defaults': 0.2, u'scores': {}}}
ers_scores = {u'status': 0, u'ersScores': {u'order': [], u'defaults': 0.2, u'scores': {}}}
mrs_scores = {u'status': 0, u'mrsScores': {u'order': [], u'defaults': 0.2, u'scores': {}}}

train_status = {
    u'status': 0,
    u'tasks': [{
        u'policyID': u'db418b15-8577-46fe-a0b4-794f6859df49',
        u'taskStatus': [
            {u'status': 3, u'groupID': u'cfb7a0f1-68b5-8442-86ff-ff6bda35a561'},
            {u'status': 3, u'groupID': u'34f399bd-c8da-ef4c-b09a-cec493ca79a8'}]
    }],
    u'deviceID': u'deviceID-lian'
}

ers_models = {
    u'status': 0, 
    u'version': 1042, 
    u'ersModels': [{u'modelVersion': 2.1, u'modelParameters': [{u'name': {u'en': u'Send Resume to External Domain', u'zh': u'\u5916\u53d1\u7b80\u5386'}, 
        u'needConfig': False, u'MappedPolicyID': u'53b4da47-c20c-434b-96a5-8d5558a00ae1', u'sourceIndex': 2, 
        u'paramID': u'ed7d914d-e4ff-4d6f-abc5-a9eb823b1c69', u'type': u'built-in', u'display': True}, 
        {u'name': {u'en': u'Visiting Job Search Sites', u'zh': u'\u8bbf\u95ee\u62db\u8058\u7f51\u7ad9'}, 
        u'needConfig': False, u'MappedPolicyID': u'e57de732-143d-4d78-8e8b-20c4e743a4a4', u'sourceIndex': 1, 
        u'paramID': u'e57de732-143d-4d78-8e8b-20c4e743a4a4', u'type': u'built-in', u'display': True}, 
        {u'name': {u'en': u'Sending Multiple Files to External', u'zh': u'\u5916\u53d1\u6587\u4ef6\u6b21\u6570\u5f02\u5e38'}, 
        u'needConfig': False, u'MappedPolicyID': u'fc89677c-68f5-4e5d-ae63-694dd9e40289', u'sourceIndex': 1, 
        u'paramID': u'fc89677c-68f5-4e5d-ae63-694dd9e40289', u'type': u'built-in', u'display': True}, 
        {u'name': {u'en': u'Sending Over-sized Files to External', u'zh': u'\u5916\u53d1\u6587\u4ef6\u5927\u5c0f\u5f02\u5e38'}, 
        u'needConfig': False, u'MappedPolicyID': u'05b218e5-b28c-457a-8e25-ba6de025242a', u'sourceIndex': 1, u'paramID': u'05b218e5-b28c-457a-8e25-ba6de025242a', 
        u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Encrypted Files to External', u'zh': u'\u5916\u53d1\u52a0\u5bc6\u6587\u4ef6'}, 
        u'needConfig': False, u'MappedPolicyID': u'689a80b4-cc24-4f4c-95cf-63f9c12441ad', u'sourceIndex': 2, u'paramID': u'1ff2bda5-3de9-46f9-995d-05428e0eccd7', 
        u'type': u'built-in', u'display': True}, {u'paramID': u'5cbb7c50-df10-440f-92a6-ca0d59bad896', 
        u'name': {u'en': u'Violating DLP Policy', u'zh': u'\u89e6\u53d1\u5173\u952eDLP\u7b56\u7565'}, u'needConfig': True, u'sourceIndex': 2, u'cardinality': 3, 
        u'type': u'user-set', u'display': True}], u'description': {u'en': u'Unethical employee stealing confidential data before resignation.', 
        u'zh': u'\u4e0d\u9053\u5fb7\u5458\u5de5\u79bb\u804c\u524d\u5077\u7a83\u6570\u636e\u7684\u884c\u4e3a\u6a21\u5f0f'}, 
        u'displayName': {u'en': u'Employee Resignation Data Loss Risks', u'zh': u'\u5458\u5de5\u79bb\u804c\u6cc4\u5bc6\u98ce\u9669'}, 
        u'modelID': u'fd4d8c8b-35ba-498d-bb41-a4c0bc8f325a'}, {u'modelVersion': 2.1, u'modelParameters': [{u'name': {u'en': u'Downloading Malware', 
        u'zh': u'\u4e0b\u8f7d\u6076\u4ef6'}, u'needConfig': False, u'MappedPolicyID': u'3a8573fb-dcc7-4b9c-9b6f-e7ce141fe84c', u'sourceIndex': 1, 
        u'paramID': u'3a8573fb-dcc7-4b9c-9b6f-e7ce141fe84c', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Visiting Insecure Sites', 
        u'zh': u'\u8bbf\u95ee\u4e0d\u5b89\u5168\u7f51\u7ad9'}, u'needConfig': False, u'MappedPolicyID': u'608bc492-ea58-40c6-8523-029d4f537f85', 
        u'sourceIndex': 1, u'paramID': u'608bc492-ea58-40c6-8523-029d4f537f85', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Confidential Files to External', 
        u'zh': u'\u5916\u53d1\u5f02\u5e38\u6587\u4ef6\u884c\u4e3a'}, u'needConfig': False, 
        u'MappedPolicyID': u'689a80b4-cc24-4f4c-95cf-63f9c12441ad,12b79401-0255-4e50-8571-25ad5d8db0e6,2c949b49-1008-41d6-9712-ab0eacfdfbef', u'sourceIndex': 2, 
        u'paramID': u'178c95bc-0c85-4c48-b5be-21fe91cd0a41', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Data to External in Non-working Hours', 
        u'zh': u'\u975e\u5de5\u4f5c\u65f6\u95f4\u5916\u53d1\u6570\u636e'}, u'needConfig': False, u'MappedPolicyID': u'911e4038-4f78-4362-86b4-b1e5b0b4ece8', 
        u'sourceIndex': 1, u'paramID': u'911e4038-4f78-4362-86b4-b1e5b0b4ece8', u'type': u'built-in', u'display': True}, 
        {u'name': {u'en': u'Sending Over-sized Files to External in Non-working Hours', u'zh': u'\u975e\u5de5\u4f5c\u65f6\u95f4\u5916\u53d1\u6570\u636e\u5927\u5c0f\u5f02\u5e38'}, 
        u'needConfig': False, u'MappedPolicyID': u'23bb46f4-eae1-40c0-9fe0-2a9a40025084', u'sourceIndex': 1, u'paramID': u'23bb46f4-eae1-40c0-9fe0-2a9a40025084', 
        u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Passwords to External', u'zh': u'\u5916\u53d1\u5bc6\u7801\u6587\u4ef6'}, u'needConfig': False, 
        u'MappedPolicyID': u'b6d66fbc-af10-401c-ab88-baf9d6307bea', u'sourceIndex': 2, u'paramID': u'839587ab-30a2-469a-af44-212aedef2963', u'type': u'built-in', u'display': True}, 
        {u'paramID': u'5cbb7c50-df10-440f-92a6-ca0d59bad896', u'name': {u'en': u'Violating DLP Policy', u'zh': u'\u89e6\u53d1\u5173\u952eDLP\u7b56\u7565'}, u'needConfig': True, 
        u'sourceIndex': 2, u'cardinality': 3, u'type': u'user-set', u'display': True}], u'description': {u'en': u'Employee infecting devices with Trojan virus. ', 
        u'zh': u'\u8bbe\u5907\u611f\u67d3\u6728\u9a6c\u6cc4\u5bc6\u6570\u636e\u7684\u884c\u4e3a\u6a21\u5f0f'}, u'displayName': {u'en': u'Trojan Infection Data Loss Risks', 
        u'zh': u'\u611f\u67d3\u6728\u9a6c\u6cc4\u5bc6\u98ce\u9669'}, u'modelID': u'd947b2d2-7ed2-40fe-9456-34b37d709467'}, {u'modelVersion': 2.1, u'modelParameters': 
        [{u'paramID': u'2e3bec1e-84de-403f-b523-9b0f71cf73d7', u'name': {u'en': u'Copying Sensitive Data to Removable Media', 
        u'zh': u'\u62f7\u8d1d\u654f\u611f\u6587\u4ef6\u5230\u79fb\u52a8\u5b58\u50a8\u8bbe\u5907'}, u'needConfig': True, u'sourceIndex': 2, u'cardinality': 3, 
        u'type': u'user-set', u'display': True}, {u'name': {u'en': u'Uploading Sensitive File to NetDisk', u'zh': u'\u4e0a\u4f20\u654f\u611f\u6587\u4ef6\u5230\u7f51\u76d8'}, 
        u'needConfig': False, u'MappedPolicyID': u'f2d5d705-2ff8-468f-957f-ace1121ccf5a', u'sourceIndex': 1, u'paramID': u'f2d5d705-2ff8-468f-957f-ace1121ccf5a', 
        u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Email to Personal External Mailbox', u'zh': u'\u53d1\u9001\u90ae\u4ef6\u81f3\u4e2a\u4eba\u5916\u7f51\u90ae\u7bb1'}, 
        u'needConfig': False, u'MappedPolicyID': u'582536e3-54ad-41c6-979c-0437018bb4ab', u'sourceIndex': 2, u'paramID': u'0f352f05-7811-4939-be1c-ea0cde94c102', 
        u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Encrypted Files to External', u'zh': u'\u5916\u53d1\u52a0\u5bc6\u6587\u4ef6'}, u'needConfig': False, 
        u'MappedPolicyID': u'689a80b4-cc24-4f4c-95cf-63f9c12441ad', u'sourceIndex': 2, u'paramID': u'1ff2bda5-3de9-46f9-995d-05428e0eccd7', u'type': u'built-in', u'display': True}, 
        {u'paramID': u'5cbb7c50-df10-440f-92a6-ca0d59bad896', u'name': {u'en': u'Violating DLP Policy', u'zh': u'\u89e6\u53d1\u5173\u952eDLP\u7b56\u7565'}, 
        u'needConfig': True, u'sourceIndex': 2, u'cardinality': 3, u'type': u'user-set', u'display': True}], u'description': {u'en': u'Malicious employee stealing confidential data.', 
        u'zh': u'\u6076\u610f\u5458\u5de5\u76d7\u7a83\u6570\u636e\u7684\u884c\u4e3a\u6a21\u5f0f'}, u'displayName': {u'en': u'Malicious User Data Loss Risks', 
        u'zh': u'\u6076\u610f\u7528\u6237\u6cc4\u5bc6\u98ce\u9669'}, u'modelID': u'74b5d421-09c5-49ba-ba94-fbbe954f64b5'}, {u'modelVersion': 2.1, u'modelParameters': 
        [{u'name': {u'en': u'Sending Multiple Files to External', u'zh': u'\u5916\u53d1\u6587\u4ef6\u6b21\u6570\u5f02\u5e38'}, u'needConfig': False, 
        u'MappedPolicyID': u'fc89677c-68f5-4e5d-ae63-694dd9e40289', u'sourceIndex': 1, u'paramID': u'fc89677c-68f5-4e5d-ae63-694dd9e40289', u'type': u'built-in', u'display': True}, 
        {u'name': {u'en': u'Sending Over-sized Files to External', u'zh': u'\u5916\u53d1\u6587\u4ef6\u5927\u5c0f\u5f02\u5e38'}, u'needConfig': False, 
        u'MappedPolicyID': u'05b218e5-b28c-457a-8e25-ba6de025242a', u'sourceIndex': 1, u'paramID': u'05b218e5-b28c-457a-8e25-ba6de025242a', u'type': u'built-in', u'display': True}, 
        {u'name': {u'en': u'Sending Data to External in Non-working Hours', u'zh': u'\u975e\u5de5\u4f5c\u65f6\u95f4\u5916\u53d1\u6570\u636e'}, u'needConfig': False, 
        u'MappedPolicyID': u'911e4038-4f78-4362-86b4-b1e5b0b4ece8', u'sourceIndex': 1, u'paramID': u'911e4038-4f78-4362-86b4-b1e5b0b4ece8', u'type': u'built-in', 
        u'display': True}, {u'name': {u'en': u'Sending Files to GitHub or SVN', u'zh': u'\u5411GitHub\u6216SVN\u4f20\u8f93\u6587\u4ef6'}, u'needConfig': False, 
        u'MappedPolicyID': u'361bae3d-96b4-43a1-93e1-59b68d26163d', u'sourceIndex': 1, u'paramID': u'361bae3d-96b4-43a1-93e1-59b68d26163d', u'type': u'built-in', u'display': True}, 
        {u'name': {u'en': u'Sending Source Code to External', u'zh': u'\u5916\u53d1\u7814\u53d1\u4ee3\u7801\u5185\u5bb9'}, u'needConfig': False, 
        u'MappedPolicyID': u'8e2d1942-e5bf-497f-9f5a-20de297c760a', u'sourceIndex': 2, u'paramID': u'3d8a619e-e74b-4c1a-a29a-354f3af8959a', u'type': u'built-in', u'display': True}],
        u'description': {u'en': u'Research and Development employee losing confidential data', 
        u'zh': u'\u7814\u53d1\u5de5\u4f5c\u4eba\u5458\u6570\u636e\u6cc4\u5bc6\u7684\u884c\u4e3a\u6a21\u5f0f'}, 
        u'displayName': {u'en': u'Research and Development Data Loss Risks', u'zh': u'\u7814\u53d1\u6570\u636e\u6cc4\u5bc6\u98ce\u9669'}, 
        u'modelID': u'def6d838-58bc-4bb4-93fb-66fc90a8061d'}, {u'modelVersion': 2.1, u'modelParameters': [{u'name': {u'en': u'Sending Multiple Files to External', 
        u'zh': u'\u5916\u53d1\u6587\u4ef6\u6b21\u6570\u5f02\u5e38'}, u'needConfig': False, u'MappedPolicyID': u'fc89677c-68f5-4e5d-ae63-694dd9e40289', u'sourceIndex': 1, 
        u'paramID': u'fc89677c-68f5-4e5d-ae63-694dd9e40289', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Over-sized Files to External', 
        u'zh': u'\u5916\u53d1\u6587\u4ef6\u5927\u5c0f\u5f02\u5e38'}, u'needConfig': False, u'MappedPolicyID': u'05b218e5-b28c-457a-8e25-ba6de025242a', u'sourceIndex': 1, 
        u'paramID': u'05b218e5-b28c-457a-8e25-ba6de025242a', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Data to External in Non-working Hours', 
        u'zh': u'\u975e\u5de5\u4f5c\u65f6\u95f4\u5916\u53d1\u6570\u636e'}, u'needConfig': False, u'MappedPolicyID': u'911e4038-4f78-4362-86b4-b1e5b0b4ece8', u'sourceIndex': 1, 
        u'paramID': u'911e4038-4f78-4362-86b4-b1e5b0b4ece8', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Confidential Files to External', 
        u'zh': u'\u5916\u53d1\u5f02\u5e38\u6587\u4ef6\u884c\u4e3a'}, u'needConfig': False, 
        u'MappedPolicyID': u'689a80b4-cc24-4f4c-95cf-63f9c12441ad,12b79401-0255-4e50-8571-25ad5d8db0e6,2c949b49-1008-41d6-9712-ab0eacfdfbef', u'sourceIndex': 2, 
        u'paramID': u'178c95bc-0c85-4c48-b5be-21fe91cd0a41', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Unknown Files to External', 
        u'zh': u'\u5916\u53d1\u672a\u77e5\u6587\u4ef6\u7c7b\u578b'}, u'needConfig': False, u'MappedPolicyID': u'd59fbb85-26b6-4d86-8a76-86587db356ff', u'sourceIndex': 2, 
        u'paramID': u'8ecf0a35-18eb-40dd-8042-2506d3595aab', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Licenses and Private Keys to External', 
        u'zh': u'\u5916\u53d1\u8bc1\u4e66\u548c\u79c1\u94a5\u6587\u4ef6'}, u'needConfig': False, u'MappedPolicyID': u'6cadfe1a-35aa-49a6-b7eb-19bfe49b9bbd', u'sourceIndex': 2, 
        u'paramID': u'ae73aaf7-27f1-46dd-ae29-80d2a9296069', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Passwords to External', 
        u'zh': u'\u5916\u53d1\u5bc6\u7801\u6587\u4ef6'}, u'needConfig': False, u'MappedPolicyID': u'b6d66fbc-af10-401c-ab88-baf9d6307bea', u'sourceIndex': 2, 
        u'paramID': u'839587ab-30a2-469a-af44-212aedef2963', u'type': u'built-in', u'display': True}, {u'paramID': u'5cbb7c50-df10-440f-92a6-ca0d59bad896', 
        u'name': {u'en': u'Violating DLP Policy', u'zh': u'\u89e6\u53d1\u5173\u952eDLP\u7b56\u7565'}, u'needConfig': True, u'sourceIndex': 2, u'cardinality': 3, 
        u'type': u'user-set', u'display': True}], u'description': {u'en': u'Action of sending abnormal data transmission by internals', 
        u'zh': u'\u5de5\u4f5c\u4eba\u5458\u5f02\u5e38\u6570\u636e\u4f20\u8f93\u6cc4\u5bc6\u7684\u884c\u4e3a\u6a21\u5f0f'}, u'displayName': 
        {u'en': u'Abnormal Transmission Data Loss Risks', u'zh': u'\u5f02\u5e38\u4f20\u8f93\u6cc4\u5bc6\u98ce\u9669'}, u'modelID': u'3b717d0b-2c00-4857-9b3b-eb5bb3563fce'}, 
        {u'modelVersion': 2.1, u'modelParameters': [{u'name': {u'en': u'Sending Emails to External via BCC', u'zh': u'\u5bc6\u9001\u90ae\u4ef6\u81f3\u5916\u7f51'}, 
        u'needConfig': False, u'MappedPolicyID': u'712fcb0e-a66f-4c86-964e-a2ffba334738', u'sourceIndex': 2, u'paramID': u'4134bce6-47c7-4ae6-ba2d-b716cf78f8ef', 
        u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Forwarding Emails to External', u'zh': u'\u8f6c\u53d1\u90ae\u4ef6\u81f3\u5916\u7f51'}, 
        u'needConfig': False, u'MappedPolicyID': u'1c8be850-22a3-44c4-8ded-6f700229ae19', u'sourceIndex': 2, u'paramID': u'309f2ee3-59eb-40cf-a10d-4095e86c97b4', 
        u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending Encrypted Files to External', u'zh': u'\u5916\u53d1\u52a0\u5bc6\u6587\u4ef6'}, 
        u'needConfig': False, u'MappedPolicyID': u'689a80b4-cc24-4f4c-95cf-63f9c12441ad', u'sourceIndex': 2, u'paramID': u'1ff2bda5-3de9-46f9-995d-05428e0eccd7', 
        u'type': u'built-in', u'display': True}, {u'paramID': u'5cbb7c50-df10-440f-92a6-ca0d59bad896', u'name': {u'en': u'Violating DLP Policy', 
        u'zh': u'\u89e6\u53d1\u5173\u952eDLP\u7b56\u7565'}, u'needConfig': True, u'sourceIndex': 2, u'cardinality': 3, u'type': u'user-set', u'display': True}], 
        u'description': {u'en': u'Employee forwarding or sending emails to external with blind carbon copy', 
        u'zh': u'\u8f6c\u53d1\u6216\u5bc6\u9001\u5916\u7f51\u90ae\u4ef6\u6cc4\u5bc6\u7684\u884c\u4e3a\u6a21\u5f0f'}, u'displayName': {
        u'en': u'Email BCC and Forward Data Loss Risks', u'zh': u'\u5bc6\u9001\u8f6c\u53d1\u6cc4\u5bc6\u98ce\u9669'}, u'modelID': u'17e02e9c-0e6b-4515-ab68-5289c300236c'}, 
        {u'modelVersion': 2.1, u'modelParameters': [{u'name': {u'en': u'Posting Questionable Information', u'zh': u'\u53d1\u5e03\u4e0d\u826f\u4fe1\u606f'}, 
        u'needConfig': False, u'MappedPolicyID': u'06e36a05-3121-4988-bd33-9ed1f29d106c', u'sourceIndex': 2, u'paramID': u'de6c9b7f-4db0-4749-91ac-294a9ec0109e', 
        u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Visiting Sites Like Forums, Blogs, and BBS', u'zh': u'\u8bbf\u95ee\u8bba\u575b\uff0c\u5fae\u535a\uff0cBBS'}, 
        u'needConfig': False, u'MappedPolicyID': u'590bd437-5e6b-43ec-b854-4ca7a1b086c2', u'sourceIndex': 1, u'paramID': u'590bd437-5e6b-43ec-b854-4ca7a1b086c2', 
        u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Visiting Sites with Extreme, Adult and Violent Contents', 
        u'zh': u'\u8bbf\u95ee\u53cd\u52a8\uff0c\u6210\u4eba\uff0c\u66b4\u529b\u7f51\u7ad9'}, u'needConfig': False, u'MappedPolicyID': u'd13783a0-1a40-4e56-86bc-2dcecd99c9b3', 
        u'sourceIndex': 1, u'paramID': u'd13783a0-1a40-4e56-86bc-2dcecd99c9b3', u'type': u'built-in', u'display': True}], u'description': 
        {u'en': u'Employee posting questionable information', u'zh': u'\u4e0d\u826f\u4fe1\u606f\u53d1\u5e03\u7684\u884c\u4e3a\u6a21\u5f0f'}, u'displayName': {u'en':
         u'Posting Questionable Information', u'zh': u'\u4e0d\u826f\u4fe1\u606f\u53d1\u5e03\u98ce\u9669'}, u'modelID': u'56fb56bd-6fe4-4b96-a490-8b7e6793d735'}, {
         u'modelVersion': 2.2, u'modelParameters': [{u'name': {u'en': u'Sending DNS requests with domain names exceeding limits on characters', 
         u'zh': u'DNS\u8bf7\u6c42\u57df\u540d\u957f\u5ea6\u5f02\u5e38'}, u'needConfig': False, u'MappedPolicyID': u'1646fb4f-da14-4760-8b5a-ecf7df0049c5', 
         u'sourceIndex': 3, u'paramID': u'1646fb4f-da14-4760-8b5a-ecf7df0049c5', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending DNS requests with invalid domain names', 
         u'zh': u'DNS\u8bf7\u6c42\u57df\u540d\u540d\u79f0\u5f02\u5e38'}, u'needConfig': False, u'MappedPolicyID': u'2c73b415-17e6-4c4e-b460-5109cbc20ed7', 
         u'sourceIndex': 3, u'paramID': u'2c73b415-17e6-4c4e-b460-5109cbc20ed7', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending invalid DNS requests', 
         u'zh': u'DNS\u8bf7\u6c42\u7c7b\u578b\u5f02\u5e38'}, u'needConfig': False, u'MappedPolicyID': u'07804c7a-b858-4d14-bdb1-58265f22b93d', u'sourceIndex': 3, 
         u'paramID': u'07804c7a-b858-4d14-bdb1-58265f22b93d', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending DNS requests with excessive data packages', 
         u'zh': u'DNS\u6570\u636e\u5305\u603b\u6570\u5f02\u5e38'}, u'needConfig': False, u'MappedPolicyID': u'cf4094e9-19f0-46b7-ae70-dbae8d169d54', u'sourceIndex': 3, 
         u'paramID': u'cf4094e9-19f0-46b7-ae70-dbae8d169d54', u'type': u'built-in', u'display': True}, {u'name': {u'en': u'Sending DNS requests with data packages exceeding limits on size', 
         u'zh': u'DNS\u6570\u636e\u5305\u957f\u5ea6\u5f02\u5e38'}, u'needConfig': False, u'MappedPolicyID': u'2dbacf05-1cad-46dd-ad94-e0f7b971b79a', u'sourceIndex': 3, 
         u'paramID': u'2dbacf05-1cad-46dd-ad94-e0f7b971b79a', u'type': u'built-in', u'display': True}], u'description': {
         u'en': u'Action of sending abnormal DNS requests which may cause data loss', u'zh': u'DNS\u5f02\u5e38\u6570\u636e\u6cc4\u5bc6\u7684\u884c\u4e3a\u6a21\u5f0f'}, 
         u'displayName': {u'en': u'DNS Anomaly Data Loss Risks', u'zh': u'DNS\u5f02\u5e38\u6cc4\u5bc6\u98ce\u9669'}, u'modelID': u'badf93c0-12aa-4f68-abf2-aff067bf15ca'}, 
         {u'modelVersion': 2.1, u'modelParameters': [{u'isSecure': False, u'name': {u'en': u'Visiting Sites Like Forums, Blogs, and BBS', 
         u'zh': u'\u8bbf\u95ee\u8bba\u575b\u5fae\u535a\u7f51\u7ad9'}, u'categoryType': [770, 771, 772, 773, 774, 1029], u'needConfig': False, 
         u'MappedPolicyID': u'91410e12-8893-4b3d-aa94-7318d862352d', u'isVirus': False, u'cardinality': 3, u'paramID': u'91410e12-8893-4b3d-aa94-7318d862352d', 
         u'type': u'built-in', u'display': True}, {u'isSecure': False, u'name': {u'en': u'Visiting Sites Like shopping', u'zh': u'\u8bbf\u95ee\u8d2d\u7269\u5a31\u4e50\u7f51\u7ad9'}, 
         u'categoryType': [1025, 1026, 1035, 1279, 769], u'needConfig': False, u'MappedPolicyID': u'7ff0437f-13c8-4adb-9df8-fc671213e96c', u'isVirus': False,
         u'cardinality': 3, u'paramID': u'7ff0437f-13c8-4adb-9df8-fc671213e96c', u'type': u'built-in', u'display': True}, {u'cardinality': 3, u'name': {
         u'en': u'Violating DLP Policy', u'zh': u'\u89e6\u53d1\u5173\u952eDLP\u7b56\u7565'}, u'needConfig': True, u'paramID': u'5cbb7c50-df10-440f-92a6-ca0d59bad896', 
         u'type': u'user-set', u'display': True}], u'description': {u'en': u'Behaviour of Entertainment', u'zh': u'\u5de5\u4f5c\u65f6\u95f4\u5a31\u4e50\u7684\u884c\u4e3a\u6a21\u5f0f'}, 
         u'displayName': {u'en': u'Entertainment Model', u'zh': u'\u8bbf\u95ee\u5de5\u4f5c\u65e0\u5173\u5185\u5bb9'}, u'modelID': u'daff19f5-6309-4ea0-aaac-8daefde3b036'}]}

ers_models_version = {u'status': 0, u'version': 1042}

# added by wendong
