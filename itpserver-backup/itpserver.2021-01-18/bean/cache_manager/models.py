import collections
import json
import logging

import base64
import binascii

import redis
import itertools
from django.db import models
from django.db.models import Q
from django.contrib import admin
from django.utils import timezone
from django.core.cache import cache
from django.utils.html import format_html
from django.contrib.auth.models import User
from datetime import timedelta

from . import settings

logger = logging.getLogger(__name__)


def decode_bytes(value, encoding='utf-8', method='replace'):
    if isinstance(value, bytes):
        return value.decode(encoding, method)
    else:
        return value


class Q_up(Q):

    def deconstruct(self):
        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        if path.startswith('django.db.models.query_utils'):
            path = path.replace('django.db.models.query_utils', 'django.db.models')
        args, kwargs = (), {}
        if len(self.children) == 1 and not isinstance(self.children[0], Q):
            child = self.children[0]
            kwargs = {child[0]: child[1]}
        else:
            args = tuple(self.children)
            if self.connector != self.default:
                kwargs = {'_connector': self.connector}
        if self.negated:
            kwargs['_negated'] = True
        return path, args, kwargs


class Query:
    order_by = tuple()

    def __init__(self, queryset):
        self.queryset = queryset

    def select_related(self, *args, **kwargs):
        assert not args and not kwargs
        return self


class Queryset(models.QuerySet):

    def __init__(self, model, query=None, slice_limit=101):
        self.slice_limit = slice_limit
        self.q = '*'
        self.filters = ()
        self.admin = admin
        self.model = model
        self._meta = model._meta
        self._cache = None
        self._get_cache = None
        self.slice = None
        self._result_cache = None

        # self.ordered = True
        self.query = query or Query(self)

    def count(self):
        return len(self)

    def order_by(self, *args, **kwargs):
        return self

    def filter(self, *filters, **raw_filters):
        self._cache = dict()
        self._get_cache = None
        self.filters = list(filters)
        if raw_filters:
            self.filters.append(Q_up(**raw_filters))

        query = None
        for filter in self.filters:
            path, args, kwargs = filter.deconstruct()

            error = ('%r is not supported yet, please file a bug report on '
                     'https://github.com/WoLpH/redis_admin/issues/') % filter

            # Not sure when args are ever a thing so we don't support it yet
            # assert not args, error

            for key, value in kwargs.items():
                # Can't have multiple filters with redis
                assert not query, error

                key = key.split('__', 1)
                if key[1:]:
                    key, query = key
                else:
                    key, = key
                    query = None

                # Can't search for anything besides key with redis
                assert key == 'key' or 'pk', error

                if query == 'exact' or query is None:
                    query = value
                elif query == 'startswith':
                    query = '%s*' % value
                elif query == 'endswith':
                    query = '*%s' % value
                elif query == 'contains':
                    query = '*%s*' % value
                elif query == 'in':
                    query = value
                else:
                    raise AssertionError(error)

        self.q = query or '*'

        return self

    def __getattr__(self, key):
        message = 'queryset.%s' % key
        print(message)
        raise AttributeError('Unknown attribute %s' % message)

    def _clone(self):
        return self

    def __len__(self):
        if self.filters:
            # Arbitrary number, we don't want to search if not needed
            if not self._cache:
                self[:self.slice_limit]

            return len(self._cache)
        else:
            # return 1000
            return len(cache.keys("*"))

    def get(self, *args, **kwargs):
        if not self._get_cache:
            self._get_cache = next(iter(self.filter(**kwargs)))
        return self._get_cache

    def exists(self):
        if self._cache is None:
            return self.query.has_results(using=self.db)
        return bool(self._result_cache)

    def __iter__(self):
        logger.error('searching %r with query %r', self.model._meta.model_name, self.q)

        if self._cache:
            for value in self._cache.values():
                yield value

            return

        self.slice = index = self.slice or slice(self.slice_limit)
        slice_size = min(index.stop, self.slice_limit)
        # keys_iter = self.slave.scan_iter(self.q, count=slice_size)
        if isinstance(self.q, list):
            keys_iter = self.q
        else:
            keys_iter = cache.keys(self.q)

        keys = itertools.islice(keys_iter, index.start, index.stop, index.step)

        keys = [key.decode() for key in keys]

        now = timezone.now()

        values = collections.OrderedDict()

        for key in keys:
            ttl = cache.ttl(key)
            if ttl > 0:
                expires_at = now + timedelta(seconds=ttl)
            else:
                expires_at = None
            value = self.model.create(key=key, ttl=ttl, expires_at=expires_at, value=cache.get(key))
            values[key] = value

        self._cache = values
        for value in values.values():
            yield value

    def __getitem__(self, index):
        if isinstance(index, int):
            self.index = slice(0, index, 1)
        elif isinstance(index, slice):
            self.index = index
        else:
            raise TypeError('Unsupported index type %r: %r' % (type(index), index))

        return self


