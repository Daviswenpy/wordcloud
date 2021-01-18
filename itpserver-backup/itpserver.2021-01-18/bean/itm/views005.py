# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-02-19 15:16:00
File Name: views005.py @v2.0
SOME NOTE: itpserver scores part
"""
from __future__ import unicode_literals

import pandas as pd
from collections import Counter

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.core.cache import cache

from itm import logger
from config import config
from esmodels import get_threat
from views004 import merge_models
from utils import simple_datetime
from exceptions import APIBaseError, APIDataNotFound
from elasticsearchorm import ERSResultsORM, ARSResultsORM, MRSResultsORM, EASResultsORM, ElasticsearchORM

import sys
reload(sys)
sys.setdefaultencoding('utf8')


__all__ = [
    'x_scores',
    'data_info',
]


pd.set_option('display.width', 260)


def catch_except(except_result, inlog=True):
    def make_wrapper(func):
        def log_wrapper(*args, **kw):
            try:
                result = func(*args, **kw)
            except:
                result = except_result
                if inlog:
                    logger.exception('PASS ERROR')
            return result
        return log_wrapper
    return make_wrapper


def cache_value(func):
    def wrapper(*args):
        if args in cache:
            return cache.get(args)
        else:
            result = func(*args)
            cache.set(args, result, 60)
            return result
    return wrapper


def _risk_level(arr):
    """
    pd func to apply riskLevel.
    """
    ARS, MRS, ERS = arr
    if ARS and MRS and ERS:
        if eval(config.LEVEL_5):
            return 5
        elif eval(config.LEVEL_4):
            return 4
        elif eval(config.LEVEL_3):
            return 3
        elif eval(config.LEVEL_2):
            return 2
        else:
            return 1


def get_risk_level(deviceID=None, xrs=None, field="timestamp"):
    ers_es = ERSResultsORM()
    mrs_es = MRSResultsORM()
    ars_es = ARSResultsORM()
    eas_es = EASResultsORM()

    es = ElasticsearchORM(index=['ars_results', 'mrs_results', 'ers_results', 'eas_results'])
    xrs_timestamp = int(es.field_aggs(mode='max', field=field, deviceID=deviceID)) / 1000 # max time in es
    # use in next version
    # wait mrs struct update
    # query = {
    #     "_source": ["username", "scores", "policyID"],
    #     "query": {
    #         "bool": {
    #             "must": [{"term": {"deviceID.keyword": deviceID}}],
    #             "must_not": [{"term": {"scores": 0}}],
    #             "filter": [{"term": {"timestamp": simple_datetime(xrs_timestamp, str, True)}}]
    #         }
    #     }
    # }
    # test = es.search(True, query=query)
    # tf = pd.DataFrame(test)

    if simple_datetime(None, int) - xrs_timestamp > 24 * 60 * 60:
        raise APIBaseError('No scores in {}.'.format(xrs_timestamp))

    # xrs_timestamp = 1608775200

    # @cache_value
    def get_df(xrs, deviceID, value, es):
        query = {
            "_source": ["username", "scores", "policyID"],
            "query": {
                "bool": {
                    "must": [{"term": {"deviceID.keyword": deviceID}}],
                    "must_not": [{"term": {"scores": 0}}],
                    "filter": [{"term": {"timestamp": value}}]
                }
            }
        }
        xrs_scores = es.search(True, query=query)
        df = pd.DataFrame(xrs_scores)
        size = df.index.size
        logger.info("xrs:{} size:{} ,if size is 0, pass error.".format(xrs, size))
        if size != 0:
            df = pd.DataFrame(df.loc[:, "_source"].values.tolist())
            try:
                df = df.set_index(["username", "policyID"]).unstack(level=1)
            except ValueError:
                df_cp = df.set_index(["username", "policyID"])
                mult_index = df_cp.index.values.tolist()
                cnt = Counter(mult_index)
                duplicates = [key for key in cnt.keys() if cnt[key] > 1]
                logger.error('ValueError: Index contains duplicate entries, cannot reshape with {}'.format(duplicates))
                return pd.DataFrame()

            if xrs == 'eas':
                df.columns = 'endpoint_' + df.columns.droplevel()
            else:
                df.columns = df.columns.droplevel()
            df.columns.name = None
            df.index.name = 'sip'
        return df

    def get_threat_level(model_list, fast_path=False):
        ers_models = merge_models(deviceID)
        threat_level_map = {i["modelID"]: i["threat_level"] for i in ers_models["ersModels"]}
        threat_level_list = [threat_level_map.get(i, 4) for i in model_list]
        if fast_path:
            return threat_level_list
        threat_weigth_list = [config.threat_level_mapping.get(i) for i in threat_level_list]
        return threat_weigth_list

    @cache_value
    def get_xrs_df(xrs):
        df_xrs = pd.DataFrame({"sip": [], xrs + "_scores": []}).set_index("sip")
        df_xrs_list = []
        value = simple_datetime(xrs_timestamp, str, True)

        if xrs == 'mrs':
            try:
                xrs_scores = mrs_es.match_obj_or_404(field=field, value=value, deviceID=deviceID)
            except APIDataNotFound:
                return df_xrs
            except:
                logger.exception('Unknow error!')
                return df_xrs

            for i in xrs_scores:
                df = pd.DataFrame(index=[i['_source']['policyID']], data=eval(i['_source']['scores']))
                df = df.T
                df.index.name = 'sip'
                df_xrs_list.append(df)
        else:
            if xrs == 'ars':
                df = get_df(xrs, deviceID, value, ars_es)
                df_xrs_list.append(df)
                df = get_df('eas', deviceID, value, eas_es)
            else:
                df = get_df(xrs, deviceID, value, ers_es)
            df_xrs_list.append(df)

        if df_xrs_list:
            if pd.__version__ < config.pd_old1_version:
                df_xrs = pd.concat(df_xrs_list, axis=1).fillna(0.2)
            else:
                df_xrs = pd.concat(df_xrs_list, axis=1, sort=False).fillna(0.2)

            if xrs == "ers":
                model_list = df_xrs.columns.tolist()
                threat_weigth_list = get_threat_level(model_list)
                df_xrs[xrs + '_scores'] = df_xrs[model_list].mul(threat_weigth_list).max(axis=1)
            else:
                df_xrs[xrs + '_scores'] = df_xrs.max(axis=1)
        return df_xrs.round(1)

    @catch_except({"defaults": 0.20, "order": [], "scores": {}}, inlog=True)
    def get_riskLevel():
        df_ars = get_xrs_df('ars')
        df_mrs = get_xrs_df('mrs')
        df_ers = get_xrs_df('ers')
        df = pd.concat([df_ars[['ars_scores']], df_mrs[['mrs_scores']], df_ers[['ers_scores']]], axis=1).fillna(0.2).replace(0, 0.2)
        if not df.empty:
            df['scores'] = df.apply(_risk_level, axis=1)
            risk_data = {"defaults": 1, "timestamp": xrs_timestamp}
            risk_data['scores'] = df[['scores']].to_dict("index")
            return risk_data

    @catch_except({"defaults": 0.20, "order": [], "scores": {}}, inlog=True)
    def get_arsScores():
        df_ars = get_xrs_df('ars')
        ars_data = {"defaults": 0.20, "timestamp": xrs_timestamp, "order": [], "feature_order": [], "feature_mode": "max", "scores": {}}
        un_columns = ['network', 'protocols', 'events', 'endpoint']
        ars_data['order'] = un_columns
        for col_name in un_columns:
            selector = df_ars.columns[df_ars.columns.str.contains(col_name)].astype(str)
            ars_data['feature_order'].append([i.split('_')[-1] for i in selector.tolist()])
            if pd.__version__ < config.pd_old1_version:
                df_ars[col_name] = df_ars.apply(lambda x: [x[i] for i in x.keys() if col_name in i], axis=1)
            else:
                df_ars[col_name] = df_ars[selector].apply(lambda x: x.tolist(), axis=1).apply(lambda x: x if isinstance(x, list) else [])

        df_ars = df_ars[un_columns]
        df_ars['scores'] = df_ars.apply(lambda x: [[i for i in x]], axis=1).apply(lambda x: x[0])
        ars_data['scores'] = df_ars[['scores']].to_dict('index')
        return ars_data

    @catch_except({"defaults": 0.20, "order": [], "scores": {}}, inlog=False)
    def get_xrsScores(xrs):
        df_xrs = get_xrs_df(xrs)
        xrs_data = {"defaults": 0.20, "timestamp": xrs_timestamp, "order": [], "scores": {}}
        df_xrs = df_xrs.drop([xrs + '_scores'], axis=1)
        model_list = df_xrs.columns.tolist()
        xrs_data['order'] = model_list
        if xrs == "ers":
            xrs_data['threat_level'] = get_threat_level(model_list, True)
        df_xrs['scores'] = df_xrs.apply(lambda x: [[i for i in x]], axis=1).apply(lambda x: x[0] if len(x) == 1 else x)
        xrs_data['scores'] = df_xrs[['scores']].to_dict('index')
        return xrs_data

    if xrs == 'riskLevel':
        data = get_riskLevel()

    elif xrs == 'arsScores':
        data = get_arsScores()

    elif xrs == 'ersScores' or xrs == 'mrsScores':
        data = get_xrsScores(xrs[:3])

    elif xrs is None:
        data = get_riskLevel(), get_arsScores(), get_xrsScores('ers'), get_xrsScores('mrs')
    return data


@api_view(http_method_names=['GET'])
def x_scores(request, deviceID, pk=None):
    weights = {"aWeight": 0.333, "mWeight": 0.333, "eWeight": 0.333}

    if pk:
        if pk == "weights":
            data = {"weights": weights}
        else:
            data = {pk: get_risk_level(deviceID, pk)}
    else:
        data = {"weights": weights}
        data['riskLevel'], data['arsScores'], data['ersScores'], data['mrsScores'] = get_risk_level(deviceID)
    return Response(data)


@api_view(http_method_names=['GET'])
def data_info(request, deviceID):
    """
    TODO: move in views004
    """
    data = {}
    data["threats"] = [{k: v["name"]} for k, v in get_threat(deviceID)["threats"].items()]
    return Response(data)


class XRSScoresViewSet(APIView):

    def get(self, request, deviceID, pk=None):
        weights = {"aWeight": 0.333, "mWeight": 0.333, "eWeight": 0.333}
        device = request.device
        if pk:
            if pk == "weights":
                data = {"weights": weights}
            else:
                data = {pk: get_risk_level(deviceID, device, pk)}
        else:
            data = {"weights": weights}
            data['riskLevel'], data['arsScores'], data['ersScores'], data['mrsScores'] = get_risk_level(deviceID, device)
        return Response(data)


class EASThreatViewSet(APIView):

    def get(self, request, deviceID):
        data = {}
        data["threats"] = [{k: v["name"]} for k, v in get_threat(deviceID)["threats"].items()]
        return Response(data)
