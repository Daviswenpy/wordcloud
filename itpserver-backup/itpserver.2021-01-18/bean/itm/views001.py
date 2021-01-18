# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-02-19 14:35:44
File Name: views001.py @v2.0
SOME NOTE: itpserver auth part
"""
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from utils import get_ip
from models import Session
from serializers import MultiSessionSerializer


__all__ = [
    'check_in',
    'login_out',
]


@api_view(http_method_names=['POST'])
@permission_classes((AllowAny,))
def check_in(request):
    request.data['clientIP'] = get_ip(request)
    serializer = MultiSessionSerializer.get_serializer_class(request.method)(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer = serializer.create()
    return Response(serializer.data)


@api_view(http_method_names=['GET', 'DELETE'])
def login_out(request, sessionID):
    session = get_object_or_404(Session, sessionID=sessionID)
    serializer = MultiSessionSerializer.get_serializer_class(request.method)(session)
    return Response(serializer.data)


class LoginViewSet(APIView):

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_classes_map = {}
        serializer_class = serializer_classes_map[self.request.method]
        return serializer_class(*args, **kwargs)

    def post(self, request):
        request.data['clientIP'] = get_ip(request)
        serializer = MultiSessionSerializer.get_serializer_class(request.method)(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer = serializer.create()
        return Response(serializer.data)

    def get(self, request, sessionID, format=None):
        session = get_object_or_404(Session, sessionID=sessionID)
        serializer = MultiSessionSerializer.get_serializer_class(request.method)(session)
        return Response(serializer.data)

    def delete(self, request, sessionID, format=None):
        session = get_object_or_404(Session, sessionID=sessionID)
        serializer = MultiSessionSerializer.get_serializer_class(request.method)(session)
        return Response(serializer.data)
