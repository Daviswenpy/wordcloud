# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-02-19 14:41:57
File Name: views002.py @v2.0
SOME NOTE: itpserver device part
"""
from __future__ import unicode_literals


from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from serializers import DeviceSerializer, DeviceBlacklistSerializer
from viewsfuncs import mysql_beat, update_task, device_iptables_mapping


__all__ = [
    'register',
    'itm_configs',
    'configuration',
    'conf_xrs',
]


@api_view(http_method_names=['POST', 'DELETE'])
def register(request, deviceID):
    use = request.method == 'POST'
    serializer = DeviceSerializer(data=request.data if use else {"is_active": False, "deviceID": deviceID})
    serializer.is_valid(raise_exception=True)
    logSources = serializer.validated_data.get('logSources', None)
    device, _ = serializer.save() # actually, run itm.serializers.DeviceSerializer.create()
    serializer = DeviceSerializer(device)
    logSources = logSources or serializer.data_device['logSources']
    # mysql_beat(use, deviceID, logSources if use else {})  # if testing, disable it
    update_task(deviceID, serializer.data)
    device_iptables_mapping("enable", deviceID, [i['ip'] for i in logSources])
    cache.set(deviceID, serializer.data['is_active'])
    data = {} if use else serializer.data_device
    return Response(data)


def update_device(device):
    deviceID = device['deviceID']
    serializer = DeviceSerializer(data=device)
    serializer.is_valid(raise_exception=True)
    device, res = serializer.save() # same like register
    serializer = DeviceSerializer(device)
    update_task(deviceID, serializer.data)
    return res


@api_view(http_method_names=['POST'])
def itm_configs(request, deviceID):
    device = request.device
    device['itmConfigs'] = request.data
    update_device(device)
    return Response()


@api_view(http_method_names=['GET'])
def configuration(request, deviceID):
    data = request.device
    return Response(data)


@api_view(http_method_names=['GET', 'POST'])
def conf_xrs(request, deviceID, pk, bk=None):
    device = request.device

    if request.method == 'GET':
        data = {}
        if pk == "versions":
            data["version"] = {
                'ars': device['itmConfigs']['ars']['version'],
                'mrs': device['itmConfigs']['mrs']['version'],
                'ers': device['itmConfigs']['ers']['version']
            }
        else:
            if bk:
                data['blacklist'] = device['itmConfigs'][pk]['blacklist']
            else:
                data[pk] = device['itmConfigs'][pk]
        return Response(data)

    if request.method == 'POST' and pk != "versions":
        if bk:
            serializer = DeviceBlacklistSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            device['itmConfigs'][pk].update(serializer.data)
        else:
            # Can not serializer xrs conf
            device['itmConfigs'][pk] = request.data
        update_device(device)
        return Response(device)


class DeviceRegViewSet(APIView):

    def post(self, request, deviceID):
        serializer = DeviceSerializer(request.data)
        serializer.is_valid(raise_exception=True)
        return Response(self.data(serializer, True, deviceID))

    def delete(self, request, deviceID):
        request_data = {"is_active": False, "deviceID": deviceID}
        serializer = DeviceSerializer(request_data)
        return Response(self.data(serializer, False, deviceID))

    def data(self, serializer, use, deviceID):
        logSources = serializer.validated_data.get('logSources', None)
        device, _ = serializer.save()
        serializer = DeviceSerializer(device)
        logSources = logSources or serializer.data_device['logSources']
        mysql_beat(use, deviceID, logSources if use else {})
        update_task(deviceID, serializer.data)
        device_iptables_mapping("enable", deviceID, [i['ip'] for i in logSources])
        cache.set(deviceID, serializer.data['is_active'])
        data = {} if use else serializer.data_device
        return data


class DeviceViewSet(APIView):

    def get(self, request, deviceID):
        return Response(request.device)

    def post(self, request, deviceID, pk):
        device = request.device
        device['itmConfigs'] = request.data
        update_device(device)
        return Response()


class DeviceConfViewSet(APIView):

    def get(self, request, deviceID, pk, bk=None):
        device = request.device
        data = {}
        if pk == "versions":
            data["version"] = {
                'ars': device['itmConfigs']['ars']['version'],
                'mrs': device['itmConfigs']['mrs']['version'],
                'ers': device['itmConfigs']['ers']['version']
            }
        else:
            if bk:
                data['blacklist'] = device['itmConfigs'][pk]['blacklist']
            else:
                data[pk] = device['itmConfigs'][pk]
        return Response(data)

    def post(self, request, deviceID, pk, bk=None):
        device = request.device
        if pk == 'version':
            raise TypeError('Can not change version in this api!')
        if bk:
            serializer = DeviceBlacklistSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            device['itmConfigs'][pk].update(serializer.data)
        else:
            device['itmConfigs'][pk] = request.data
        update_device(device)
        return Response()
