# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-06-15 15:42:19
File Name: test_api.py @v1.0
"""
from tests.case_api import *

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bean.settings")
django.setup()

from django.urls import reverse


clientIP = None
sessionID = None
headers = None


class APITestCase(unittest.TestCase):
    """API Test Case"""

    def setUp(self):
        response = req.post(uri + reverse('check-in'), json=login_data)
        globals()['sessionID'] = response.json().get('sessionID')
        globals()['clientIP'] = response.json().get('clientIP')
        globals()['headers'] = {'Authorization': 'basic ' + base64.b64encode(clientIP + ":" + sessionID)}

    def tearDown(self):
        pass

    def test_check_in(self):
        """
        check in
        """
        response = req.post(uri + reverse('check-in'), json=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 4)
        self.assertEqual(response.json().get('status'), 0)
        self.assertEqual(response.json().get('sessionTimeout'), 3600)

    def test_keeplive(self):
        """
        keep live
        """
        response = req.get(uri + reverse('login-out', args=(sessionID,)), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        self.assertEqual(response.json().get('sessionTimeout'), 3600)

    def test_check_out(self):
        """
        check out
        """
        response = req.delete(uri + reverse('login-out', args=(sessionID,)), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        self.assertEqual(response.json().get('username'), username)
        self.assertEqual(response.json().get('sessionID'), sessionID)

    def test_register(self):
        """
        register
        """
        response = req.delete(test_URL + 'itm_configs/itm_configs/' + deviceID + '?refresh=true')
        self.assertEqual(response.json().get('result'), 'deleted')
        response = req.post(uri + reverse('register', args=(deviceID,)), json=device_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        response = req.delete(uri + reverse('register', args=(deviceID,)), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        self.assertEqual(response.json().get('deviceID'), device_data.get('deviceID'))
        self.assertEqual(response.json().get('logSources'), device_data.get('logSources'))
        self.assertEqual(response.json().get('deviceName'), device_data.get('deviceName'))
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'ars')), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 4)
        response = req.post(uri + reverse('register', args=(deviceID,)), json=device_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)

    def test_disregister(self):
        """
        disregister
        """
        pass

    def test_configuration(self):
        """
        configuration
        """
        response = req.get(uri + reverse('configuration', args=(deviceID,)), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        self.assertDictEqual(response.json(), device_configuration)

    def test_get_conf_ars(self):
        """
        get conf ars
        """
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'ars')), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        self.assertEqual(response.json(), device_ars_conf)

    def test_get_conf_mrs(self):
        """
        get conf mrs
        """
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'mrs')), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        self.assertEqual(response.json(), device_mrs_conf)

    def test_get_conf_ers(self):
        """
        get conf ers
        """
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'ers')), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        self.assertEqual(response.json(), device_ers_conf)

    def test_get_conf_versions(self):
        """
        get conf versions
        """
        response = req.get(uri + reverse('conf-xrs', args=(deviceID, 'versions')), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        self.assertEqual(response.json(), device_versions)

    def test_post_conf_ars(self):
        """
        post conf ars
        """
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'ars')), json=post_ars_conf, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'ars')), json=device_ars_conf['ars'], headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)

    def test_post_conf_mrs(self):
        """
        post conf mrs
        """
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'mrs')), json=post_mrs_conf, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'mrs')), json=device_mrs_conf['mrs'], headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)

    def test_post_conf_ers(self):
        """
        post conf ers
        """
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'ers')), json=post_ers_conf, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'ers')), json=device_ers_conf['ers'], headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)

    def test_post_balcklist_ars(self):
        """
        post conf ars
        """
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'ars', 'blacklists')), json={"blacklist": [{"type": 1, "value": "172.22.118.55"}]}, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)

    def test_post_balcklist_mrs(self):
        """
        post conf mrs
        """
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'mrs', 'blacklists')), json={"blacklist": [{"type": 1, "value": "172.22.118.55"}]}, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)

    def test_post_balcklist_ers(self):
        """
        post conf ers
        """
        response = req.post(uri + reverse('conf-xrs', args=(deviceID, 'ers', 'blacklists')), json={"blacklist": [{"type": 1, "value": "172.22.118.55"}]}, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 0)

    def test_x_scores(self):
        """
        x_scores
        """
        response = req.get(uri + reverse('x-scores', args=(deviceID,)), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), x_scores)

    def test_ars_scores(self):
        """
        ars scores
        """
        response = req.get(uri + reverse('x-scores', args=(deviceID, 'arsScores')), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), ars_scores)

    def test_ers_scores(self):
        """
        ers scores
        """
        response = req.get(uri + reverse('x-scores', args=(deviceID, 'ersScores')), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), ers_scores)

    def test_mrs_scores(self):
        """
        mrs scores
        """
        response = req.get(uri + reverse('x-scores', args=(deviceID, 'mrsScores')), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), mrs_scores)

    def test_mrs_tasks(self):
        """
        mrs task
        """
        response = req.post(uri + reverse('mrs-tasks', args=(deviceID, deviceID)), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 1)

    def test_tasks_status(self):
        """
        tasks status
        """
        response = req.get(uri + reverse('tasks-status', args=(deviceID,)), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), train_status)

    def test_ers_models(self):
        """
        ers models
        """
        response = req.get(uri + reverse('ers-models'), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ers_models)

    def test_ers_models_version(self):
        """
        ers models version
        """
        response = req.get(uri + reverse('ers-models', args=('version',)), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ers_models_version)
