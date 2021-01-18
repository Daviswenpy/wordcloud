# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-02-19 16:20:01
File Name: authentication.py @v2.3
"""
from __future__ import unicode_literals

import base64
import hashlib
import datetime

from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BasicAuthentication

from models import Session


class APIBackendAuthentication(object):

    def authenticate(self, username=None, timestamp=None, passwordHash=None):
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                return None
        except Exception:
            return None

        hash_str = hashlib.sha256(user.username + str(timestamp) + user.userprofile.passwordHash).hexdigest()

        if base64.b64encode(hash_str)[:12] == passwordHash:
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except Exception:
            return None


class ExpiringTokenAuthentication(BasicAuthentication):

    www_authenticate_realm = 'api-Session'

    model = Session

    def authenticate_credentials(self, clientIP, sessionID, request=None):

        cache_user = cache.get(sessionID)
        if cache_user:
            cache.set(sessionID, cache_user, 3600)
            return (cache_user, sessionID)

        try:
            session = self.model.objects.select_related('user').get(sessionID=sessionID, clientIP=clientIP)
        except self.model.DoesNotExist:
            raise AuthenticationFailed(_('Authentication failed.'))

        if not session.user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        time_now = datetime.datetime.now()
        time_start = time_now - datetime.timedelta(minutes=session.sessionTimeout / 60)

        if session.created < time_start:
            session.delete()
            raise AuthenticationFailed(_('Session has expired then delete.'))

        if session:
            self.model.objects.filter(created__lt=time_start).delete()
            # self.model.objects.filter(user=session.user, created__lt=time_start).delete()
            session.created = time_now
            session.save()

        return (session.user, session)

    def authenticate_header(self, request):
        return 'Basic realm="%s" for ITPServer.' % self.www_authenticate_realm
