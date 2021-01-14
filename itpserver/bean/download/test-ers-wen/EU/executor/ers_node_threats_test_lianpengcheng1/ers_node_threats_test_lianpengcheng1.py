# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-08-12 18:10:30
File Name: ers_node_threats_test_lianpengcheng1.py @v4.1
"""
# import copy

from utils import simple_datetime
from ers_node_threats.ers_node_threats import ers_node_threats


def get_EU(info):
    """
    Get detector instance.
    """
    return ers_node_threats_test_lianpengcheng1(info)


class ers_node_threats_test_lianpengcheng1(ers_node_threats):
    threats_type = 'external'
    node_type = 'external_connection'

    def __init__(self, detector_json):
        super(ers_node_threats_test_lianpengcheng1, self).__init__(detector_json)

    @property
    def get_query(self):
        _query = {
            # "sort": {"@timestamp": {"order": "desc"}},
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_orig": {"value": "false"}}},
                        {"term": {"local_resp": {"value": "true"}}},
                        {"term": {"proto.keyword": {"value": "tcp"}}},
                        {"term": {"deviceID.keyword": self.deviceID}},
                        {"terms": {"conn_state.keyword": ["S1", "S2", "S3", "SF", "RSTO", "RSTR"]}}
                    ],
                    "must_not": [
                        {"terms": {"resp_h": self.white_list}},
                        {"terms": {"resp_p": self.ignore_ports}},
                    ],
                    "should": [
                    ],
                    "filter": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": simple_datetime(self.start_time, str, True),
                                    "lt": simple_datetime(self.end_time, str, True)
                                }
                            }
                        }
                    ]
                }
            },
            "size": 0,
            "aggs": {
                "ipterm": {
                    "terms": {
                        "field": "userId.keyword",
                        "min_doc_count": self.at_least,
                        "size": self.config.MAX_AGGS
                    },
                    "aggs": {
                        "dipterm": {
                            "terms": {
                                "field": "resp_p",
                                "size": self.config.MAX_AGGS
                            },
                            "aggs": {
                                "orig_h#cnt": {
                                    "cardinality": {
                                        "field": "orig_h"
                                    }
                                },
                                "scores_selector": {
                                    "bucket_selector": {
                                        "buckets_path": {
                                            "doc_count": "_count",
                                            "set_port": "_key",
                                            "orig_h_cnt": "orig_h#cnt"
                                        },
                                        "script": "(params.doc_count>10 && [4786, 161, 162, 1433, 3306, 1521, 1434, 69, 111, 123, 53].contains(params.set_port)) || (params.orig_h_cnt>10)"
                                    }
                                },
                                "_value": {
                                    "bucket_script": {
                                        "buckets_path": {
                                            "doc_count": "_count",
                                            "set_port": "_key",
                                            "orig_h_cnt": "orig_h#cnt"
                                        },
                                        "script": "params.orig_h_cnt>10?2:(params.doc_count>10 && [4786, 161, 162, 1433, 3306, 1521, 1434, 69, 111, 123, 53].contains(params.set_port))?1:0"
                                    }
                                }
                            }
                        },
                        "value": {
                            "max_bucket": {
                                "buckets_path": "dipterm>_value"
                            }
                        },
                        "scores_selector": {
                            "bucket_selector": {
                                "buckets_path": {
                                    "dipterm": "dipterm._bucket_count"
                                },
                                "script": "params.dipterm>0"
                            }
                        },
                        "_fill#dipterm#resp_p#key": {
                            "bucket_script": {
                                "buckets_path": {},
                                "script": "0"
                            }
                        }
                    }
                }
            }
        }
        return _query

    def external_connection(self, df):
        """
        name: ers_node_threats_test_lianpengcheng1
        uuid: 2ccae299-81c6-3d86-b42c-dcfc364e5280
        """
        if self.reuse:
            self.save_scores(df)
        return self.fill_frame(df)

    def run(self, data_store, params):
        self.extract_data(data_store, params)


if __name__ == "__main__":
    pass
