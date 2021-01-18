# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-01-25 12:53:22
File Name: serializers.py @v3.3
"""
import os
import time
import json
import zipfile
from io import BytesIO

from django.conf import settings
from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from config import config
from models import Session
from utils import simple_datetime
from esmodels import Device, Tasks
from userinfo import get_filter_query
from authentication import APIBackendAuthentication
from exceptions import APIOBJECTERROR, APIPASSWORDERROR, APIINPUTERROR


class MultiActionSerializer(serializers.HyperlinkedModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        self.action = kwargs.pop('action', 'GET')

        super(BaseModeSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'passwordHash')

    def passwordHash(self, obj):
        return obj.userprofile.passwordHash


class UserNormalSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'id')


class PostSessionSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(max_length=30, required=True, write_only=True)
    clientIP = serializers.CharField(max_length=45, min_length=7, required=True)
    timestamp = serializers.IntegerField(required=True, write_only=True)
    passwordHash = serializers.CharField(max_length=12, min_length=12, required=True, write_only=True)
    user = serializers.SerializerMethodField()
    # future support
    # devceType = serializers.IntegerField()
    # connectionType = serializers.IntegerField()

    class Meta:
        model = Session
        fields = ('clientIP', 'username', 'timestamp', 'passwordHash', 'user')

    def get_user(self, obj):
        obj.pop('clientIP')
        Auth = APIBackendAuthentication()
        user = Auth.authenticate(**obj)
        if user is None:
            raise APIINPUTERROR(_('Authentication failure, or invalid password.'), 1)
        return user

    def validate_timestamp(self, timestamp):
        time_deviation = config.TIME_DEVIATION
        t_now = simple_datetime(None, int)
        if not t_now - time_deviation < timestamp < t_now + time_deviation:
            raise APIINPUTERROR(_('Invalid timestamp.'))
        return timestamp

    def create(self):
        session = Session.objects.create(sessionTimeout=config.SESSION_TIMEOUT * 60, **self.data)
        return SessionSerializer(session)


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    # username = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ('clientIP', 'sessionID', 'sessionTimeout')

    def get_username(self, obj):
        return obj.user.username


class GetSessionSerializer(serializers.HyperlinkedModelSerializer):
    # username = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ('sessionTimeout',)


class DeleteSessionSerializer(serializers.HyperlinkedModelSerializer):

    username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Session
        fields = ('sessionID', 'username')

    def get_username(self, obj):
        username = obj.user.username
        obj.delete()
        return username


class SessionsSerializer(MultiActionSerializer):
    username = serializers.CharField(max_length=30, required=True, write_only=True)
    clientIP = serializers.CharField(max_length=45, min_length=7, required=True)
    timestamp = serializers.IntegerField(required=True, write_only=True)
    passwordHash = serializers.CharField(max_length=12, min_length=12, required=True, write_only=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ('sessionID', 'username', 'sessionTimeout', 'clientIP', 'timestamp', 'passwordHash', 'user')
        # action == 'GET':
        # fields = ('sessionTimeout',)
        # action == 'DELETE':
        # fields = ('sessionID', 'username')
        # action == 'POST'
        # fields = ('clientIP', 'username', 'timestamp', 'passwordHash', 'user')

    def get_username(self, obj):
        username = obj.user.username
        if self.action == 'DELETE':
            obj.delete()
        return username

    def get_user(self, obj):
        obj.pop('clientIP')
        Auth = APIBackendAuthentication()
        user = Auth.authenticate(**obj)
        if user is None:
            raise APIINPUTERROR(_('Authentication failure, or invalid password.'), 1)
        return user

    def validate_timestamp(self, timestamp):
        time_deviation = config.TIME_DEVIATION
        t_now = simple_datetime(None, int)
        if not t_now - time_deviation < timestamp < t_now + time_deviation:
            raise APIINPUTERROR(_('Invalid timestamp.'))
        return timestamp

    def create(self):
        session = Session.objects.create(sessionTimeout=config.SESSION_TIMEOUT * 60, **self.data)
        return SessionSerializer(session)


class MultiSessionSerializer(object):

    @staticmethod
    def get_serializer_class(method):
        if method == 'GET':
            return GetSessionSerializer
        elif method == 'POST':
            return PostSessionSerializer
        elif method == 'DELETE':
            return DeleteSessionSerializer


class DeviceSerializer(serializers.ModelSerializer):
    deviceName = serializers.CharField(required=False)
    logSources = serializers.ListField(required=False)
    deviceID = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False, default=True)
    itmConfigs = serializers.DictField(required=False)

    class Meta:
        model = Device
        fields = ('deviceName', 'logSources', 'deviceID', 'is_active', 'itmConfigs')
        # extra_kwargs = {'is_active': {'write_only': True}}

    def create(self, validated_data):
        if 'logSources' in validated_data:
            for i in validated_data['logSources']:
                if 'passwd' in i:
                    del i['passwd']
                if 'user' in i:
                    del i['user']
        try:
            device = Device.objects.get(validated_data['deviceID']).__dict__ # update, elasticsearchORM.ElasticsearchORM.get
        except:
            device = config.DEFAULT_CONFIG
        device.update(validated_data)
        device, res = Device.objects.create(device['deviceID'], device) # esmodels.create()
        return device, res

    @property
    def data_device(self):
        return {'deviceID': self.data['deviceID'], 'deviceName': self.data['deviceName'], 'logSources': self.data['logSources']}


class DeviceBlacklistSerializer(serializers.Serializer):
    blacklist = serializers.ListField(required=True, allow_empty=False)

    def validate(self, attrs):
        blacklist = attrs['blacklist']
        if len(blacklist) != 5:
            raise ValidationError
        for i in range(5):
            if blacklist[i]['type'] != i - 1 and not isinstance(blacklist[i]['value'], list):
                raise ValidationError
        return attrs


class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def save(self):
        file = self.validated_data['file']
        file.name = str(time.time()) + "_" + file.name
        with open(os.path.join(settings.UPLOAD, file.name), 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return file.name, os.path.join(settings.UPLOAD, file.name)


class UploadModelsFileSerializer(serializers.Serializer):
    filename = serializers.FileField()

    def save(self, deviceID):
        file = self.validated_data['filename']
        file.name = str(time.time()) + "_" + file.name
        ext = file.name.split('.')[-1].lower()

        if ext != 'zip':
            raise APIOBJECTERROR(_('Only zip files are allowed.'))

        ers_config_path = config.ERS_CONFIG + deviceID
        bif_path = "/opt/skyguard/itpcompose/zodiac/EU/executor/ers_model_base_simple/bifs/"
        pwd = config.ERS_CONFIG_PWD
        fileobj = BytesIO(file.read())

        try:
            zip_hand = zipfile.ZipFile(fileobj)
            new_custom_models = json.loads(zip_hand.read('ers_custom_models.json', pwd=pwd))
            zip_hand.extractall(ers_config_path, None, pwd)
            os.system('cp {}/*.bif {}'.format(ers_config_path, bif_path))
        except RuntimeError:
            raise APIPASSWORDERROR(_('Invaild password'))

        except (ValueError, KeyError):
            raise APIOBJECTERROR(_('Invaild json'))

        except (zipfile.BadZipfile, AttributeError):
            raise APIOBJECTERROR(_('Bad zip file'))

        finally:
            zip_hand.close()

        return file.name, new_custom_models


class MRSTasksSerializer(serializers.Serializer):
    deviceID = serializers.CharField(required=True)
    taskID = serializers.CharField(required=True)
    taskIDs = serializers.ListField(allow_empty=False, write_only=True)
    action = serializers.IntegerField(required=True)
    chosenGroups = serializers.ListField(required=True)

    def validate_chosenGroups(self, chosenGroups):
        return [''] if chosenGroups == [] else chosenGroups

    def validate(self, attrs):
        if attrs['taskID'] not in attrs['taskIDs']:
            raise ValidationError
        return attrs


class TasksSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Tasks
        fields = ('deviceID', 'tasks')

    def get_tasks(self, obj):
        tasks = [{"policyID": i, "taskStatus": []} for i in list(set([i["policyID"] for i in obj.tasks]))]
        [i["taskStatus"].append({"status": j["taskStatus"], "groupID": j["groupID"]}) for i in tasks for j in obj.tasks if j["policyID"] == i["policyID"]]
        return tasks


class XRSForensicsSerializer(serializers.Serializer):
    """
    TODO: add *args **kargs with views_func
    """
    timestamp = serializers.IntegerField(min_value=1514736000, max_value=4070880000, required=True)
    user = serializers.CharField(max_length=45, min_length=7, required=True)
    pageSize = serializers.IntegerField(min_value=1, max_value=200, default=20)


class EASSerializer(serializers.Serializer):
    startTimestamp = serializers.IntegerField(min_value=1514736000, max_value=4070880000, required=True)
    endTimestamp = serializers.IntegerField(min_value=1514736000, max_value=4070880000, required=True)
    pageSize = serializers.IntegerField(min_value=1, max_value=500, default=5, write_only=True)
    page = serializers.IntegerField(min_value=1, max_value=200, default=1, write_only=True)
    top = serializers.IntegerField(min_value=1, max_value=500, required=False)
    filter = serializers.ListField(allow_empty=False, write_only=True)
    deviceID = serializers.CharField(required=True, write_only=True)
    must_list = serializers.ListField(read_only=True, required=False)
    from_size = serializers.IntegerField(required=False)
    size = serializers.IntegerField(read_only=True, required=False)

    def validate(self, attrs):
        if 'top' in attrs:
            attrs['size'] = attrs['top']
            attrs['from_size'] = 0
            del attrs['top']
        else:
            attrs['size'] = attrs['pageSize']
            attrs['from_size'] = (attrs['page'] - 1) * attrs['pageSize']
        attrs['must_list'] = get_filter_query(attrs['deviceID'], attrs['filter'])
        return attrs