class CacheManager(models.Manager):

    def get_queryset(self):
        return Queryset(self.model)


class RedisMeta:
    managed = False

    def get_field(self, name):
        class Field:
            is_relation = False
            auto_created = True

        return Field()

    def __getattr__(self, key):
        message = 'meta.%s' % key
        print(message)
        raise AttributeError('Unknown attribute %s' % message)


class RedisValue(models.Model):

    TYPES = dict()

    value_types = [
        ('User', 'User'),
        ('DeviceID', 'DeviceID'),
        ('SessionID', 'SessionID'),
        ('Bool', 'Bool'),
        ('DataFrame', 'DataFrame'),
        ('String', 'String'),
        ('XRS', 'XRS'),
        ('Unspecified', 'Unspecified'),
    ]
    key_types = [
        ('UserId', 'UserId'),
        ('DeviceID', 'DeviceID'),
        ('SessionID', 'SessionID'),
        ('XRS', 'XRS'),
        ('Unspecified', 'Unspecified'),
    ]

    key = models.CharField(max_length=256, primary_key=True)
    _key_type = models.CharField(max_length=64, choices=key_types, default='Unspecified', help_text="Check and support with list.")
    timeout = models.IntegerField(default=3600, help_text="Default timeout is 3600.")
    _value_type = models.CharField(max_length=64, choices=value_types, default='Unspecified', help_text="Check and support with list.")
    value = models.CharField(max_length=10000, help_text="Raw value with CharField, convert type with value type.")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Expiration time.")
    ttl = models.IntegerField(help_text="Returns the remaining expiration time in seconds.")
    type = models.CharField(max_length=8, default='none')

    objects = CacheManager()

    # idle_since = models.DateTimeField(null=True, blank=True)
    # base64 = models.BooleanField()
    # json = models.BooleanField()

    @classmethod
    def register_type(cls, type):
        def _register_type(class_):
            cls.TYPES[type] = class_
            return class_

        return _register_type

    @classmethod
    def create(cls, type='none', **kwargs):
        class_ = cls.TYPES.get(type, cls)
        return class_(type=type, **kwargs)

    def decode_string(self, value):
        v0 = value
        value = decode_bytes(value) or ''

        v1 = value
        if settings.BASE64_KEY_RE.match(self.key):
            try:
                value = decode_bytes(base64.b64decode(value))
                self.base64 = True
            except binascii.Error:
                self.base64 = False

        v2 = value
        if settings.JSON_KEY_RE.match(self.key):
            try:
                value = settings.JSON_MODULE.loads(value)
                self.json = True
            except json.JSONDecodeError as e:
                print('error %r attempting json on: %r', e, value)
                self.json = False

        return value

    # @property
    # def value(self):
    #     # if self.value_type == 'UserName':
    #     #     print(type(self.raw_value))
    #     # #     return User.objects.get(username=self.raw_value)
    #     # elif self.value_type == 'Bool':
    #     #     print(type(self.raw_value))
    #     # #     return bool(raw_value)
    #     # elif self.value_type == 'DataFrame':
    #     #     print(type(self.raw_value))
    #     # #     pass
    #     return self.raw_value

    @property
    def key_type(self):
        if isinstance(self.key, tuple):
            return "XRS"
        elif isinstance(self.key, (str, unicode)):
            if len(self.key) == 40:
                return "SessionID"
            elif isinstance(cache.get(self.key), bool):
                # add related search
                return "DeviceID"
            else:
                return "Unspecified({})".format(type(self.key))
        else:
            return "Unspecified({})".format(type(self.key))

    @property
    def value_type(self):
        if isinstance(self.key, tuple):
            return "DataFrame"
        elif isinstance(self.key, (str, unicode)):
            if len(self.key) == 40:
                return "UserName"
            elif isinstance(cache.get(self.key), bool):
                # add related search
                return "Bool"
            else:
                return "Unspecified({})".format(type(self.value))
        else:
            return "Unspecified({})".format(type(self.value))

    def get_cropped_value(self, crop_size):
        value = str(self.value)

        if len(value) >= crop_size:
            crop_half = crop_size // 2
            value = value[:crop_half] + '...' + value[-crop_half:]
        return value

    def fetch_value(self, client):
        '''
        Fetch the value. Note that if a pipe is passed as `client` the
        result will be in the `pipe.execute()` instead
        '''
        raise NotImplementedError('fetch_value is not implemented for %r'
                                  % self.type)

    def delete(self, using=None, keep_parents=False):
        return cache.delete(self.key)

    def convert_type(self):
        # todo
        # convert key with _key_type
        # convert value with _value
        # convert _value with _value_type
        pass

    def save(self, using=None, keep_parents=False):
        self.convert_type()
        if self._value_type == 'Bool':
            if self.value in ['True', 'true', '1']:
                return cache.set(self.key, True, self.timeout)
            elif self.value in ['False', 'false', '0']:
                return cache.set(self.key, False, self.timeout)
        return cache.set(self.key, self.value, self.timeout)

    def touch(self, using=None, keep_parents=False):
        if cache.ttl(self.key) >= self.timeout:
            # print("The default timeout is too small, touch unsuccessfully.")
            return False
        else:
            return cache.touch(self.key, self.timeout)

    def __getattr__(self, key):
        message = '%s.%s' % (self.__class__.__name__, key)
        print(message)
        raise AttributeError('Unknown attribute %s' % message)

    def __repr__(self):
        return '<{class_name}[{key}] {value}>'.format(
            class_name=self.__class__.__name__,
            key=self.key,
            value=self.get_cropped_value(40),
        )

    def __str__(self):
        return '<%s: %s  %s: %s>' % (self.key_type, self.key, self.value_type, self.value)

    def __unicode__(self):
        return u'<%s: %s  %s: %s>' % (self.key_type, self.key, self.value_type, self.value)

    class Meta(RedisMeta):
        abstract = True


