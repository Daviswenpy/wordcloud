# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-02-19 14:55:55
File Name: views003.py @v2.0
SOME NOTE: itpserver up-down load file part
"""
from __future__ import unicode_literals

import os

from django.conf import settings
from django.http import StreamingHttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from utils import get_ip
from viewsfuncs import update_task
from serializers import UploadFileSerializer


__all__ = [
    'upload_file',
    'download_file',
]


@api_view(http_method_names=['POST'])
def upload_file(request):
    serializer = UploadFileSerializer(request.POST, request.FILES)
    serializer.is_valid(raise_exception=True)
    filename, full_filename = serializer.save()
    status = update_task(pk="upload", filename=full_filename, sourceip=get_ip(request))
    data = {"resourceName": filename, "status": int(not status)}
    return Response(data)


@api_view(http_method_names=["GET"])
def download_file(request, filename=None):
    data = {}

    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    if filename:
        filename = os.path.join(settings.DOWNLOAD, filename)
        if os.path.exists(filename):
            response = StreamingHttpResponse(file_iterator(filename))
            response['Content-Type'] = 'application/octet-stream'
            return response
        else:
            data['status'] = 1
    data['download_list'] = os.walk(settings.DOWNLOAD).next()[2]
    return Response(data)


class UploadFileViewSet(APIView):

    def post(self, request):
        serializer = UploadFileSerializer(request.POST, request.FILES)
        serializer.is_valid(raise_exception=True)
        filename, full_filename = serializer.save()
        update_task(pk="upload", filename=full_filename, sourceip=get_ip(request))
        return Response({"resourceName": filename, "status": 0})


class DownloadFileViewSet(APIView):
    """
    TODO: viewset opts
    """

    def get(self, request, filename=None):
        data = {}

        def file_iterator(file_name, chunk_size=512):
            with open(file_name) as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        if filename:
            filename = os.path.join(settings.DOWNLOAD, filename)
            if os.path.exists(filename):
                response = StreamingHttpResponse(file_iterator(filename))
                response['Content-Type'] = 'application/octet-stream'
                return response
            else:
                data['status'] = 1
        data['download_list'] = os.walk(settings.DOWNLOAD).next()[2]
        return Response(data)
