# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-03-17 18:02:52
File Name: urls.py @v3.4
"""
from django.conf.urls import url

from views import *


urlpatterns = [
    # total cnt: 51
    # AllowAny
    # api: check-in # method: POST
    url(r'^ITMCP/v1/sessions$', check_in, name='check-in'),

    # IsAuthenticated
    # api: login-out # method: GET DELETE
    url(r'^ITMCP/v1/sessions/(?P<sessionID>([^/]+))$', login_out, name='login-out'),
    # url(r'^ITMCP/v1/sessions$', LoginViewSet.as_view(), name='login_out'),

    # api: itm-register # method: POST DELETE
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))$', register, name='register'),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))$', DeviceRegViewSet.as_vies(), name='register'),
    # api: configuration # method: GET
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/configurations$', configuration, name='configuration'),
    # api: itm-configs # method: POST
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/configurations/itmConfigs$', itm_configs, name='itm-configs'),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/configurations/itmConfigs$', DeviceViewSet.as_view(), name='itm-conf'),
    # api: conf-xrs # method: GET POST
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/configurations/itmConfigs/(?P<pk>(ars)|(mrs)|(ers)|(versions))$', conf_xrs, name='conf-xrs'),
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/configurations/itmConfigs/(?P<pk>(ars)|(mrs)|(ers))/(?P<bk>(blacklists))$', conf_xrs, name='conf-xrs'),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/configurations/itmConfigs/(?P<pk>(ars)|(mrs)|(ers)|(versions))$', DeviceConfViewSet.as_view(), name='conf-xrs'),

    # api: x-scores # method: GET
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/scores$', x_scores, name='x-scores'),
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/scores/(?P<pk>(arsScores)|(mrsScores)|(ersScores)|(weights)|(riskLevel))$', x_scores, name='x-scores'),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/scores/(?P<pk>(arsScores)|(mrsScores)|(ersScores)|(weights)|(riskLevel))$', XRSScoresViewSet.as_view(), name='x-scores'),

    # api: mrs-tasks # method: POST
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/tasks/mrs/(?P<taskID>.*)$', mrs_tasks, name='mrs-tasks'),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/tasks/mrs/(?P<taskID>.*)$', MRSTasksViewSet.as_view(), name='mrs-tasks'),
    # api: tasks-status # method: GET
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/tasks/mrs$', tasks_status, name='tasks-status'),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/tasks/mrs$', TaskStatusViewSet.as_view(), name='tasks-status'),
    # api: ers-models # method: GET POST DELETE
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/models/ers$', ers_models, name='ers-models'),
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/models/ers/(?P<pk>(version))$', ers_models, name='ers-models'),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/models/ers/(?P<pk>(version))$', ERSModelsViewSet.as_view(), name='ers-models'),
    # api: eas-anomaly # method: GET
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/anomalies$', eas_anomaly, name="eas-anomaly"),
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/anomalies/(?P<anomalyID>([^/]+))$', eas_anomaly, name="eas-anomaly"),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/anomalies/(?P<anomalyID>([^/]+))$', EASAnomalyViewSet.as_view(), name="eas-anomaly"),
    # api: eas-parameters # method: GET
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/eas/parameters$', eas_parameters, name="eas-parameters"),
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/eas/parameters/(?P<paramID>([^/]+))$', eas_parameters, name="eas-parameters"),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/eas/parameters/(?P<paramID>([^/]+))$', EASParametersViewSet.as_view(), name="eas-parameters"),

    # api: upload-file # method: POST
    url(r'^ITMCP/v1/upload/files/', upload_file, name="upload-file"),
    # url(r'ITMCP/v1/upload/files/', UploadFileViewSet.as_view(), name="upload-file"),
    # api: download-file # method: GET
    url(r'^ITMCP/v1/download/files/(?P<filename>([^/]+))', download_file, name="download-file"),
    url(r'^ITMCP/v1/download/files/', download_file, name="download-file"),
    # url(r'ITMCP/v1/download/files/(?P<filename>([^/]+))', DownloadFileViewSet.as_view(), name="download-file"),

    # api: xrs-forensics # method: POST
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/forensics/(?P<xrs>(ers|ars))$', xrs_forensics, name="xrs-forensics"),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/forensics/eas$', eas_forensics, name="eas-forensics"),
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/forensics/(?P<xrs>(ers))/(?P<pk>(model|param))/(?P<ID>([^/]+))$', xrs_forensics, name="xrs-forensics"),
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/forensics/(?P<xrs>(eas))/(?P<pk>(threat|anomalyGroup|anomaly))/(?P<ID>([^/]+))$', xrs_forensics, name="xrs-forensics"),
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/forensics/(?P<xrs>(ars))/(?P<pk>(protocols|network))$', xrs_forensics, name="xrs-forensics"),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/forensics/(?P<xrs>(ars))/(?P<pk>(protocols|network))$', XRSForensicsViewSet.as_view(), name="xrs-forensics"),

    # api: eas-report # method: POST
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/report/eas$', eas_report, name="eas-report"),
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/report/eas/(?P<paramID>([^/]+))$', eas_report, name="eas-report"),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/report/eas/(?P<paramID>([^/]+))$', EASReportViewSet.as_view(), name="eas-report"),
    # api: eas anomaliesSummary # method: POST
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/anomaliesSummary/eas$', anomaliesSummary, name="anomaliesSummary"),
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/anomaliesSummary/eas/(?P<anomalyID>([^/]+))$', anomaliesSummary, name="anomaliesSummary"),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/anomaliesSummary/eas/(?P<anomalyID>([^/]+))$', AnomaliesSummaryViewSet.as_view(), name="anomaliesSummary"),

    # api: data-info # method: GET
    url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/data/info$', data_info, name="data-info"),
    # url(r'^ITMCP/v1/devices/(?P<deviceID>([^/]+))/data/info$', EASThreatViewSet.as_view(), name="data-info"),

]


# TODO
# 1.提取共用路径
# 2.高级参数传递优化
# 3.缺省参数视图合并

# urlpatterns1 = [
#     url(r'^ITMCP/v1/',
#         include([
#             url(r'^sessions$', check_in, name='check-in'),
#             url(r'^sessions(?P<sessionID>([^/]+))$', login_out, name='login-out'),
#         ]),
#         include([
#             url(r'^devices/(?P<deviceID>([^/]+))',
#                 include([
#                     url(r'^$', register, name='register'),
#                     url(r'^$')
#                 ])
#                 )
#         ]),
#         )
# ]