@RedisValue.register_type('string')
class RedisString(RedisValue):

    def fetch_value(self, client):
        return cache.get(self.key)

    @property
    def value(self):
        return self.decode_string(self.value)


@RedisValue.register_type('list')
class RedisList(RedisValue):

    def fetch_value(self, client):
        return client.lrange(self.key, 0, -1)

    @property
    def value(self):
        value = self.value
        if value:
            value = [self.decode_string(v) for v in value]

        return value


@RedisValue.register_type('set')
class RedisSet(RedisList):

    def fetch_value(self, client):
        return client.smembers(self.key)

    @property
    def value(self):
        return set(RedisList.value(self))


@RedisValue.register_type('hash')
class RedisHash(RedisValue):

    def fetch_value(self, client):
        return client.hgetall(self.key)

    @property
    def value(self):
        value = self.value
        if value:
            value = {decode_bytes(k): self.decode_string(v)
                     for k, v in value.items()}

        return value


@RedisValue.register_type('zset')
class RedisZSet(RedisHash):

    def fetch_value(self, client):
        return client.zrangebyscore(self.key, '-inf', '+inf', withscores=True)

    @property
    def value(self):
        value = self.value
        if value:
            value = collections.OrderedDict(
                (decode_bytes(k), self.decode_string(v))
                for k, v in value)

        return value


server_models = dict()

for name, server in settings.SERVERS.items():
    class Meta(RedisMeta):
        pass

    # Overwrite meta variables if available
    if 'meta' in server:
        for key, value in server['meta'].items():
            setattr(Meta, key, value)

    server_models[name] = type(name.capitalize(), (RedisValue,), {
        '__module__': __name__,
        'Meta': Meta,
    })
    globals()[name.capitalize()] = server_models[name]
