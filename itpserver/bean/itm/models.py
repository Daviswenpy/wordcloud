# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-01-24 17:07:12
File Name: models.py @v2.2
"""
from __future__ import unicode_literals

import os
import hashlib
import binascii
import datetime

from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


__all__ = ['UserProfile', 'Session']


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    passwordHash = models.CharField(max_length=128, help_text=_(
        '<div style="color:red">! This field is set to ensure admin security. '
        'Replace it directly with a new password and save it automatically for sha256 encryption.'
        "Don't repeat by clicking the Save button. </div>"),
    )

    class Meta:
        ordering = ('user',)
        verbose_name = _('User password')
        verbose_name_plural = _('Users password')

    def save(self, *args, **kwargs):
        self.passwordHash = hashlib.sha256(self.passwordHash).hexdigest()
        super(UserProfile, self).save(*args, **kwargs)

    def set_passwordHash(self, raw_password, *args, **kwargs):
        self.passwordHash = hashlib.sha256(raw_password).hexdigest()
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.user)

    def __unicode__(self):
        return u'<%s: %s>' % (self.__class__.__name__, self.user)


class Session(models.Model):
    sessionID = models.CharField(_("SessionID"), max_length=40, primary_key=True, unique=True)
    clientIP = models.CharField(max_length=32)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='auth_session', on_delete=models.CASCADE, verbose_name=_("User"))
    sessionTimeout = models.IntegerField(default=3600)

    class Meta:
        ordering = ('created',)
        verbose_name = _('Session')
        verbose_name_plural = _('Sessions')

    def save(self, *args, **kwargs):
        if not self.sessionID:
            self.sessionID = self.generate_sessionID()
        cache.set(self.sessionID, self.user, self.sessionTimeout)
        return super(Session, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        cache.delete(self.sessionID)
        return super(Session, self).delete(*args, **kwargs)

    def generate_sessionID(self):
        return binascii.hexlify(os.urandom(20)).decode()

    @property
    def get_username(self):
        return self.user.username

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.sessionID)

    def __unicode__(self):
        return u'<%s: %s>' % (self.__class__.__name__, self.sessionID)
