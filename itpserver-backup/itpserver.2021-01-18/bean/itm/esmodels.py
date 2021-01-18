# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-04-01 14:22:37
File Name: esmodels.py @v1.1
TODO: Use django-elasticsearch-dsl or elasticsearch-django insstead of esmodels
# TODO: deserialization
"""
from django.db import models
from django.utils import six
from django.db.models.base import ModelBase
from django.utils.encoding import force_str, force_text
from django.utils.translation import ugettext_lazy as _

from fields import fields
from elasticsearchorm import *


class Model(six.with_metaclass(ModelBase)):
    _deferred = False

    def __repr__(self):
        try:
            u = six.text_type(self)
        except (UnicodeEncodeError, UnicodeDecodeError):
            u = '[Bad Unicode data]'

        return force_str('<%s: %s>' % (self.__class__.__name__, u))

    def __str__(self):
        if six.PY2 and hasattr(self, '__unicode__'):
            return force_text(self).encode('utf-8')

        return str('%s object' % self.__class__.__name__)

    def __eq__(self, other):
        if not isinstance(other, Model):
            return False

        if self._meta.concrete_model != other._meta.concrete_model:
            return False

        my_pk = self._get_pk_val()

        if my_pk is None:
            return self is other

        return my_pk == other._get_pk_val()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        if self._get_pk_val() is None:
            raise TypeError('Model instances without primary key value are unhashable')
        return hash(self._get_pk_val())

    def _get_pk_val(self, meta=None):
        if not meta:
            meta = self._meta
        return getattr(self, meta.pk.attname)


class ESBaseManager(models.Manager):
    use_in_migrations = False

    @property
    def init_db(self):
        return eval(self.model.__name__ + 'ORM')()

    def get(self, doc_id=None):
        return self.model(self.init_db.get_obj(doc_id=doc_id))

    def all(self):
        return []

    def aggregate(self):
        pass

    def bulk_create(self):
        pass

    def bind(self, field_name, parent):
        # super(ESBaseManager, self).bind(field_name, parent)
        pass

    def create(self, doc_id, row_obj):
        res = self.init_db.create_obj(doc_id=doc_id, row_obj=row_obj)
        return self.get(doc_id=doc_id), res

    def count(self):
        return 0

    def db(self):
        pass

    def db_manager(self):
        pass

    def exists(self, doc_id):
        pass

    def filter(self, filter):
        pass

    def first(self):
        pass

    def from_queryset(self, queryset):
        pass

    def last(self):
        pass

    def order_by(self, order):
        pass

    def raw(self):
        pass

    def values(self):
        pass

    def values_list(self):
        pass


class Dict2Obj(object):

    def __init__(self, dct):
        if isinstance(dct, dict):
            self.__dict__.update(dct)


class Device(Dict2Obj, models.Model):
    deviceID = fields.CharField(max_length=64)
    deviceName = fields.CharField(max_length=32)
    logSources = fields.ListField()
    itmConfigs = fields.DictField()
    is_active = fields.BooleanField(default=True, help_text=_(
        '<div style="color:red">! This field is set to ensure device active. </div>')
    )

    objects = ESBaseManager()

    class Meta:
        ordering = ('deviceID',)
        verbose_name = _('Device')
        verbose_name_plural = _('Devices')

    def save(self, *args, **kwargs):
        return super(Session, self).save(*args, **kwargs)

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.deviceID)

    def __unicode__(self):
        return u'<%s: %s>' % (self.__class__.__name__, self.deviceID)


class Tasks(Dict2Obj, models.Model):
    deviceID = fields.CharField(max_length=64)
    tasks = fields.ListField()

    objects = ESBaseManager()

    class Meta:
        ordering = ('deviceID',)
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.deviceID)

    def __unicode__(self):
        return u'<%s: %s>' % (self.__class__.__name__, self.deviceID)


class Parameter(Dict2Obj, models.Model):
    parameterID = fields.CharField(max_length=64)
    description = fields.DictField()
    description = fields.DictField()
    type_ = fields.CharField()
    values = fields.ListField()
    inputType = fields.IntegerField()
    key = fields.CharField()

    objects = ESBaseManager()

    class Meta:
        ordering = ('parameterID',)
        verbose_name = _('Parameter')
        verbose_name_plural = _('Parameters')

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.parameterID)

    def __unicode__(self):
        return u'<%s: %s>' % (self.__class__.__name__, self.parameterID)

    def get_parameter(self, parameterID):
        return get_parameter(parameterID)

    def get_parameters(self, query=None):
        return get_parameters(query)

    def save_parameter(self, parameterID, parameter):
        return save_parameter(parameterID, parameter)

    def save_parameters(self, parameters):
        return save_parameters(parameters)


class Anomaly(Dict2Obj, models.Model):
    anomalyID = fields.CharField(max_length=64)
    display = fields.BooleanField(default=True, help_text=_(
        '<div style="color:red">! This field is contral display anomaly in anomalies details. </div>')
    )
    description = fields.DictField()
    type_ = fields.IntegerField(help_text=_(
        '<div style="color:red">! This field is set to indicate the log type. </div>')
    )
    description = fields.DictField()
    use_query = fields.BooleanField(default=True)
    parameterUuid = models.ForeignKey(Parameter)
    forensics = fields.DictField()

    objects = ESBaseManager()

    class Meta:
        ordering = ('anomalyID',)
        verbose_name = _('Anomaly')
        verbose_name_plural = _('Anomalies')

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.anomalyID)

    def __unicode__(self):
        return u'<%s: %s>' % (self.__class__.__name__, self.anomalyID)

    def get_anomaly(self, anomalyID):
        return get_anomaly(anomalyID)

    def get_anomalies(self, query=None):
        return get_anomalies(query)


def doc_to_map(docs):
    """
    >>> docs
    [{'_index': 'test', '_type': '_doc', '_id': '1', '_source': {'x': 1}},
    {'_index': 'test', '_type': '_doc', '_id': '2', '_source': {'x': 2}},
    {'_index': 'test', '_type': '_doc', '_id': '3', '_source': {'x': 3}}]
    >>> doc_to_map(docs)
    {'1': {'x': 1}, '2': {'x': 2}, '3': {'x': 3}}
    """
    return {i['_id']: i['_source'] for i in docs}


def get_anomaly(anomalyID):
    anomalyID = anomalyID or "_all"
    if anomalyID == '_all':
        query = {
            "size": 10000,
            "query": {
                "bool": {
                    "must": {
                        "term": {
                            "display": True
                        }
                    }
                }
            }
        }
        return get_anomalies(query)

    es = AnomaliesORM()
    return es.get_obj_or_404(doc_id=anomalyID)


def get_anomalies(query=None):
    es = AnomaliesORM()
    docs = es._search(query)['hits']['hits']
    return doc_to_map(docs)


def get_parameterID(deviceID, parameterID):
    """define parameterID = `deviceID`_`parameterID`, maybe change in next version."""
    return deviceID + '_' + parameterID


def get_parameter(deviceID, parameterID):
    # need deviceid filter
    if parameterID is None:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "type.keyword": {
                                    "value": "user-set"
                                }
                            }
                        }
                    ]
                }
            }
        }
        return get_parameters(deviceID, query)
    es = ParametersORM()
    return es.get_obj_or_404(doc_id=get_parameterID(deviceID, parameterID))


def get_parameters(deviceID, query):
    es = ParametersORM()
    docs = [i for i in es._search(query)['hits']['hits'] if deviceID in i['_id']]
    return doc_to_map(docs)


def save_parameter(parameterID, parameter):
    es = ParametersORM()
    return es.update(doc_id=parameterID, row_obj=parameter)


def save_parameters(parameters):
    for key, value in parameters.items():
        save_parameter(key, value)
    return True


def get_threat(deviceID):
    eas_threat_orm = EASThreatORM()
    return eas_threat_orm.get_obj_or_404(doc_id=deviceID)
