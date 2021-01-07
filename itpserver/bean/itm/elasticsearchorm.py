# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-02-19 16:20:09
File Name: elasticsearchorm.py @v3.0
"""
import copy
import json
import datetime
from functools import partial

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan
from django.utils.translation import ugettext_lazy as _

from config import config
from utils import simple_datetime, concat_dict
from exceptions import APINotRigister, APIDataNotFound, APIBaseError


class ElasticSearchClient(object):
    """
    Elasticsearch client.
    """

    @staticmethod
    def get_es_servers():
        """
        Elasticsearch client use config.py file parameters.
        """

        es_client = Elasticsearch(config.ES_URL, http_auth=(config.USER, config.PASSWD), timeout=config.TIMEOUT)

        return es_client


class ElasticsearchORM(object):
    """
    Elasticsearch Object Relational Mapping.

    Attributes
    ----------
    index : str, default None
    doc_type : str, default '_all'
    es_client : Elasticsearch

    Examples
    --------
    Code initialization.
    >>> index = "test_index"
    >>> doc_type = "test_doc_type"
    >>> es = ElasticsearchORM(index=index, doc_type=doc_type)

    Index does not exist and uses mapping.
    >>> mapping = {"properties": {"scores": {"enabled": False}}}
    >>> es1 = ElasticsearchORM(index=index, doc_type=doc_type, mapping=mapping)

    Add a new doc.
    >>> es.add(doc_id='1', row_obj={"key":1, "user": "lian"})
    True

    Automatic generation of id.
    >>> es.add(row_obj={"key": 2, "user": "zhang"})
    True

    Get doc or 404.
    >>> es.get_obj_or_404(doc_id="1")
    {u'user': u'lian', u'key': 1}
    >>> es.get_obj_or_404(doc_id="2")
    Traceback (most recent call last):
    NotFound: TransportError(404, u'{"_index":"test_index","_type":"test_doc_type","_id":"2","found":false}')

    Get doc or create.
    >>> doc, created = es.get_obj_or_create(doc_id="1")
    >>> doc
    {u'user': u'lian', u'key': 1}
    >>> created
    False
    >>> es.get_obj_or_create(doc_id="3", doc_demo={"key3": 3, "user": "test"})
    ({u'key3': 3, u'user': u'test'}, True)

    Doc update.
    >>> es.update(doc_id="1", row_obj={"key11": 11})
    True
    >>> es.get_obj_or_404(doc_id="1")
    {u'key11': 11, u'user': u'lian', u'key': 1}

    Delete doc.
    >>> es.on_delete(doc_id="3")
    True

    Serach doc data using query.
    >>> es.search(use_scan=True, query={}) #doctest: +ELLIPSIS
    <generator object scan at 0x...>

    Search doc data using built-in query.
    >>> es.search(use_scan=True, start_datetime=start, end_datetime=end, deviceID=deviceID, must_list=must, filter_list=filter, must_not_list=must_not, group_id=group_id, source=None) # doctest: +SKIP
    >>> ... # doctest: +SKIP

    Aggregate doc data using query.
    >>> es.aggregate(query=query) # doctest: +SKIP
    >>> ... # doctest: +SKIP

    Aggregate doc data using built-in query.
    >>> es.aggregate(aggs=aggs, start_datetime=star, end_datetime=end, deviceID=deviceID, must_list=must, filter_list=filter,must_not_list=must_not, group_id=group_id) # doctest: +SKIP
    >>> ... # doctest: +SKIP

    Bulk insert data.
    >>> data = [{"_id": "4", "user": "test1", "key": 1}, {"_id": "5", "user": "test2", "key": 5}]
    >>> es.data_bulk(row_obj_list=data, bulk_num=10)
    {u'failed': [], u'success': 2}

    Built-in quick aggregation.

    Max value of field.
    >>> es.field_aggs(mode="max", field="key", deviceID=None)
    5.0

    Terms of field.
    >>> es.field_aggs(mode="terms", field="key")
    [{u'key': 1, u'doc_count': 2}, {u'key': 2, u'doc_count': 1}, {u'key': 5, u'doc_count': 1}]

    Extended stats value of field.
    >>> es.field_aggs(mode="extended_stats", field="key") # doctest: +SKIP +REPORT_NDIFF
    >>> ... # doctest: +SKIP

    Percentiles value of field.
    >>> es.field_aggs(mode="percentiles", field="key") # doctest: +SKIP +REPORT_NDIFF
    {u'values': {u'5.0': 1.0, u'25.0': 1.0, u'1.0': 1.0, u'95.0': 4.549999999999999, u'75.0': 2.75, u'99.0': 4.909999999999999, u'50.0': 1.5}}

    Delete index.
    >>> es.index_delete()
    {u'acknowledged': True}
    """

    def __init__(self, index=None, doc_type='_doc', mapping=None, settings=None):
        self.index = index
        self.es_client = ElasticSearchClient.get_es_servers()
        self.doc_type = doc_type
        if index:
            self.check_index(mapping, settings)

    # def check_index(self, mapping, settings):
    #     """
    #     Check the index of elasticsearch and create it if it does not
    #     exist, does not create mapping.
    #     Ignore 400 cause by IndexAlreadyExistsException when creating
    #     an index.
    #     """
    #     if not self.es_client.indices.exists(index=self.index):
    #         # settings = {"index": {"number_of_shards": 1, "number_of_replicas": 0}}
    #         self.es_client.indices.create(index=self.index, ignore=400)
    #         if self.index in {"eas_parameters", "eas_anomalies"}:
    #             mapping = {"properties": {self.index.split("_")[-1]: {"enabled": False}}}
    #         if mapping:
    #             self.es_client.indices.put_mapping(index=self.index, doc_type=self.doc_type, body=mapping)
    #     if settings:
    #         # settings = {"index.mapping.total_fields.limit": 50000}
    #         self.es_client.indices.put_settings(index=self.index, body=settings)

    def check_index(self, mapping, settings={"index.number_of_replicas": 0, "index.number_of_shards": 1}, dynamic=True):
        """
        Check the index of elasticsearch and create it if it does not
        exist, does not create mapping.
        Ignore 400 cause by IndexAlreadyExistsException when creating
        an index.
        """
        if isinstance(self.index, list):
            for index in self.index:
                if not self.es_client.indices.exists(index=index):
                    self.es_client.indices.create(index=index, ignore=400)

        elif not self.es_client.indices.exists(index=self.index):
            if settings:
                self.es_client.indices.put_settings(index=self.index, body=settings)
            self.es_client.indices.create(index=self.index, ignore=400)

            if self.index in {"parameters"} or dynamic is False:
                mapping = {
                    "dynamic": False,
                    "properties": {
                        "type": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                }
            if mapping:
                self.es_client.indices.put_mapping(index=self.index, doc_type=self.doc_type, body=mapping)

    def get_obj_or_404(self, doc_id):
        """
        Get a typed JSON document from the index based on `doc_id`.
        """
        try:
            obj = self.es_client.get(index=self.index, doc_type=self.doc_type, refresh=True, id=doc_id)
            if obj["_source"].get("is_active") is not True and self.index == "itm_configs":
                raise Exception
            return obj["_source"]
        except Exception as e:
            if self.index == "itm_configs":
                raise APINotRigister
            else:
                raise APIDataNotFound(detail=_(getattr(e, 'error', getattr(e, 'message', 'Uncaught'))), status=1)

    def get_obj(self, doc_id):
        """
        Get a typed JSON document from the index based on `doc_id`.
        """
        try:
            obj = self.es_client.get(index=self.index, doc_type=self.doc_type, refresh=True, id=doc_id)
            return obj["_source"]
        except Exception as e:
            raise APIDataNotFound(detail=_(getattr(e, 'error', getattr(e, 'message', 'Uncaught'))))

    def create_obj(self, doc_id, row_obj):
        res = self.es_client.index(index=self.index, refresh=True, doc_type=self.doc_type, body=row_obj, id=doc_id) # here, not exist create, or uodate
        results = res.get('result', False)
        if results not in {'created', 'updated'}:
            raise APIBaseError('Created or updated doc failed with {}'.format(res))
        return results

    def mget(self, body, **kwargs):
        """
        Get multiple documents based on an index, type (optional) and ids, ignore ids that do not exist.
        """
        es_result = self.es_client.mget(index=self.index, doc_type=self.doc_type, body=body, refresh=True, **kwargs)
        return es_result

    def get_obj_or_create(self, doc_id, demo=config.DEFAULT_CONFIG):
        """
        Get doc or create a doc for index with default doc template.
        """
        try:
            obj = self.es_client.get(index=self.index, doc_type=self.doc_type, refresh=True, id=doc_id)
            return (obj["_source"], False)
        except Exception:
            if 'deviceID' in demo:
                demo["deviceID"] = doc_id
            res = self.add(doc_id, demo)
            obj = self.get_obj_or_404(doc_id)
            return (obj, res)

    def match_obj_or_404(self, deviceID=None, field=None, value=None):
        """
        Execute a search query and get back search hits that match the query.
        """
        try:
            if deviceID is None:
                data = {
                    "query": {
                        "bool": {
                            "filter": [{"term": {field: value}}]
                        }
                    }
                }
            else:
                data = {
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {field: value}},
                                {"term": {"deviceID.keyword": deviceID}}
                            ]
                        }
                    }
                }
            res = self.es_client.search(index=self.index, doc_type=self.doc_type, body=data)
            doc = res["hits"]["hits"]
            if len(doc) == 0:
                raise APIDataNotFound(detail="Data is null.")
            return doc
        except Exception as e:
            raise APIDataNotFound(detail=_(e.message))

    def add(self, doc_id=None, row_obj=None):
        """
        Adds or updates a typed JSON document in a specific index, making it searchable, and returns True.
        """
        try:
            if doc_id is None:
                res = self.es_client.index(index=self.index, doc_type=self.doc_type, refresh=True, body=row_obj)
            else:
                res = self.es_client.index(index=self.index, doc_type=self.doc_type, refresh=True, body=row_obj, id=doc_id)
            return res["result"] == "created"
        except Exception as e:
            # e = traceback.format_exc()
            raise APIDataNotFound(detail=_(e.message))

    def update(self, doc_id, row_obj):
        """
        Update a document based on a script or partial data provided, and returns True.
        """
        try:
            res = self.es_client.update(index=self.index, refresh=True, doc_type=self.doc_type, body={"doc": row_obj, "doc_as_upsert": False}, id=doc_id)
            return res["result"] == "updated"
        except Exception as e:
            raise APIDataNotFound(detail=_(e.message))

    def on_delete(self, doc_id):
        """
        Delete a typed JSON document from a specific index based on its id, and returns True or 404.
        """
        try:
            res = self.es_client.delete(index=self.index, doc_type=self.doc_type, refresh=True, id=doc_id)
            return res["result"] == "deleted"
        except Exception as e:
            raise APIDataNotFound(detail=_(e.message))

    def index_delete(self, ignore=[400, 404]):
        """
        Delete all doc of index, And ignore 400 and 404 errors.
        """
        res = self.es_client.indices.delete(index=self.index, ignore=ignore)
        return res

    def field_aggs(self, mode=None, field=None, deviceID=None, filter_list=None, must_not_list=None, must_list=None):
        """
        Simple aggregation of a field.
        Gets the max, min, avg, terms, cardinal number, stats,
        extended_stats, sum, percentiles, percentile_ranks of a field.
        Behind the scenes this method calls search(...).
        If you need other query to use function aggregate(query).

        Parameters
        ----------
        field : int, float, datetime or str(int or float)
            According to the field get the aggs value.
        """
        must_list = must_list or []
        mode_options = ['max', 'min', 'avg', 'cardinality', 'stats',
                        'extended_stats', 'terms', 'sum', 'percentiles',
                        'percentile_ranks']
        if mode not in mode_options:
            raise ValueError("invalid value for 'mode' parameter,"
                             " valid options are: {}".format(mode_options))
        if deviceID is None:
            data = {
                "size": 0,
                "aggs": {
                    mode + "_" + field: {
                        mode: {
                            "field": field
                        }
                    }
                }
            }
        else:
            data = {
                "size": 0,
                "query": {
                    "bool": {
                        "must": [{
                            "term": {
                                "deviceID.keyword": deviceID
                            }
                        }] + must_list
                    }
                },
                "aggs": {
                    mode + "_" + field: {
                        mode: {
                            "field": field
                        }
                    }
                }
            }
        if filter_list:
            data["query"]["bool"]["filter"] = filter_list
        if must_not_list:
            data["query"]["bool"]["must_not"] = must_not_list
        res = self.es_client.search(index=self.index, doc_type=self.doc_type, body=data)
        try:
            value = res["aggregations"][mode + "_" + field]["value"]
        except KeyError:
            try:
                value = res["aggregations"][mode + "_" + field]["buckets"]
            except KeyError:
                value = res["aggregations"][mode + "_" + field]
        if value is None:
            value = 0
        return value

    def data_bulk(self, row_obj_list, bulk_num=5000):
        """
        Perform many index/delete operations in a single API call.
        Not set doc _id : "_id": row_obj.get("_id", None).

        Parameters
        ----------
        row_obj_list : list
            Doc list.
        bukl_num : int, default 5000
            Number of data bars per bulk.
        """
        load_data = []
        i = 1
        for row_obj in row_obj_list:
            action = {
                "_index": self.index,
                "_type": self.doc_type,
                "_id": row_obj.pop("_id", None),
                "_source": row_obj
            }
            load_data.append(action)
            i += 1
            if len(load_data) == bulk_num:
                success, failed = bulk(self.es_client, load_data, index=self.index, refresh=True, raise_on_error=True)
                del load_data[0:len(load_data)]
                print(success, failed)

        if len(load_data) > 0:
            success, failed = bulk(self.es_client, load_data, index=self.index, refresh=True, raise_on_error=True)
            del load_data[0:len(load_data)]
            return {"success": success, "failed": failed}

    def search(self, use_scan=False, start_datetime=None, end_datetime=None, deviceID=None,
               must_list=None, filter_list=None, must_not_list=None, group_id=None, source=None,
               use_from=None, use_sort=None, time_field="@timestamp", time_include=("gte", "lt"),
               query=None, **kwargs):
        """
        Search or scan docs. Behind the scenes this method calls search(…).
        If use query, do func twice when group is flag("notset_group").
        If you need other query to use the query parameter.
        """

        def _search(use_scan=False, query=None, **kwargs):
            if use_scan:
                res = scan(client=self.es_client, index=self.index, query=query, **kwargs)
            else:
                res = self.es_client.search(index=self.index, body=query, **kwargs)
            return res

        if query is None:
            must_list = must_list or []
            filter_list = filter_list or []
            must_not_list = must_not_list or []
            start_time = simple_datetime(start_datetime, str, True)
            end_time = simple_datetime(end_datetime, str, True)
            query = {
                "query": {
                    "bool": {
                        "must": [{"match_all": {}}] + must_list,
                        "filter": [
                            {
                                "range": {
                                    time_field: {
                                        time_include[0]: start_time, time_include[1]: end_time
                                    }
                                }
                            },
                            {
                                "term": {"deviceID.keyword": deviceID}
                            }
                        ] + filter_list,
                        "must_not": must_not_list
                    }
                }
            }
            if source:
                query["_source"] = source
            if use_from:
                query["from"] = use_from
            if use_sort:
                query["sort"] = use_sort
        return _search(use_scan, query, **kwargs)

    def _search(self, query={"size": 10000}, **kwargs):
        res = self.es_client.search(index=self.index, body=query, **kwargs)
        return res

    def aggregate(self, aggs=None, start_datetime=None, end_datetime=None,
                  deviceID=None, must_list=None, filter_list=None,
                  must_not_list=None, group_id=None, time_field="@timestamp",
                  time_include=("gte", "lt"), query=None, **kwargs):
        """
        Aggregate data, if use query, do func twice when group is flag.
        Search is not allowed in aggregate.If you need other query to
        use the query parameter.

        Parameters
        ----------
        start_datetime : datetime

        Note
        ----
        Sorting is not valid when groupid is empty.
        """
        def _search(query=None, **kwargs):
            res = self.es_client.search(index=self.index, body=query, **kwargs)
            return res

        if query is None:
            must_list = must_list or []
            filter_list = filter_list or []
            must_not_list = must_not_list or []
            aggs = aggs or {}
            start_time = simple_datetime(start_datetime, str, True)
            end_time = simple_datetime(end_datetime, str, True)
            query = {
                "query": {
                    "bool": {
                        "must": [{"match_all": {}}] + must_list,
                        "filter": [
                            {
                                "range": {
                                    time_field: {
                                        time_include[0]: start_time, time_include[1]: end_time
                                    }
                                }
                            },
                            {
                                "term": {"deviceID.keyword": deviceID}
                            }
                        ] + filter_list,
                        "must_not": must_not_list
                    }
                },
                "from": 0,
                "size": 0,
                "aggs": aggs
            }
            if group_id == "notset_group":
                query_userId = copy.deepcopy(query)
                query_sourceIp = copy.deepcopy(query)
                query_sourceIp_str = json.dumps(query_sourceIp).replace("userId.keyword", "sourceIp")
                query_sourceIp = json.loads(query_sourceIp_str)
                query_userId["query"]["bool"]["must"] += [{"exists": {"field": "userId"}}]
                res_userId = _search(query_userId, **kwargs)
                query_sourceIp["query"]["bool"]["must_not"] += [{"exists": {"field": "userId"}}]
                query_sourceIp["query"]["bool"]["must_not"].remove(query_sourceIp["query"]["bool"]["must_not"][-2])
                res_sourceIp = _search(query_sourceIp, **kwargs)
                res = concat_dict(res_userId, res_sourceIp)
            else:
                res = _search(query, **kwargs)
        else:
            res = _search(query, **kwargs)
        return res


