# -*- coding: utf-8 -*-
'''
User Name: wendong@skyguard.com.cn
Date Time: 11/2/20 10:01 AM
File Name: test_api_vi.py
Version: 1.0
info:
    1.when testing, cannot run the test_logout
    2.once testing configs, cannot run the disregister
'''

from case_api import *
import pytest
import requests
import django
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bean.settings")
django.setup()

clientIP = None
sessionID = None
headers = None

# everytime the module run, setup_module run first, for once
def setup_module():
    print "Getting session..."
    response = requests.post(uri + reverse('check-in'), json=login_data)
    globals()['sessionID'] = response.json().get('sessionID')
    globals()['clientIP'] = response.json().get('clientIP')
    globals()['headers'] = {'Authorization': 'basic ' + base64.b64encode(clientIP + ":" + sessionID)}

# before the module end, teardown_module run, for once
def teardown_module():
    pass

class TestDeviceManager:
    """views002"""

    def test_register(self):
        """test register"""
        response = requests.post(uri + reverse('register', args=(deviceID,)), json=device_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"

    '''
    def test_disregister(self):
        """test disregister"""
        response = req.delete(uri + reverse('register', args=(deviceID,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 4, "response data's items should be 4"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json().get('deviceName') == "wen-test-ucss"
        assert response.json().get('deviceID') == "deviceID-wen"
    '''

    def test_itmconfigs(self):
        """test itmconfigs"""
        response = requests.post(uri + reverse('itm-configs', args=(deviceID,)), json=device_itmconfigs_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"

    def test_configuration(self):
        """test configuration"""
        response = requests.get(uri + reverse('configuration', args=(deviceID,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_configuration

    def test_get_conf_ars(self):
        """test ars_conf"""
        response = requests.get(uri + reverse('conf-xrs', args=(deviceID, 'ars')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_ars_conf

    def test_get_conf_ers(self):
        """test ers_conf"""
        response = requests.get(uri + reverse('conf-xrs', args=(deviceID, 'ers')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_ers_conf

    def test_get_conf_mrs(self):
        """test mrs_conf"""
        response = requests.get(uri + reverse('conf-xrs', args=(deviceID, 'mrs')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_mrs_conf

    def test_get_conf_version(self):
        """test conf_versions"""
        response = requests.get(uri + reverse('conf-xrs', args=(deviceID, 'versions')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_versions

    def test_get_conf_ars_blacklists(self):
        """test conf_ars_blacklists"""
        response = requests.get(uri + reverse('conf-xrs', args=(deviceID, 'ars', 'blacklists')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_ars_blacklists_conf

    def test_get_conf_ers_blacklists(self):
        """test conf_ers_blacklists"""
        response = requests.get(uri + reverse('conf-xrs', args=(deviceID, 'ers', 'blacklists')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_ers_blacklists_conf

    def test_get_conf_mrs_blacklists(self):
        """test conf_mrs_blacklists"""
        response = requests.get(uri + reverse('conf-xrs', args=(deviceID, 'mrs', 'blacklists')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_mrs_blacklists_conf

    def test_post_conf_ars(self):
        """test conf_ars"""
        response = requests.post(uri + reverse('conf-xrs', args=(deviceID, 'ars')),json=post_ars_conf, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"

    def test_post_conf_ers(self):
        """test conf_ers"""
        response = requests.post(uri + reverse('conf-xrs', args=(deviceID, 'ers')), json=post_ers_conf, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"

    def test_post_conf_mrs(self):
        """test conf_mrs"""
        response = requests.post(uri + reverse('conf-xrs', args=(deviceID, 'mrs')), json=post_mrs_conf, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"

    def test_post_conf_ars_blacklists(self):
        pass

    def test_post_conf_ers_blacklists(self):
        pass

    def test_post_conf_mrs_blacklists(self):
        pass

class TestFileManager:
    """views003"""
    def test_upload_file(self):
       """test upload_file"""
       response = requests.post(uri + reverse('upload-file', ), json=filename, headers=headers)
       assert response.status_code == 200, "response status code should be 200"
       assert response.json().get('status') == 0, "if response succeeded, status is 0"


    def test_download_file(self):
        """test download_file"""
        response = requests.get(uri + reverse('download-file', ), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        for key in response.json():
            if key != "status":
                assert key == "download_list"
        # response = req.get(uri + reverse('download-file', args=(filename,)), headers=headers)
        # assert response.status_code == 200, "response status code should be 200"
        # assert response.json().get('status') == 0, "if response succeeded, status is 0"

class TestModelsManager:
    """views004"""

    def test_get_ers_models(self):
        """test ers_models"""
        response = requests.get(uri + reverse("ers-models", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0
        response = requests.get(uri + reverse("ers-models", args=(deviceID_1, 'version')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_ers_models(self):
        """test ers_models"""
        response = requests.delete(uri + reverse("ers-models", args=(deviceID_1,)), json=ers_models_file, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_delete_ers_models(self):
        """test ers_models"""
        response = requests.delete(uri + reverse("ers-models", args=(deviceID_1,)), json=ers_models_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_mrs_tasks(self):
        """test mrs_tasks"""
        response = requests.post(uri + reverse("mrs-tasks", args=(deviceID_1,taskID)), json=mrs_tasks_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_tasks_status(self):
        """test tasks_status >>> mrs_tasks"""
        response = requests.get(uri + reverse("tasks-status", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 3, "there are status and deviceID,tasks"
        assert response.json().get('status') == 0

    def test_eas_anomaly(self):
        """test eas_anomaly"""
        response = requests.get(uri + reverse("eas-anomaly", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0
        response = requests.get(uri + reverse("eas-anomaly", args=(deviceID_1, anomalyID)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_get_eas_parameters(self):
        """test eas_parameters"""
        response = requests.get(uri + reverse("eas-parameters", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0
        response = requests.get(uri + reverse("eas-parameters", args=(deviceID_1, paramID)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        print response.json()
        assert response.json().get('status') == 0 # todo

    def test_post_eas_parameters(self):
        "test eas_parameters"
        response = req.get(uri + reverse("eas-parameters", args=(deviceID_1,)), json=eas_parameters_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        print response.json()
        assert response.json().get('status') == 0

class TestScores:
    """views005"""

    def test_data_info(self):
        """test data_info"""
        response = requests.get(uri + reverse("data-info", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 2, "there are status and threats"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"

    def test_get_x_scores(self):
        """test x_scores"""
        response = requests.get(uri + reverse("x-scores", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(
            response.json()) == 6, "there are status and scores >>> arsScores|mrsScores|ersScores|weights|riskLevel"
        assert response.json().get('status') == 0

    def test_get_ars_scores(self):
        """test ars_scores"""
        response = requests.get(uri + reverse("x-scores", args=(deviceID_1, 'arsScores')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_get_ers_scores(self):
        """test ers_scores"""
        response = requests.get(uri + reverse("x-scores", args=(deviceID_1, 'ersScores')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_get_mrs_scores(self):
        """test mrs_scores"""
        response = requests.get(uri + reverse("x-scores", args=(deviceID_1, 'mrsScores')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_get_weights_scores(self):
        """test weights_scores"""
        response = requests.get(uri + reverse("x-scores", args=(deviceID_1, 'weights')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_get_riskLevel_scores(self):
        """test riskLevel_scores"""
        response = requests.get(uri + reverse("x-scores", args=(deviceID_1, 'riskLevel')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

class TestForensics:
    """views006"""

    def test_anomaliesSummary(self):
        """test anomaliesSummary"""
        response = requests.post(uri + reverse("anomaliesSummary", args=(deviceID_1,)), json=anomaliesSummary_data,headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0
        response = requests.post(uri + reverse("anomaliesSummary", args=(deviceID_1,anomaliesSummaryID)), json=anomaliesSummary_data,headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_eas_report(self):
        """test eas_report"""
        response = requests.post(uri + reverse("eas-report", args=(deviceID_1,)), json=eas_report_data,headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0
        response = requests.post(uri + reverse("eas-report", args=(deviceID_1, eas_reportID)), json=eas_report_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_ers_forensics(self):
        """test ers_forensics"""
        response = requests.post(uri + reverse("xrs-forensics", args=(deviceID_1,"ers")), json=ers_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_ars_forensics(self):
        """test ers_forensics"""
        response = requests.post(uri + reverse("xrs-forensics", args=(deviceID_1,"ars")), json=ers_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_ersModels_forensics(self):
        """test ers_forensics"""
        response = requests.post(uri + reverse("xrs-forensics", args=(deviceID_1, "ers", "model", modelID)), json=ers_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_ersParam_forensics(self):
        """test ers_forensics"""
        response = requests.post(uri + reverse("xrs-forensics", args=(deviceID_1,"ers", "param", nodeID)), json=ers_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_arsProtocols_forensics(self):
        """test ers_forensics"""
        response = requests.post(uri + reverse("xrs-forensics", args=(deviceID_1,"ars", "protocols")), json=ars_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_arsNetwork_forensics(self):
        """test ers_forensics"""
        response = requests.post(uri + reverse("xrs-forensics", args=(deviceID_1,"ars", "network")), json=ars_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_easThreat_forensics(self):
        """test ers_forensics"""
        response = requests.post(uri + reverse("xrs-forensics", args=(deviceID_1,"eas", "threat", threatID)), json=ars_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_easAnomalyGroup_forensics(self):
        """test ers_forensics"""
        response = requests.post(uri + reverse("xrs-forensics", args=(deviceID_1,"eas", "anomalyGroup", anomalyGroupID)), json=ars_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_easAnomaly_forensics(self):
        """test ers_forensics"""
        response = requests.post(uri + reverse("xrs-forensics", args=(deviceID_1,"eas", "anomaly", anomalyID)), json=ars_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

class TestSessionManager:
    """views001"""

    def test_checkin(self):
        """test check_in"""
        response = requests.post(uri + reverse('check-in'), json=login_data)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 4, "response data's items should be 4"
        assert response.json().get('status') == 0, "response succeeded, status is 0"
        assert response.json().get('sessionTimeout') == 3600, "sessionTimeout should be 3600"

    def test_keepalive(self):
        """test lonin_out >>> keep-alive"""
        response = requests.get(uri + reverse('login-out', args=(sessionID,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 2, "response data's items should be 2"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json().get('sessionTimeout') == 3600, "sessionTimeout should be 3600"


    def test_logout(self):
        """test login_out >>>logout"""
        response = requests.delete(uri + reverse('login-out', args=(sessionID,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 3, "response data's items should be 3"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json().get('username') == 'itm-admin', "username for test is itm-admin"

'''
class TestAPICase(object):
    """API Test Case"""

    @classmethod
    def setup_class(cls):
        print 'test is beginning...'
        response = req.post(uri + reverse('check-in'), json=login_data)
        globals()['sessionID'] = response.json().get('sessionID')
        globals()['clientIP'] = response.json().get('clientIP')
        globals()['headers'] = {'Authorization': 'basic ' + base64.b64encode(clientIP + ":" + sessionID)}


    @classmethod
    def teardown_class(cls):
        print 'test is over...'


    def test_checkin(self):
        """test check_in"""
        response = req.post(uri + reverse('check-in'), json=login_data)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 4, "response data's items should be 4"
        assert response.json().get('status') == 0, "response succeeded, status is 0"
        assert response.json().get('sessionTimeout') == 3600, "sessionTimeout should be 3600"

    def test_keepalive(self):
        """test lonin_out >>> keep-alive"""
        response = req.get(uri + reverse('login-out', args=(sessionID,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 2, "response data's items should be 2"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json().get('sessionTimeout') == 3600, "sessionTimeout should be 3600"

    
    def test_logout(self):
        """test login_out >>>logout"""
        response = req.delete(uri + reverse('login-out', args=(sessionID,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 3, "response data's items should be 3"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json().get('username') == 'itm-admin', "username for test is itm-admin"
    

    def test_register(self):
        """test register"""
        response = req.post(uri + reverse('register', args=(deviceID,)), json=device_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"

    
    def test_disregister(self):
        """test disregister"""
        response = req.delete(uri + reverse('register', args=(deviceID,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 4, "response data's items should be 4"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json().get('deviceName') == "wen-test-ucss"
        assert response.json().get('deviceID') == "deviceID-wen"
    

    def test_itmconfigs(self):
        """test itmconfigs"""
        response = req.post(uri + reverse('itm-configs', args=(deviceID,)), json=device_itmconfigs_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"


    def test_configuration(self):
        """test configuration"""
        response = req.get(uri + reverse('configuration', args=(deviceID,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_configuration


    def test_get_conf_ars(self):
        """test ars_conf"""
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'ars')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_ars_conf

    def test_get_conf_ers(self):
        """test ers_conf"""
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'ers')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_ers_conf

    def test_get_conf_mrs(self):
        """test mrs_conf"""
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'mrs')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_mrs_conf

    def test_get_conf_version(self):
        """test conf_versions"""
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'versions')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_versions

    def test_get_conf_ars_blacklists(self):
        """test conf_ars_blacklists"""
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'ars', 'blacklists')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_ars_blacklists_conf

    def test_get_conf_ers_blacklists(self):
        """test conf_ers_blacklists"""
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'ers', 'blacklists')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_ers_blacklists_conf

    def test_get_conf_mrs_blacklists(self):
        """test conf_mrs_blacklists"""
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'mrs', 'blacklists')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        assert response.json() == device_mrs_blacklists_conf


    def test_post_conf_ars(self):
        """test conf_ars"""
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'ars')),json=post_ars_conf, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"

    def test_post_conf_ers(self):
        """test conf_ers"""
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'ers')), json=post_ers_conf, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"

    def test_post_conf_mrs(self):
        """test conf_mrs"""
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'mrs')), json=post_mrs_conf, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"

    def test_post_conf_ars_blacklists(self):
        pass

    def test_post_conf_ers_blacklists(self):
        pass

    def test_post_conf_mrs_blacklists(self):
        pass

    
    def test_upload_file(self):
        """test upload_file"""
        response = req.post(uri + reverse('upload-file', ), json=filename, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
    

    def test_download_file(self):
        """test download_file"""
        response = req.get(uri + reverse('download-file', ), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"
        for key in response.json():
            if key != "status":
                assert key == "download_list"
        # response = req.get(uri + reverse('download-file', args=(filename,)), headers=headers)
        # assert response.status_code == 200, "response status code should be 200"
        # assert response.json().get('status') == 0, "if response succeeded, status is 0"


    def test_get_ers_models(self):
        """test ers_models"""
        response = req.get(uri + reverse("ers-models", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0
        response = req.get(uri + reverse("ers-models", args=(deviceID_1, 'version')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_ers_models(self):
        """test ers_models"""
        response = req.delete(uri + reverse("ers-models", args=(deviceID_1,)), json=ers_models_file, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_delete_ers_models(self):
        """test ers_models"""
        response = req.delete(uri + reverse("ers-models", args=(deviceID_1,)), json=ers_models_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_mrs_tasks(self):
        """test mrs_tasks"""
        response = req.post(uri + reverse("mrs-tasks", args=(deviceID_1,taskID)), json=mrs_tasks_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_tasks_status(self):
        """test tasks_status >>> mrs_tasks"""
        response = req.get(uri + reverse("tasks-status", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 3, "there are status and deviceID,tasks"
        assert response.json().get('status') == 0

    def test_eas_anomaly(self):
        """test eas_anomaly"""
        response = req.get(uri + reverse("eas-anomaly", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0
        response = req.get(uri + reverse("eas-anomaly", args=(deviceID_1, anomalyID)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_get_eas_parameters(self):
        """test eas_parameters"""
        response = req.get(uri + reverse("eas-parameters", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0
        response = req.get(uri + reverse("eas-parameters", args=(deviceID_1, paramID)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        print response.json()
        assert response.json().get('status') == 0 # todo

    def test_post_eas_parameters(self):
        "test eas_parameters"
        response = req.get(uri + reverse("eas-parameters", args=(deviceID_1,)), json=eas_parameters_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        print response.json()
        assert response.json().get('status') == 0


    def test_data_info(self):
        """test data_info"""
        response = req.get(uri + reverse("data-info", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 2, "there are status and threats"
        assert response.json().get('status') == 0, "if response succeeded, status is 0"

    def test_get_x_scores(self):
        """test x_scores"""
        response = req.get(uri + reverse("x-scores", args=(deviceID_1,)), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert len(response.json()) == 6, "there are status and scores >>> arsScores|mrsScores|ersScores|weights|riskLevel"
        assert response.json().get('status') == 0

    def test_get_ars_scores(self):
        """test ars_scores"""
        response = req.get(uri + reverse("x-scores", args=(deviceID_1, 'arsScores')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_get_ers_scores(self):
        """test ers_scores"""
        response = req.get(uri + reverse("x-scores", args=(deviceID_1, 'ersScores')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_get_mrs_scores(self):
        """test mrs_scores"""
        response = req.get(uri + reverse("x-scores", args=(deviceID_1, 'mrsScores')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_get_weights_scores(self):
        """test weights_scores"""
        response = req.get(uri + reverse("x-scores", args=(deviceID_1, 'weights')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_get_riskLevel_scores(self):
        """test riskLevel_scores"""
        response = req.get(uri + reverse("x-scores", args=(deviceID_1, 'riskLevel')), headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_anomaliesSummary(self):
        """test anomaliesSummary"""
        response = req.post(uri + reverse("anomaliesSummary", args=(deviceID_1,)), json=anomaliesSummary_data,headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0
        response = req.post(uri + reverse("anomaliesSummary", args=(deviceID_1,anomaliesSummaryID)), json=anomaliesSummary_data,headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_eas_report(self):
        """test eas_report"""
        response = req.post(uri + reverse("eas-report", args=(deviceID_1,)), json=eas_report_data,headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0
        response = req.post(uri + reverse("eas-report", args=(deviceID_1, eas_reportID)), json=eas_report_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_ers_forensics(self):
        """test ers_forensics"""
        response = req.post(uri + reverse("xrs-forensics", args=(deviceID_1,"ers")), json=ers_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_ars_forensics(self):
        """test ers_forensics"""
        response = req.post(uri + reverse("xrs-forensics", args=(deviceID_1,"ars")), json=ers_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_ersModels_forensics(self):
        """test ers_forensics"""
        response = req.post(uri + reverse("xrs-forensics", args=(deviceID_1, "ers", "model", modelID)), json=ers_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_ersParam_forensics(self):
        """test ers_forensics"""
        response = req.post(uri + reverse("xrs-forensics", args=(deviceID_1,"ers", "param", nodeID)), json=ers_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_arsProtocols_forensics(self):
        """test ers_forensics"""
        response = req.post(uri + reverse("xrs-forensics", args=(deviceID_1,"ars", "protocols")), json=ars_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_arsNetwork_forensics(self):
        """test ers_forensics"""
        response = req.post(uri + reverse("xrs-forensics", args=(deviceID_1,"ars", "network")), json=ars_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_easThreat_forensics(self):
        """test ers_forensics"""
        response = req.post(uri + reverse("xrs-forensics", args=(deviceID_1,"eas", "threat", threatID)), json=ars_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_easAnomalyGroup_forensics(self):
        """test ers_forensics"""
        response = req.post(uri + reverse("xrs-forensics", args=(deviceID_1,"eas", "anomalyGroup", anomalyGroupID)), json=ars_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0

    def test_post_easAnomaly_forensics(self):
        """test ers_forensics"""
        response = req.post(uri + reverse("xrs-forensics", args=(deviceID_1,"eas", "anomaly", anomalyID)), json=ars_forensics_data, headers=headers)
        assert response.status_code == 200, "response status code should be 200"
        assert response.json().get('status') == 0
'''

if __name__ == '__main__':
    pytest.main()
