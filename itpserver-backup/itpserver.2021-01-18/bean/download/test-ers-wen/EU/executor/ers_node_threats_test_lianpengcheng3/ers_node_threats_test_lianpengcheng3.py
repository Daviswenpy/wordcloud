# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-08-12 18:15:24
File Name: ers_node_thrats_test_lianpengcheng3.py @v4.1
"""
# import copy

from utils import simple_datetime
from ers_node_threats.ers_node_threats import ers_node_threats


def get_EU(info):
    """
    Get detector instance.
    """
    return ers_node_thrats_test_lianpengcheng3(info)


class ers_node_thrats_test_lianpengcheng3(ers_node_threats):
    threats_type = 'external'
    node_type = 'external_portsscan'

    def __init__(self, detector_json):
        super(ers_node_thrats_test_lianpengcheng3, self).__init__(detector_json)

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
                        {"range": {"resp_p": {"lt": 10000}}},
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
                        "min_doc_count": self.at_least[0],
                        "size": self.config.MAX_AGGS
                    },
                    "aggs": {
                        "dipterm": {
                            "terms": {
                                "field": "resp_h",
                                "size": self.config.MAX_AGGS
                            },
                            "aggs": {
                                "resp_p#cnt": {
                                    "cardinality": {
                                        "field": "resp_p"
                                    }
                                },
                                "orig_p#cnt": {
                                    "cardinality": {
                                        "field": "orig_p"
                                    }
                                },
                                "scores_selector": {
                                    "bucket_selector": {
                                        "buckets_path": {
                                            "resp_pcnt": "resp_p#cnt",
                                            "orig_pcnt": "orig_p#cnt"
                                        },
                                        "script": "params.resp_pcnt>{} && params.orig_pcnt>{}".format(*self.at_least)
                                    }
                                }
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
                        "value": {
                            "bucket_script": {
                                "buckets_path": {},
                                "script": "1"
                            }
                        },
                        "_fill#dipterm#orig_h#key": {
                            "bucket_script": {
                                "buckets_path": {
                                },
                                "script": "0"
                            }
                        },
                        "count": {
                            "sum_bucket": {
                                "buckets_path": "dipterm._count"
                            }
                        }
                    }
                }
            }
        }
        return _query

    def external_portsscan(self, df):
        """
        name: ers_node_thrats_test_lianpengcheng3
        uuid: af55953d-669f-36e3-bdb8-7ee28319e140
        """
        if self.reuse:
            self.save_scores(df)
        return self.fill_frame(df)

    # def anomaly_filter_with_ports(self, df):
    #     """
    #     模版扩展
    #     出现并超过ports at_least为异常

    #     >>> df.head()
    #     >>>              dip    dpt                                userId
    #     >>> 0   172.25.31.74  50945  007a4387-ac24-6640-a973-a6acc6c6ce4d
    #     >>> 1  172.25.26.195   8406  00e83204-5cac-b443-ba95-804c7502225b
    #     >>> 2  172.25.19.161    135  013bd4f3-1305-e141-985a-7a7bfe656df8
    #     >>> 3  172.25.19.161    445  013bd4f3-1305-e141-985a-7a7bfe656df8
    #     >>> 4  172.25.19.161   1723  013bd4f3-1305-e141-985a-7a7bfe656df8
    #     """

    #     # transform dpt nunique with group by dip & userId
    #     df['cnt'] = df.groupby(['userId', 'dip'])['dpt'].transform('nunique')

    #     df = df[df['cnt'] > self.at_least]

    #     df = df.groupby('userId').agg(lambda x: x.unique().tolist()[:self.keep_cnt])

    #     ip_keyword = "resp_h" if self.node_type == 'internal_portsscan' else "orig_h"

    #     def to_query(arr):
    #         fqt = {
    #             "query": copy.deepcopy(self._query['query']),
    #             "sort": {"@timestamp": {"order": "desc"}}
    #         }
    #         fqt['query']['bool']['must'] += [{"term": {"userId.keyword": {"value": arr.name}}}, {"terms": {ip_keyword: arr.dip}}]
    #         return fqt

    #     if df.empty:
    #         return df

    #     return self.to_frame(df, to_query)

    def run(self, data_store, params):
        self.extract_data(data_store, params)


if __name__ == "__main__":
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "local_orig": {
                                "value": "false"
                            }
                        }
                    },
                    {
                        "term": {
                            "local_resp": {
                                "value": "true"
                            }
                        }
                    },
                    {
                        "term": {
                            "proto.keyword": {
                                "value": "tcp"
                            }
                        }
                    },
                    {
                        "term": {
                            "deviceID.keyword": "6a6887d4-b195-7ceb-f1d3-4d66eaf164a9"
                        }
                    },
                    {
                        "terms": {
                            "conn_state.keyword": [
                                "S1",
                                "S2",
                                "S3",
                                "SF",
                                "RSTO"
                            ]
                        }
                    }
                ],
                "must_not": [
                    {
                        "terms": {
                            "resp_h": []
                        }
                    },
                    {
                        "terms": {
                            "resp_p": []
                        }
                    }
                ],
                "should": [],
                "filter": [
                    {
                        "range": {
                            "resp_p": {
                                "lt": 10000
                            }
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": "2019-11-16T17:00:00+0800",
                                "lt": "2019-11-25T17:00:00+0800"
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
                    "min_doc_count": 10,
                    "size": 10000
                },
                "aggs": {
                    "dipterm": {
                        "terms": {
                            "field": "resp_h",
                            "size": 10000
                        },
                        "aggs": {
                            "resp_p#cnt": {
                                "cardinality": {
                                    "field": "resp_p"
                                }
                            },
                            "orig_p#cnt": {
                                "cardinality": {
                                    "field": "orig_p"
                                }
                            },
                            "scores_selector": {
                                "bucket_selector": {
                                    "buckets_path": {
                                        "resp_pcnt": "resp_p#cnt",
                                        "orig_pcnt": "orig_p#cnt"
                                    },
                                    "script": "params.resp_pcnt>10 && params.orig_pcnt>1"
                                }
                            }
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
                    "value": {
                        "bucket_script": {
                            "buckets_path": {},
                            "script": "1"
                        }
                    },
                    "_fill#dipterm#orig_h#key": {
                        "bucket_script": {
                            "buckets_path": {
                            },
                            "script": "0"
                        }
                    },
                    "count": {
                        "max_bucket": {
                            "buckets_path": "dipterm.resp_p#cnt"
                        }
                    }
                }
            }
        }
    }
    pass