DeviceORM = partial(ElasticsearchORM, "itm_configs")

# mrs something
TasksORM = partial(ElasticsearchORM, "train_states")

# ers something
ERSModelsORM = partial(ElasticsearchORM, "ers_models")
ERSCustomModelsORM = partial(ElasticsearchORM, "ers_custom_models")

# scores results
EASResultsORM = partial(ElasticsearchORM, 'eas_results')
ERSResultsORM = partial(ElasticsearchORM, 'ers_results')
MRSResultsORM = partial(ElasticsearchORM, 'mrs_results')
ARSResultsORM = partial(ElasticsearchORM, 'ars_results')

NETWORKScoresORM = partial(ElasticsearchORM, "network_scores")
PROTOCOLSScoresORM = partial(ElasticsearchORM, "swg_scores")
# EVENTSScoresORM = partial(ElasticsearchORM, "incidentlog_scores")

# eas something
EASThreatORM = partial(ElasticsearchORM, "eas_threat")

AnomaliesORM = partial(ElasticsearchORM, "anomalies")
ParametersORM = partial(ElasticsearchORM, "parameters")

# log something
# EndpointORM = partial(ElasticsearchORM, "endpoint-*")
# SWGORM = partial(ElasticsearchORM, "swg-*")
# NetworkORM = partial(ElasticsearchORM, "network-*")
# IncidentlogORM = partial(ElasticsearchORM, "incidentlog-*")
# SSlORM = partial(ElasticsearchORM, "ssl-*")
# DNSORM = partial(ElasticsearchORM, "dns-*")

# policy scores
ARSScoresORM = partial(ElasticsearchORM, "ars_scores")
MRSScoresORM = partial(ElasticsearchORM, "mrs_scores")
AnomaliesScoresORM = partial(ElasticsearchORM, "anomalies_scores")


def auto_client(index_prefix='swg', days=7, start_date=datetime.date.today()):
    return ElasticsearchORM([index_prefix + "-" + (start_date - datetime.timedelta(i)).strftime("%Y.%m.%d") for i in range(days + 1)])
