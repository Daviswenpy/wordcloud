# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-02-19 15:32:29
File Name: views006.py @v2.1
SOME NOTE: itpserver forensics part
"""
from __future__ import unicode_literals

from numpy import sum
from pandas import date_range
from collections import defaultdict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from config import config
from viewsfuncs006 import *
from esmodels import get_anomaly
from elasticsearchorm import AnomaliesScoresORM
from utils import dict_merge, simple_datetime
from serializers import XRSForensicsSerializer, EASSerializer


__all__ = [
    'xrs_forensics',
    'eas_report',
    'anomaliesSummary',
]


@api_view(http_method_names=['POST'])
def xrs_forensics(request, deviceID, xrs, pk='model', ID=None):
    """
    Parameters
    ----------
    xrs : str
        ers
        eas
        ars

    pk : str or None
        model
        param
        threat
        anomalyGroup
        anomaly
        network
        protocols
    """
    kwargs_f = locals()
    del kwargs_f['request']
    serializer = XRSForensicsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    kwargs = serializer.data
    kwargs.update(kwargs_f)
    data = get_forensics(**kwargs)
    return Response(data)


def get_datetime_list(esorm, deviceID, must_not_list, must_list, startTimestamp, endTimestamp):
    filter_list = [{"range": {"timestamp": {"gte": startTimestamp * 1000, "lte": endTimestamp * 1000}}}]
    max_t = int(esorm.field_aggs("max", "timestamp", deviceID, filter_list, must_not_list, must_list) / 1000)
    d1 = simple_datetime(startTimestamp, str, True)
    d2 = simple_datetime(endTimestamp, str, True)
    d3 = simple_datetime(max_t, str, True)
    datetime_list = [i.replace(" ", "T") for i in date_range(d1, d2, normalize=True).astype(str).values.tolist()[1:]]
    datetime_list[-1] = d3
    return datetime_list


@api_view(http_method_names=['POST'])
def anomaliesSummary(request, deviceID, anomalyID=None):
    data = defaultdict(list)

    data_pre = request.data
    data_pre['deviceID'] = deviceID

    serializer = EASSerializer(data=data_pre)
    serializer.is_valid(raise_exception=True)
    kwargs = serializer.data

    from_size = kwargs.pop('from_size')
    size = kwargs.pop('size')
    must_list = kwargs.pop('must_list')
    must_not_list = [{"terms": {"scores": [0]}}]
    esorm = AnomaliesScoresORM()
    datetime_list = get_datetime_list(esorm, deviceID, must_not_list, must_list, **kwargs)
    if anomalyID:
        must_list += [{"term": {"anomalyID.keyword": anomalyID}}]
    else:
        anomalyID = "_all"

    anomalies = get_anomaly(anomalyID)

    must_display = [{"terms": {"anomalyID.keyword": list(anomalies.keys())}}] if anomalyID == "_all" else []

    query = {
        "size": size,
        "_source": ["userId", "username", "timestamp", "scores", "summary", "anomalyID"],
        "from": from_size,
        "sort": [{"timestamp": {"order": "desc"}}, {"scores": {"order": "desc"}}],
        "query": {
            "bool": {
                "must": must_list + must_display,
                "filter": [{"terms": {"timestamp": datetime_list}}, {"term": {"deviceID.keyword": deviceID}}],
                "must_not": must_not_list
            }
        }
    }
    res = esorm.search(False, query=query)
    docs = [i['_source'] for i in res['hits']['hits']]

    if anomalyID == "_all":
        for i in anomalies:
            anomaly = anomalies[i]
            anomaly['summary'] = anomaly['forensics']['summary']
            del anomaly['forensics']
    else:
        anomaly = anomalies
        anomaly['summary'] = anomaly['forensics']['summary']
        del anomaly['forensics']

    for doc in docs:
        anomaly = anomalies[doc["anomalyID"]] if anomalyID == "_all" else anomalies
        data[anomalyID].append(dict_merge(anomaly, doc, True))

    data["hits"] = res["hits"]["total"]
    return Response(data)


@api_view(http_method_names=['POST'])
def eas_report(request, deviceID, paramID=None):
    data = defaultdict(dict)

    data_pre = request.data
    data_pre['deviceID'] = deviceID

    serializer = EASSerializer(data=data_pre)
    serializer.is_valid(raise_exception=True)
    kwargs = serializer.data

    startTimestamp = kwargs['startTimestamp']
    endTimestamp = kwargs['endTimestamp']

    size = kwargs.pop('size')
    from_size = kwargs.pop('from_size')
    must_list = kwargs.pop('must_list')

    must_not_list = [{"term": {"scores": 0}}]

    if paramID:
        must_list += [{"term": {"anomalyID.keyword": paramID}}]
        anomaly = get_anomaly(paramID)
        data[paramID]['name'] = anomaly['name']
    else:
        paramID = "_all"
        anomalies = get_anomaly(paramID)
        must_list += [{"terms": {"anomalyID.keyword": list(anomalies.keys())}}]
        data[paramID]['name'] = {"en": "All Anomaly", "zh": "全部异常"}

    esorm = AnomaliesScoresORM()

    datetime_list = get_datetime_list(esorm, deviceID, must_not_list, must_list, **kwargs)

    min_bound_date = simple_datetime(startTimestamp, str, True)[:10]
    max_bound_date = simple_datetime(endTimestamp - 3600 * 24, str, True)[:10]

    demo = {
        "hits": 0,
        "top": {
            "abnormalHits": [],
            "abnormalScores": []
        },
        "histogram": {
            "abnormalHits": []
        },
    }

    data[paramID].update(demo)

    query = {
        "size": size,
        "from": from_size,
        "_source": ["username", "scores"],
        "sort": [
            {"scores": {"order": "desc"}}
        ],
        "query": {
            "bool": {
                "must": must_list,
                "filter": [
                    {"terms": {"timestamp": datetime_list}},
                    {"term": {"deviceID.keyword": deviceID}}
                ],
                "must_not": must_not_list
            }
        },
        "aggs": {
            "count_anomaly": {
                "terms": {
                    "field": "anomalyID.keyword",
                    "size": config.MAX_AGGS
                },
                "aggs": {
                    "histinfo": {
                        "date_histogram": {
                            "field": "timestamp",
                            "interval": "day",
                            "extended_bounds": {
                                "min": min_bound_date,
                                "max": max_bound_date
                            },
                            "min_doc_count": 0,
                            "format": "yyyy-MM-dd"
                        },
                        "aggs": {
                            "clone_count": {
                                "cumulative_sum": {
                                    "buckets_path": "_count"
                                }
                            }
                        }
                    }
                }
            },
            "top_hits": {
                "terms": {
                    "field": "username.keyword",
                    "size": config.TOP_SIZA,
                    "show_term_doc_count_error": True
                }
            },
            "top_scores": {
                "terms": {
                    "field": "username.keyword",
                    "size": config.TOP_SIZA,
                    "show_term_doc_count_error": True,
                    "order": [
                        {"max_scores": "desc"}
                    ]
                },
                "aggs": {
                    "max_scores": {
                        "max": {
                            "field": "scores"
                        }
                    }
                }
            }
        }
    }
    res = esorm.aggregate(query=query)

    if res["hits"]["total"]:
        data[paramID]["hits"] = res["hits"]["total"]
        acab = res["aggregations"]["count_anomaly"]["buckets"]
        athb = res["aggregations"]["top_hits"]["buckets"]
        atsb = res["aggregations"]["top_scores"]["buckets"]
        data[paramID]["histogram"]["abnormalHits"] = sum([[j["doc_count"] for j in i["histinfo"]["buckets"]] for i in acab], axis=0)  # .tolist()
        data[paramID]["top"]["abnormalHits"] = [{"username": i["key"], "hits": i["doc_count"]} for i in athb[0:size]]
        data[paramID]["top"]["abnormalScores"] = [{"username": i["key"], "scores": i["max_scores"]["value"]} for i in atsb[0:size]]

        if paramID == "_all":
            data[paramID]["anomalies_hits"] = [{"anomalyID": i["key"], "hits": i["doc_count"], "name": anomalies[i["key"]]["name"]} for i in acab]

    return Response(data)


class XRSForensicsViewSet(APIView):

    def post(self, request, deviceID, xrs, pk='model', ID=None):
        kwargs_f = locals()
        del kwargs_f['request']
        serializer = XRSForensicsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kwargs = serializer.data
        kwargs.update(kwargs_f)
        return Response(get_forensics(**kwargs))


class AnomaliesSummaryViewSet(APIView):

    def post(self, request, deviceID, anomalyID=None):
        data = defaultdict(list)
        data_pre = request.data
        data_pre['deviceID'] = deviceID
        serializer = EASSerializer(data=data_pre)
        serializer.is_valid(raise_exception=True)
        kwargs = serializer.data
        from_size = kwargs.pop('from_size')
        size = kwargs.pop('size')
        must_list = kwargs.pop('must_list')
        must_not_list = [{"term": {"scores": 0}}]
        if anomalyID:
            must_list += [{"term": {"anomalyID.keyword": anomalyID}}]
        else:
            anomalyID = "_all"
        esorm = AnomaliesScoresORM()
        datetime_list = get_datetime_list(esorm, deviceID, must_not_list, must_list, **kwargs)

        query = {
            "size": size,
            "_source": ["userId", "username", "timestamp", "scores", "summary", "anomalyID"],
            "from": from_size,
            "sort": [{"timestamp": {"order": "desc"}}, {"scores": {"order": "desc"}}],
            "query": {
                "bool": {
                    "must": must_list,
                    "filter": [{"terms": {"timestamp": datetime_list}}, {"term": {"deviceID.keyword": deviceID}}],
                    "must_not": must_not_list
                }
            }
        }
        res = esorm.search(False, query=query)
        docs = [i['_source'] for i in res['hits']['hits']]
        anomalies = get_anomaly(deviceID, anomalyID)
        if anomalyID == "_all":
            for i in anomalies:
                anomaly = anomalies[i]
                anomaly['summary'] = anomaly['forensics']['summary']
                del anomaly['forensics']
        else:
            anomaly = anomalies
            anomaly['summary'] = anomaly['forensics']['summary']
            del anomaly['forensics']

        for doc in docs:
            anomaly = anomalies[doc["anomalyID"]] if anomalyID == "_all" else anomalies
            data[anomalyID].append(dict_merge(anomaly, doc, True))

        data["hits"] = res["hits"]["total"]
        return Response(data)


class EASReportViewSet(APIView):

    def post(self, deviceID, paramID=None):
        data = defaultdict(dict)
        data_pre = request.data
        data_pre['deviceID'] = deviceID
        serializer = EASSerializer(data=data_pre)
        serializer.is_valid(raise_exception=True)
        kwargs = serializer.data
        startTimestamp = kwargs['startTimestamp']
        endTimestamp = kwargs['endTimestamp']
        size = kwargs.pop('size')
        from_size = kwargs.pop('from_size')
        must_list = kwargs.pop('must_list')
        must_not_list = [{"term": {"scores": 0}}]
        if paramID:
            must_list += [{"term": {"anomalyID.keyword": paramID}}]
            anomaly = get_anomaly(deviceID, paramID)
            data[paramID]['name'] = anomaly['name']
        else:
            paramID = "_all"
            anomalies = get_anomaly(deviceID, paramID)
            data[paramID]['name'] = {"en": "All anomaly", "zh": "全部异常"}
        esorm = AnomaliesScoresORM()
        datetime_list = get_datetime_list(esorm, deviceID, must_not_list, must_list, **kwargs)
        min_bound_date = simple_datetime(startTimestamp, str, True)[:10]
        max_bound_date = simple_datetime(endTimestamp - 3600 * 24, str, True)[:10]
        demo = {
            "hits": 0,
            "top": {
                "abnormalHits": [],
                "abnormalScores": []
            },
            "histogram": {
                "abnormalHits": []
            },
        }
        data[paramID].update(demo)
        query = {
            "size": size,
            "from": from_size,
            "_source": ["username", "scores"],
            "sort": [
                {"scores": {"order": "desc"}}
            ],
            "query": {
                "bool": {
                    "must": must_list,
                    "filter": [
                        {"terms": {"timestamp": datetime_list}},
                        {"term": {"deviceID.keyword": deviceID}}
                    ],
                    "must_not": must_not_list
                }
            },
            "aggs": {
                "count_anomaly": {
                    "terms": {
                        "field": "anomalyID.keyword",
                        "size": config.MAX_AGGS
                    },
                    "aggs": {
                        "histinfo": {
                            "date_histogram": {
                                "field": "timestamp",
                                "interval": "day",
                                "extended_bounds": {
                                    "min": min_bound_date,
                                    "max": max_bound_date
                                },
                                "min_doc_count": 0,
                                "format": "yyyy-MM-dd"
                            },
                            "aggs": {
                                "clone_count": {
                                    "cumulative_sum": {
                                        "buckets_path": "_count"
                                    }
                                }
                            }
                        }
                    }
                },
                "top_hits": {
                    "terms": {
                        "field": "username.keyword",
                        "size": config.TOP_SIZA,
                        "show_term_doc_count_error": True
                    }
                },
                "top_scores": {
                    "terms": {
                        "field": "username.keyword",
                        "size": config.TOP_SIZA,
                        "show_term_doc_count_error": True,
                        "order": [
                            {"max_scores": "desc"}
                        ]
                    },
                    "aggs": {
                        "max_scores": {
                            "max": {
                                "field": "scores"
                            }
                        }
                    }
                }
            }
        }
        res = esorm.aggregate(query=query)
        if res["hits"]["total"] != 0:
            data[paramID]["hits"] = res["hits"]["total"]
            acab = res["aggregations"]["count_anomaly"]["buckets"]
            athb = res["aggregations"]["top_hits"]["buckets"]
            atsb = res["aggregations"]["top_scores"]["buckets"]
            data[paramID]["histogram"]["abnormalHits"] = sum([[j["doc_count"] for j in i["histinfo"]["buckets"]] for i in acab], axis=0)  # .tolist()
            data[paramID]["top"]["abnormalHits"] = [{"username": i["key"], "hits": i["doc_count"]} for i in athb[0:size]]
            data[paramID]["top"]["abnormalScores"] = [{"username": i["key"], "scores": i["max_scores"]["value"]} for i in atsb[0:size]]
            if paramID == "_all":
                data[paramID]["anomalies_hits"] = [{"anomalyID": i["key"], "hits": i["doc_count"], "name": anomalies[i["key"]]["name"]} for i in acab]
        return Response(data)
