# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-06-23 15:02:04
File Name: config.py @v2.0
"""
import os


__all__ = ['config']


class Params(dict):

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)

    def copy(self, **extra_params):
        p = super(Params, self).copy()
        p.__class__ = Params
        p.update(extra_params)
        return p


class Dict2Obj(object):

    def __init__(self, dct):
        self.__dict__.update(dct)


class ConfigBase(object):

    def __setattr__(self, name, value):
        if hasattr(self, name):
            raise AttributeError("Can't set attribute %r to %s" % (name, self))
        else:
            object.__setattr__(self, name, value)


class Config(ConfigBase):
    """
    ITPService config factory.

    Attributes
    ----------
    USER : str, default ""
        Elasticsearch and kibana username.
    PASSWD : str, default ""
        Elasticsearch and kibana password.
    TIMEOUT : int, default 120
        Elasticsearch connection timeout.
    MAX_AGGS : int, default 50000
        Elasticsearch aggregate max size.
    TOP_SIZA : int, default 5000
        Elasticsearch aggregate top size.
    PRECISION_THRESHOLD : int, default 200
        A threshold of 100 can remain within 5% of the error in the case of a unique value of millions.
    """
    USER = ''
    PASSWD = ''
    TIMEOUT = 120
    pd_old_version = '0.20.3'
    pd_old1_version = '0.23.0'
    MIN_BYTES = 1
    MAX_AGGS = 50000
    TOP_SIZA = MAX_AGGS / 10
    PRECISION_THRESHOLD = MAX_AGGS / 250
    ITM_VERSION = 2.3
    WEIGHTS = [0.333, 0.333, 0.333]
    SESSION_TIMEOUT = 60
    TIME_DEVIATION = 600
    ERS_CONFIG = '/opt/skyguard/itpcompose/zodiac/custom_ers_models/'
    ERS_CONFIG_PWD = 'P@ssw0rders'
    UPLOAD_FILE_EXT = {'zip', 'gz', 'tar'}
    UCSS_MAPPING = "/opt/skyguard/itpcompose/logstash/plugin/ucss_mapping.json"
    MYSQL_BEAT = "/opt/skyguard/mysql-beat/config.json"
    # ZODIAC_URL = "http://172.238.238.245:9447"
    # zodiac in chenyu's host
    ZODIAC_URL = "http://172.30.7.145:9447"
    LEVEL_5 = '(ARS > 7 and MRS > 7 and ERS > 7) or (ARS > 9 or MRS > 9 or ERS > 9)'
    LEVEL_4 = '(ARS > 7 and ERS > 7) or (ARS > 8 or MRS > 8 or ERS > 8)'
    LEVEL_3 = '(ARS > 6 or MRS > 6 or ERS > 6)'
    LEVEL_2 = '(ARS > 5 or MRS > 5 or ERS > 5)'
    ARS_FORENSICS = {
        "network": [
            "ars_network_ssl",
            "ars_network_tcp",
            "ars_network_udp",
            "ars_network_icmp"
        ],
        "protocols": [
            "ars_protocols_http",
            "ars_protocols_domain",
            "ars_protocols_post",
            "ars_protocols_get"
        ]
    }
    DEFAULT_CONFIG = {
        "deviceID": "",
        "deviceName": "",
        "is_active": True,
        "logSources": [],
        "itmConfigs": {
            "ars": {
                "version": 0,
                "blacklist": [{"type": 1, "value": []}, {"type": 2, "value": []}, {"type": 3, "value": []}, {"type": 4, "value": []}, {"type": 5, "value": []}],
                "interval": 7200,
                "subsystems": [],
                "chosenGroups": [],
                "topN": 0
            },
            "mrs": {
                "version": 0,
                "blacklist": [{"type": 1, "value": []}, {"type": 2, "value": []}, {"type": 3, "value": []}, {"type": 4, "value": []}, {"type": 5, "value": []}],
                "interval": 7200,
                "uploadToLab": True,
                "chosenDLPPolicies": [],
                "retrospectiveDays": 7,
                "topN": 0
            },
            "ers": {
                "version": 0,
                "topN": 0,
                "blacklist": [{"type": 1, "value": []}, {"type": 2, "value": []}, {"type": 3, "value": []}, {"type": 4, "value": []}, {"type": 5, "value": []}],
                "interval": 7200,
                "ChosenModels": [],
                "modelParameterMap": []
            }
        }
    }
    es_templete = {
        "index_patterns": ["*"],
        "order": 100,
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "_doc": {}
        }
    }
    threat_level_mapping = {
        4: 1,
        3: 0.8,
        2: 0.6,
        1: 0.4
    }
    # added by wendong,compatible with version 3.3
    if os.path.exists("/opt/skyguard/itpserver/ucss_3.3"):
        UCSS_VERSION = 3.3
    else:
        UCSS_VERSION = 3.8


class ProductionConfig(Config):
    ES_URL = 'http://172.238.238.239:9200/'
    BROKER_URL = 'redis://172.238.238.238:6379/0'
    CACHE_URL = 'redis://172.238.238.238:6379/1'
    USER_SERVICE = 'https://172.238.238.1:5001/'


class DevelopmentConfig(Config):
    ES_URL = 'http://172.22.111.250:9200/'
    BROKER_URL = 'redis://172.22.149.230:6379/0'
    CACHE_URL = 'redis://172.238.238.238:6379/1'
    USER_SERVICE = 'https://172.22.111.247:5001/'


class CIConfig(Config):
    ES_URL = 'http://172.22.118.1:9200/'
    BROKER_URL = 'redis://172.22.118.1:6379/0'
    CACHE_URL = 'redis://172.22.118.99:6379/1'
    USER_SERVICE = 'https://172.22.111.247:5001/'


class TestConfig(Config):
    # ES_URL = 'http://172.22.149.230:9200/'
    # temp test
    # ES_URL = 'http://172.22.111.15:9200/'
    # chengdu es
    ES_URL = 'http://172.30.3.57:9200/'
    # redis below 2,cannot connect
    # BROKER_URL = 'redis://172.22.118.99:6379/0'
    # CACHE_URL = 'redis://172.22.118.99:6379/1'
    BROKER_URL = 'redis://127.0.0.1:6379/0'
    CACHE_URL = 'redis://127.0.0.1:6379/1'
    USER_SERVICE = 'https://172.22.149.230:5001/'


class TestQAConfig(Config):
    ES_URL = 'http://172.22.149.230:9200/'
    BROKER_URL = 'redis://172.22.149.230:6379/0'
    CACHE_URL = 'redis://172.22.118.99:6379/1'
    USER_SERVICE = 'https://172.22.149.230:5001/'


class SelectConfig:

    __instance = None

    def __init__(self):
        # itm_config = os.environ.get('ITM_CONFIG', 'prod')
        # for test  wendong
        itm_config = os.environ.get('ITM_CONFIG', 'test')

        _map = {
            'dev': DevelopmentConfig,
            'ci': CIConfig,
            'test': TestConfig,
            'prod': ProductionConfig,
            'testqa': TestQAConfig
        }
        self.config = _map[itm_config]

    @staticmethod
    def get_config():
        if SelectConfig.__instance:
            return SelectConfig.__instance
        else:
            SelectConfig.__instance = SelectConfig().config
            return SelectConfig.__instance


config = SelectConfig().get_config()
