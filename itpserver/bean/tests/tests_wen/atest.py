# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-06-06 14:58:19
File Name: test.py @v1.0
"""
import json
import time
import base64
import inspect
import hashlib
import datetime
# from requests.auth import HTTPBasicAuth

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from anal.models import UserProfile

username = "itm-lian"
password = "itm-admin"


def checkin():
    time_now = time.mktime(datetime.datetime.now().timetuple())
    _passwordHash = base64.b64encode(hashlib.sha256(username + str(int(time_now)) + hashlib.sha256(password).hexdigest()).hexdigest())[:12]
    data = {"username": username, "timestamp": int(time_now), "passwordHash": _passwordHash}
    return data

data = checkin()
# client = APIClient()
sessionID = None
clientIP = None
deviceID = "deviceID-lian"


class UserTestCase(TestCase):
    """User"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_user(self):
        user = User.objects.create_user(username)
        userpro = UserProfile.objects.create(user=user)
        userpro.set_passwordHash(password)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, username)
        self.assertEqual(UserProfile.objects.get().passwordHash, hashlib.sha256(password).hexdigest())


class APITestCase(TestCase):
    """API"""

    def setUp(self):
        super(APITestCase, self).setUp()
        self.client = APIClient()

        user = User.objects.create_user(username)
        userpro = UserProfile.objects.create(user=user)
        user.userprofile.set_passwordHash(password)

        response = self.client.post(reverse('check-in'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data.get('status'), 0)
        self.assertEqual(response.data.get('clientIP'), '127.0.0.1')
        self.assertEqual(response.data.get('sessionTimeout'), 3600)
        globals()['sessionID'] = response.data.get('sessionID')
        globals()['clientIP'] = response.data.get('clientIP')

    def tearDown(self):
        pass

    def test_check_in(self):
        url_name = inspect.stack()[0][3][5:].replace("_", "-")
        response = self.client.post(reverse(url_name), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data.get('status'), 0)
        self.assertEqual(response.data.get('clientIP'), '127.0.0.1')
        self.assertEqual(response.data.get('sessionTimeout'), 3600)

    def test_login_out(self):
        self.client.credentials(HTTP_AUTHORIZATION='basic ' + base64.b64encode(clientIP + ':' + sessionID))
        url_name = inspect.stack()[0][3][5:].replace("_", "-")
        response_get = self.client.get(reverse(url_name, args=(sessionID,)), format='json')
        self.assertEqual(response_get.data.get('status'), 0)
        self.assertEqual(response_get.data.get('sessionTimeout'), 3600)

        response_delete = self.client.delete(reverse(url_name, args=(sessionID,)), format='json')
        self.assertEqual(response_delete.data.get('status'), 0)
        self.assertEqual(response_delete.data.get('username'), username)
        self.assertEqual(response_delete.data.get('sessionID'), sessionID)

    def test_register(self):
        self.client.credentials(HTTP_AUTHORIZATION='basic ' + base64.b64encode(clientIP + ':' + sessionID))
        url_name = inspect.stack()[0][3][5:].replace("_", "-")
        data = {"deviceID": deviceID, "deviceName": "lian-test-ucss", "logSources": ["1.1.1.1", "2.2.2.2", "3.3.3.3"]}
        response_post = self.client.post(reverse(url_name, args=(deviceID,)), json.dumps(data), content_type='application/json')
        self.assertEqual(response_post.data.get('status'), 0)
        response_delete = self.client.delete(reverse(url_name, args=(deviceID,)))
        data["status"] = 0
        self.assertEqual(response_delete.data, data)

    def test_configuration(self):
        self.client.credentials(HTTP_AUTHORIZATION='basic ' + base64.b64encode(clientIP + ':' + sessionID))
        url_name = inspect.stack()[0][3][5:].replace("_", "-")
        response = self.client.get(reverse(url_name, args=(deviceID,)), format='json')
        print response.data
