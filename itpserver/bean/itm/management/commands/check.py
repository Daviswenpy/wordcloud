# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-12-16 14:14:30
File Name: check.py @v1.0
"""
import os
import copy
import json
import hashlib
import pandas as pd

from elasticsearch.helpers import scan
from elasticsearch import Elasticsearch

from django.core.management.base import BaseCommand, CommandError


itm_config = os.environ.get('ITM_CONFIG', 'prod')

if itm_config != 'prod':
    es_url = 'http://172.22.149.230:9200/'
else:
    es_url = 'http://172.238.238.239:9200/'

deviceID = '6a6887d4-b195-7ceb-f1d3-4d66eaf164a9'
time_range = "now-7d"


class AutoVivification(dict):
    """
    Implementation of perl's autovivification feature.
    """

    def __missing__(self, key):
        """Auto dict"""
        value = self[key] = type(self)()
        return value


class ElasticSearchClient(object):

    @staticmethod
    def get_es_servers():
        es_client = Elasticsearch(es_url, timeout=10)
        return es_client


class ESORM(object):

    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "deviceID.keyword": {
                                "value": deviceID
                            }
                        }
                    },
                    {
                        "range": {
                            "timestamp": {
                                "gte": time_range
                            }
                        }
                    }
                ],
                "must_not": [
                    {
                        "term": {
                            "scores": {
                                "value": 0
                            }
                        }
                    }
                ]
            }
        }
    }

    def __init__(self, index=None, doc_type='_doc', mapping=None, settings=None):
        self.index = index
        self.es_client = ElasticSearchClient.get_es_servers()
        self.doc_type = doc_type

    def count(self, query):
        return self.es_client.count(index=self.index, doc_type=self.doc_type, body=query)

    def get_obj(self, doc_id):
        """
        Get a typed JSON document from the index based on `doc_id`.
        """
        obj = self.es_client.get(index=self.index, doc_type=self.doc_type, refresh=True, id=doc_id)
        return obj["_source"]

    def mget(self, body, **kwargs):
        """
        Get multiple documents based on an index, type (optional) and ids, ignore ids that do not exist.
        """
        es_result = self.es_client.mget(index=self.index, doc_type=self.doc_type, body=body, refresh=True, **kwargs)
        return es_result

    def _search(self, query={"size": 10000}, **kwargs):
        res = self.es_client.search(index=self.index, body=query, **kwargs)
        return res

    def _scan(self, query, **kwargs):
        return scan(client=self.es_client, index=self.index, query=query, **kwargs)

    @classmethod
    def get_count(cls, index, query):
        cls = cls(index)
        return cls.count(query)

    @classmethod
    def get_models(cls):
        cls = cls('ers_models')
        return cls.get_obj('ers_models')

    @classmethod
    def get_anomalies(cls):
        cls = cls('anomalies')
        return cls._search()['hits']['hits']

    @classmethod
    def get_model_scores(cls, modelID):
        cls = cls('ers_results')
        query = copy.deepcopy(cls.query)
        if modelID:
            query['query']['bool']['must'] += [{"terms": {"modelID.keyword": [modelID]}}]
        return cls._scan(query=query)

    @classmethod
    def get_node_scores(cls, deviceID, nodeID):
        cls = cls('anomalies_scores')
        query = copy.deepcopy(cls.query)
        if nodeID:
            query['query']['bool']['must'] += [{"terms": {"anomalyID.keyword": [nodeID]}}]
        return cls._scan(query=query)

    @classmethod
    def get_node_count(cls):
        cls = cls('anomalies_scores')
        query = copy.deepcopy(cls.query)
        query['aggs'] = {
            "date_count": {
                "terms": {
                    "field": "timestamp",
                    "size": 10000
                },
                "aggs": {
                    "anomaly_count": {
                        "terms": {
                            "field": "anomalyID.keyword",
                            "size": 100000
                        }
                    }
                }
            }
        }
        query['size'] = 0
        return cls._search(query=query)

    @classmethod
    def init(cls):
        cls.query['bool']['must'].pop(1)
        cls.query['bool']['must'] += {}


def json_print(data, **kwargs):
    print(json.dumps(data, sort_keys=True, indent=4, separators=(', ', ': ')))


def json_format(data, **kwargs):
    return json.dumps(data, sort_keys=True, indent=4, separators=(', ', ': '))


def gengerate_doc_id(selected_str):
    doc_id = hashlib.md5(selected_str.encode("utf-8")).hexdigest()
    return doc_id


def get_doc_id(start, deviceID, anomalyID, user):
    return gengerate_doc_id(start + deviceID + anomalyID + user)


def get_model_map(modelID):
    data = AutoVivification()
    ers_models = ESORM.get_models()
    ers_model_scores = ESORM.get_model_scores(modelID)

    # check modelID in next version
    # for model in ers_models['ersModels']:
    #     modelID = model['modelID']

    for sc in ers_model_scores:
        sd = sc['_source']
        data[sd['modelID']][sd['timestamp']][sd['userId']] = sd['scores']

    return data


def get_node_map(nodeID):
    data = AutoVivification()
    ers_node_scores = ESORM.get_node_scores(nodeID)
    anomalies = ESORM.get_anomalies()
    anomalies_ids = {i['_id']: i['_source'].get('display') for i in anomalies}

    for sc in ers_node_scores:
        sd = sc['_source']
        data[sd['anomalyID']][sd['timestamp']][sd['userId']]['scores'] = sd['scores']
        data[sd['anomalyID']][sd['timestamp']][sd['userId']]['_id'] = sc['_id']
        data[sd['anomalyID']][sd['timestamp']][sd['userId']]['details']['index'] = sd['details']['index']
        data[sd['anomalyID']][sd['timestamp']][sd['userId']]['details']['query'] = sd['details']['query']
        query = json.loads(sd['details']['query'])
        body = {'query': query['query']}
        try:
            data[sd['anomalyID']][sd['timestamp']][sd['userId']]['doc_count'] = ESORM.get_count(sd['details']['index'], body)['count']
        except:
            data[sd['anomalyID']][sd['timestamp']][sd['userId']]['doc_count'] = None
            json_print(body)

        if sd['anomalyID'] in anomalies_ids:
            data[sd['anomalyID']]['in_anomalies'] = True
            data[sd['anomalyID']]['display'] = anomalies_ids[sd['anomalyID']]
    return data


class Command(BaseCommand):
    help = 'Check model and node data.'

    def add_arguments(self, parser):
        parser.add_argument('-modelID', nargs='+', type=str)
        parser.add_argument('-nodeID', nargs='+', type=str)
        parser.add_argument('-time', nargs='+', type=str)
        parser.add_argument('-userId', nargs='+', type=str)
        parser.add_argument('-gt', type=str)
        parser.add_argument('-lt', type=str)
        parser.add_argument('-gte', type=str)
        parser.add_argument('-lte', type=str)
        parser.add_argument('-size', type=str)
        parser.add_argument('-must', type=str)
        parser.add_argument('-query', type=str)
        parser.add_argument('-aggs', type=str)
        parser.add_argument('-exists', type=str)
        parser.add_argument('-filter', type=str)
        parser.add_argument('-should', type=str)
        parser.add_argument('-must_not', type=str)
        parser.add_argument('--count', action='store_true', help='Count model and node data.')

    def handle(self, *args, **options):
        print(options)
        modelIDs = options['modelID'] or []
        nodeIDs = options['nodeID'] or []
        times = options['time']
        userIds = options['userId']

        if options['count']:
            data = ESORM.get_node_count()
            self.stdout.write(json_format(data))

        for modelID in modelIDs:
            data = get_model_map(modelID)
            self.stdout.write(self.style.SUCCESS('Successfully get model {} {} {} data.'.format(modelID, times, userIds)))
            if times:
                for time in times:
                    if userIds:
                        for userId in userIds:
                            self.stdout.write(json_format({time: {userId: data[modelID][time][userId]}}))
                    else:
                        self.stdout.write(json_format({time: data[modelID][time]}))
            else:
                self.stdout.write(json_format(data))

        for nodeID in nodeIDs:
            data = get_node_map(nodeID)
            self.stdout.write(self.style.SUCCESS('Successfully get node "%s" data.' % nodeID))
            if times:
                for time in times:
                    if userIds:
                        for userId in userIds:
                            self.stdout.write(json_format({time: {userId: data[nodeID][time][userId]}}))
                    else:
                        self.stdout.write(json_format({time: data[nodeID][time]}))
            else:
                self.stdout.write(json_format(data))


if __name__ == "__main__":
    pass
    # nodeID = "d75734ca-dde9-11e9-88d6-8c1645a0051c"
    # modelID = "340a4342-b85f-40c4-ab23-8d87ad296f84"
    # # model_map = get_model_map(modelID)
    # node_map = get_node_map(nodeID)
    # json_print(node_map)
    # # json_print(model_map)
    # Usages:
    # python manage.py check --count
    # python manage.py check -nodeID d75734ca-dde9-11e9-88d6-8c1645a0051c -time 2019-12-17T16:00:00+0800 2019-12-17T14:00:00+0800 -userId 172.21.21.117 172.21.20.115
    # python manage.py check -modelID 340a4342-b85f-40c4-ab23-8d87ad296f84 -time 2019-12-17T16:00:00+0800 -userId ecb54ab4-3878-ab49-a34b-78376217b8a8 172.22.83.93
