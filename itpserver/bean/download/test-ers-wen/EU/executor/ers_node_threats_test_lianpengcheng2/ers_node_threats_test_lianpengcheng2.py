# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-08-12 18:15:03
File Name: ers_node_threats_test_lianpengcheng2.py @v4.1
"""
import copy

from utils import simple_datetime
from ers_node_threats.ers_node_threats import ers_node_threats


def get_EU(info):
    """
    Get detector instance.
    """
    return ers_node_threats_test_lianpengcheng2(info)


class ers_node_threats_test_lianpengcheng2(ers_node_threats):
    threats_type = 'external'
    node_type = 'external_portscan'

    def __init__(self, detector_json):
        super(ers_node_threats_test_lianpengcheng2, self).__init__(detector_json)

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
                    "should": [],
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
                "three_features": {
                    "composite": {
                        "size": self.config.MAX_AGGS,
                        "sources": [
                            {"userId": {"terms": {"field": "userId.keyword"}}},
                            {"dip": {"terms": {"field": "orig_h"}}},
                            {"dpt": {"terms": {"field": "resp_p"}}}
                        ]
                    }
                }
            }
        }
        return _query

    def external_portscan(self, df):
        """
        name: ers_node_threats_test_lianpengcheng2
        uuid: 6a90d5e8-c967-3b2d-937f-f5572e49375e
        """
        if self.reuse:
            self.save_scores(df)
        return self.anomaly_filter_with_port(df)

    def anomaly_filter_with_port(self, df):
        """
        模版扩展
        出现并超过port at_least为异常

        >>> df.head()
        >>>              dip    dpt                                userId
        >>> 0   172.25.31.74  50945  007a4387-ac24-6640-a973-a6acc6c6ce4d
        >>> 1  172.25.26.195   8406  00e83204-5cac-b443-ba95-804c7502225b
        >>> 2  172.25.19.161    135  013bd4f3-1305-e141-985a-7a7bfe656df8
        >>> 3  172.25.19.161    445  013bd4f3-1305-e141-985a-7a7bfe656df8
        >>> 4  172.25.19.161   1723  013bd4f3-1305-e141-985a-7a7bfe656df8
        """

        # transform userId nunique with group by dip & dpt
        df['cnt'] = df.groupby(['dip', 'dpt'])['userId'].transform('nunique')

        df = df[df['cnt'] > self.at_least]

        df = df.groupby('userId').agg(lambda x: x.unique().tolist()[:self.keep_cnt])

        def to_query(arr):
            fqt = {
                "query": copy.deepcopy(self._query['query']),
                "sort": {"@timestamp": {"order": "desc"}}
            }
            fqt['query']['bool']['must'] += [{"term": {"userId.keyword": {"value": arr.name}}}, {"terms": {"resp_p": arr.dpt}}, {"terms": {"orig_h": arr.dip}}]
            return fqt

        if df.empty:
            return df

        return self.to_frame(df, to_query)

    def run(self, data_store, params):
        self.extract_data(data_store, params)


if __name__ == "__main__":
    pass
