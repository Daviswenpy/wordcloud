# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-03-19 18:11:07
File Name: viewsfuncs006.py @v2.1
"""
import json
import datetime,time,copy
from functools import partial
from collections import defaultdict

from itm import logger
from config import config
from views004 import merge_models
from exceptions import APIDataNotFound
# from code_profiler import func_line_time
from esmodels import get_anomaly, get_threat
from utils import simple_datetime, gengerate_doc_id, dict_merge
from elasticsearchorm import AnomaliesScoresORM, ElasticsearchORM, auto_client


__all__ = [
    'get_forensics',
]


def _refun(se):
    """
    Reverse se.
    """
    se.reverse()
    return None


def get_doc_id(start, deviceID, anomalyID, user):
    return gengerate_doc_id(start + deviceID + anomalyID + user)


def get_logs_with_ids(docs):
    esorm = ElasticsearchORM()
    logs = esorm.mget({"docs": docs})["docs"]
    return [i.get('_source', {}) for i in logs]


def get_logs_with_query(index, query, from_, size):
    esorm = ElasticsearchORM(index)
    res = esorm.search(query=query, from_=from_, size=size)
    return [i.get('_source', {}) for i in res['hits']['hits']], res['hits']['total']

def remove_buckets(rawData):
    for key in rawData.keys():
        if isinstance(rawData[key], dict):
            if rawData[key].has_key("buckets"):
                rawData[key] = rawData[key]["buckets"]
                for data in rawData[key]:
                    remove_buckets(data)

# @func_line_time()
def get_anomaly_forensics(deviceID=None, ID=None, temp=None, xrs=None, user=None, pageSize=None, timestamp=None):
    try:
        data = {}
        es_orm = AnomaliesScoresORM()
        start = simple_datetime(timestamp, str, True)
        doc_id = get_doc_id(start, deviceID, ID, user)
        res = es_orm.get_obj_or_404(doc_id=doc_id)

        if res.get("scores", 1) != 0:
            if temp is None:
                if xrs == 'eas':
                    temp = get_anomaly(ID)
                elif xrs == 'ers':
                    temp = get_ers_models(deviceID)['params'][ID]
                else:
                    raise Exception

            data[ID] = temp
            data[ID]['scores'] = res.get('scores', -1)
            from_ = (pageSize - 1) * 5

            if res['details'].get('logs'):
                size = pageSize * 5
                log_size = len(res["details"]["logs"])
                ids = res['details']['logs'][from_:size]
                res['details']['logs'] = get_logs_with_ids(ids)
                res['details']['size'] = log_size
            else:
                index = res['details'].pop('index', None)
                index_list = res['details'].pop('index_list', None)
                query = res['details'].pop('query', {})
                index = index_list or index

            if index and query != {}:
                size = 5
                res['details']['logs'], res['details']['size'] = get_logs_with_query(index, query, from_, size)

                if 'display' in temp and xrs == 'eas' and 'agg_query' in temp['forensics']['graphs']['template'][0]: # if anomalyid has no graphs,exception,短路
                    aggs_querys = {}
                    for graph in temp['forensics']['graphs']['template']:
                        aggs_querys.update(graph['agg_query'])

                    _query = json.loads(query)
                    _query['aggs'] = aggs_querys

                    graphs_values = ElasticsearchORM(index).search(query=_query)['aggregations']
                    remove_buckets(graphs_values)
                    res['graphs'] = graphs_values

                if ID in ["23787c99-4b94-4514-a38e-f753b8f47e57", "c91dd8fa-af7f-11e9-a5a5-144f8a006a90"]:
                    for i in res['details']['logs']:
                        if "geoip" in i:
                            if i['geoip']['country_name'] in ["Taiwan", "Hong Kong", "Macao"]:
                                i['geoip']['country_name'] = "China " + i['geoip']['country_name']

            dct = data[ID]['forensics']
            data[ID]['forensics'] = dict_merge(dct, res)


        # added by wendong, compatible with version 3.3
        if config.UCSS_VERSION == 3.3:
            for k,v in data.items():
                graphs = v["forensics"]["graphs"]
            _graphs = copy.deepcopy(graphs)
            for i in _graphs["template"]:
                if i["type"] == 1:
                    graphs["template"].remove(i)
                    continue
                elif i["type"] == 2:
                    graphs["histCnt"] = get_histCnt(graphs["histCnt"],timestamp)
                elif i["type"] == 3:
                    graphs["timeseries"] = [item["key_as_string"] for item in graphs["timeseries"]]

        return data

    except APIDataNotFound:
        logger.debug("{}ScoresORM 404_id:{} start:{} deviceID ID:{} userId".format(xrs.upper(), doc_id, timestamp, ID))
        return {}

    except:
        logger.exception("{} {} {} {} {}\n".format(timestamp, deviceID, ID, user, pageSize))
        return {}


get_param_forensics = get_anomaly_forensics


# added by wendong, compatible with version 3.3
def get_histCnt(histCnt,timestamp):

    def get_formattime(timestamp):
        timeArray = time.localtime(timestamp)
        return time.strftime("%Y-%m-%d", timeArray)

    # fast way, histCnt=[]
    if not histCnt:
        return [0]*7
    else:
        datetime_lst = [get_formattime(timestamp - i * 86400) for i in range(6, -1, -1)]
        histCnt_date_lst = [item["key_as_string"] for item in histCnt]
        match_pos = [datetime_lst.index(j) for i in histCnt_date_lst for j in datetime_lst if i == j]
        histCnt_temp = [0] * 7
        for index in range(len(histCnt)):
            histCnt_temp[match_pos[index]] = histCnt[index]["doc_count"]
        return histCnt_temp


def get_ers_models(deviceID=None):
    ers_models = merge_models(deviceID, use_all=True)
    ers_models['models'] = {}
    ers_models['params'] = {}

    for model in ers_models['ersModels']:
        modelID = model.pop('modelID')
        params = model.pop('modelParameters')
        ers_models['models'][modelID] = model
        ers_models['models'][modelID]["modelParameters"] = []

        for param in params:
            paramID = param.pop("paramID")
            ers_models["params"][paramID] = param
            ers_models['models'][modelID]["modelParameters"].append(paramID)

    return ers_models


def get_model_forensics(deviceID, ID, **kwargs):
    if kwargs['xrs'] == 'ars':
        data = get_ars_forensics(None, deviceID, ID, **kwargs)
    else:
        ers_models = get_ers_models(deviceID)
        data = defaultdict(dict)

        if ID:
            data[ID] = ers_models['models'][ID]
        else:
            data.update(ers_models['models'])
        for modelID, model in data.items():
            for anomalyID in model['modelParameters']:
                temp = ers_models['params'][anomalyID]
                data[modelID].update(get_anomaly_forensics(deviceID=deviceID, ID=anomalyID, temp=temp, **kwargs))
    return data


def get_anomalyGroup_forensics(deviceID, ID, **kwargs):
    data = {ID: {}}
    anomalyGroup = get_threat(deviceID)['anomalyGroups'][ID]
    anomalies_list = anomalyGroup.pop('anomalies')
    data[ID].update(anomalyGroup)

    for anomalyID in anomalies_list:
        temp = get_anomaly(anomalyID)
        data[ID].update(get_anomaly_forensics(deviceID=deviceID, ID=anomalyID, temp=temp, **kwargs))

    return data


def get_threat_forensics(deviceID, ID, **kwargs):
    data = {ID: {}}
    threat = get_threat(deviceID)['threats'][ID]
    anomalyGroups_list = threat.pop('anomalyGroups')
    data[ID].update(threat)

    for anomalyGroupID in anomalyGroups_list:
        data[ID].update(get_anomalyGroup_forensics(deviceID=deviceID, ID=anomalyGroupID, **kwargs))

    return data


def merge_topn(scores_dict, deviceID, pk, timestamp, size, histdays=1, at_least=None):
    feature_must = {
        "http": [{"terms": {"channelType": [1, 2]}}],
        "domain": [{"terms": {"channelType": [1, 2]}}],
        "post": [{"terms": {"method.keyword": ["POST", "PUT", "PATCH", "DELETE"]}}],
        "get": [{"terms": {"method.keyword": ["GET", "HEAD", "OPTIONS"]}}],
        "ssl": [{"term": {"service.keyword": "ssl"}}],
        "udp": [{"term": {"proto.keyword": "udp"}}],
        "tcp": [{"term": {"proto.keyword": "tcp"}}],
        "icmp": [{"term": {"proto.keyword": "icmp"}}]
    }
    if pk == 'network':
        es = auto_client(pk, histdays + 1, simple_datetime(timestamp, datetime.datetime).date())
        term_field = 'resp_h'
        sum_field = 'orig_ip_bytes'
    else:
        es = auto_client('swg', histdays + 1, simple_datetime(timestamp, datetime.datetime).date())
        term_field = 'uriDomain.keyword'
        sum_field = 'sendBytes'

    _query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "deviceID.keyword": deviceID
                        }
                    },
                    {
                        "term": {
                            "userId.keyword": scores_dict['userId']
                        }
                    }
                ] + feature_must[scores_dict['feature']],
                "filter": [
                    {
                        "range": {
                            "@timestamp": {
                                "gte": (timestamp - histdays * 3600 * 24) * 1000,
                                "lt": timestamp * 1000
                            }
                        }
                    }
                ]
            }
        },
        "size": 0,
        "aggs": {
            "tarinfo": {
                "terms": {
                    "field": term_field,
                    "size": size
                },
                "aggs": {
                    "bytes_sum": {
                        "sum": {
                            "field": sum_field
                        }
                    }
                }
            }
        }
    }

    scores_dict['tarinfo'] = es.aggregate(query=_query)['aggregations']['tarinfo']['buckets']
    return


def get_ars_forensics(pk, deviceID, ID, timestamp, user, pageSize, **kwargs):
    start = simple_datetime(timestamp, str, True)
    size = pageSize

    if pk:
        ids = [{'_id': get_doc_id(start, deviceID, i, user), '_index': 'ars_scores', '_type': '_doc'} for i in config.ARS_FORENSICS[pk]]
        res = get_logs_with_ids(ids)
        for scores_dict in res:
            if scores_dict:
                merge_topn(scores_dict, deviceID, pk, timestamp, size)
        data = {pk: res}

    else:
        data = {
            "ars": {
                "network": get_network_forensics(deviceID, ID, timestamp, user, pageSize, **kwargs)['network'],
                "protocols": get_protocols_forensics(deviceID, ID, timestamp, user, pageSize, **kwargs)['protocols']
            }
        }

    return data


get_network_forensics = partial(get_ars_forensics, 'network')
get_protocols_forensics = partial(get_ars_forensics, 'protocols')


def get_forensics(pk, **kwargs):
    data = globals().get('get_' + pk + '_forensics')(**kwargs)
    return data
