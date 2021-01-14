# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-02-19 15:02:35
File Name: views004.py @v2.0
SOME NOTE: itpserver mrs task and ers models and eas anomaly parameters part
"""
from __future__ import unicode_literals

import copy

from django.utils.translation import ugettext_lazy as _

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from config import config
from esmodels import Tasks
from viewsfuncs import update_task
from exceptions import APIDataNotFound
from esmodels import get_anomaly, get_parameter, save_parameters
from elasticsearchorm import ParametersORM, ERSModelsORM, ERSCustomModelsORM
from serializers import UploadModelsFileSerializer, MRSTasksSerializer, TasksSerializer


__all__ = [
    'ers_models',
    'mrs_tasks',
    'tasks_status',
    'eas_anomaly',
    'eas_parameters',
]


def _change_display(modelID, models_list):
    for model in models_list:
        if model['modelID'] == modelID:
            models_list[models_list.index(model)]['display'] = False
    return models_list


def _get_models(modelID, models_list):
    return [model for model in models_list if model['modelID'] == modelID][0] # given the modelID/models_list, once included, return the model


def _ers_custom_models(deviceID, ers_models_custom_orm=None, old_custom_models=None, modelID_list=None, new_custom_models=None):
    _old_custom_models = copy.deepcopy(old_custom_models)

    up_modelID_list = []
    if new_custom_models: # post custom model, run this
        for model in new_custom_models['ersModels']:
            model.setdefault('display', True) # new custom model add k-v,display:True
            up_modelID_list.append(model["modelID"]) # add new modelID into the list

        for new_model in new_custom_models['ersModels']: # traverse the new custom models
            if new_model['modelID'] in [old_model['modelID'] for old_model in old_custom_models['ersModels']]: # if new modelID in old_custom_models_modelID_list
                if _get_models(new_model['modelID'], old_custom_models['ersModels'])['display']: # if included,display=True
                    new_custom_models['ersModels'].remove(_get_models(new_model['modelID'], new_custom_models['ersModels'])) # because there are models in old-custom-models, rm the new custom models, all of the new
                else:
                    old_custom_models['ersModels'].remove(_get_models(new_model['modelID'], old_custom_models['ersModels'])) # new custom models in old custom, but display=false, among the old custom rm the exist one(new)

        old_custom_models['ersModels'] += new_custom_models['ersModels'] # after fix the exist problems, append the new models which is absolute new

    if modelID_list: # delete, run
        for modelID in modelID_list:
            if modelID in [old_model['modelID'] for old_model in old_custom_models['ersModels']]:
                old_custom_models['ersModels'] = _change_display(modelID, old_custom_models['ersModels'])
            else:
                raise APIDataNotFound(_('Model {} not found.'.format(modelID)), 1)

    if old_custom_models != _old_custom_models: # after updated, there're some change
        old_custom_models['version'] += 1 # version+1
        en_updated = ers_models_custom_orm.update(deviceID, old_custom_models) # update custom models, return true
        if en_updated:
            if modelID_list: # delete
                update_task(deviceID=deviceID, pk="custom_models", action="remove", modelID_list=modelID_list)
            if up_modelID_list: # post, add custom models
                update_task(deviceID=deviceID, pk="custom_models", action="upload", modelID_list=up_modelID_list) # update task
    return {}


def merge_models(deviceID, pk=None, use_all=False, **action):
    """
    Mergr 'ers_models' and 'ers_custom_models'.

    Parameters
    ----------
    out : dict
        Returns

    pk : None, str
        Returns version dict if `pk`
    """
    ers_models_orm = ERSModelsORM()
    version = int(ers_models_orm.field_aggs(mode='max', field='version'))
    ers_models_custom_orm = ERSCustomModelsORM()
    ers_models_custom, _ = ers_models_custom_orm.get_obj_or_create(deviceID, {'ersModels': [], 'version': 0})

    if pk:
        # we have a fast-path here.
        return {"status": 0, "version": str(version) + str(ers_models_custom['version']).zfill(4)}

    if action != {}:
        # we have a fast-path here, delete custom model/post new custom models
        return _ers_custom_models(deviceID, ers_models_custom_orm, ers_models_custom, **action)

    models = ers_models_orm.match_obj_or_404(field="version", value=version)[0]["_source"]["ersModels"]
    [model.setdefault('type', 'built-in') for model in models]
    models_custom = ers_models_custom['ersModels']
    [model.setdefault('type', 'user-set') for model in models_custom]
    ers_models_list = [i for i in models if config.ITM_VERSION >= i.get('modelVersion')]

    if use_all:
        # we have a fast-path here.
        return {"ersModels": ers_models_list + models_custom}

    ers_custom_models_list = [i for i in models_custom if i['display']]

    return {"status": 0, "version": str(version) + str(ers_models_custom['version']).zfill(4), 'ersModels': ers_models_list + ers_custom_models_list}


@api_view(http_method_names=['GET', 'POST', 'DELETE'])
def ers_models(request, deviceID, pk=None):

    if request.method == 'GET':
        data = merge_models(deviceID, pk)

    if request.method == 'POST':
        serializer = UploadModelsFileSerializer(request.POST, request.FILES)
        serializer.is_valid(raise_exception=True)
        filename, new_custom_models = serializer.save(deviceID)
        merge_models(deviceID, new_custom_models=new_custom_models)
        data = {'resourceName': filename}

    if request.method == 'DELETE':
        data = merge_models(deviceID, modelID_list=request.data.get('modelID_list', []))

    return Response(data)


@api_view(http_method_names=['POST'])
def mrs_tasks(request, **kwargs):
    data_pre = request.data
    data_pre.update(kwargs)
    data_pre['taskIDs'] = [i['policyID'] for i in request.device['itmConfigs']['mrs']['chosenDLPPolicies']]
    serializer = MRSTasksSerializer(data=data_pre)
    serializer.is_valid(raise_exception=True)
    data = serializer.data
    chosenGroups = data.pop('chosenGroups')
    for groupID in chosenGroups:
        update_task(pk="status", groupID=groupID, **data)
    return Response()


@api_view(http_method_names=['GET'])
def tasks_status(request, deviceID):
    tasks = Tasks.objects.get(deviceID)
    serializer = TasksSerializer(tasks)
    return Response(serializer.data)


@api_view(http_method_names=['GET'])
def eas_anomaly(request, deviceID, anomalyID='_all'):
    data = {anomalyID: get_anomaly(anomalyID)}
    return Response(data)


@api_view(http_method_names=["GET", "POST"])
def eas_parameters(request, deviceID, paramID=None):
    data = {}
    if request.method == 'GET':
        data['parameters'] = get_parameter(deviceID, paramID)

    if request.method == 'POST' and paramID is None:
        data["updated"] = save_parameters(request.data['parameters'])

    return Response(data)


class ERSModelsViewSet(APIView):

    def get(self, request, deviceID, pk=None):
        return Response(merge_models(deviceID, pk))

    def post(self, request, deviceID, pk=None):
        serializer = UploadModelsFileSerializer(request.POST, request.FILES)
        serializer.is_valid(raise_exception=True)
        filename, new_custom_models = serializer.save(deviceID)
        merge_models(deviceID, new_custom_models=new_custom_models)
        return Response({'resourceName': filename})

    def delete(self, request, deviceID, pk=None):
        return Response(merge_models(deviceID, modelID_list=request.data.get('modelID_list', [])))


class MRSTasksViewSet(APIView):

    def post(self, request, **kwargs):
        data_pre = request.data
        data_pre.update(kwargs)
        data_pre['taskIDs'] = [i['policyID'] for i in request.device['itmConfigs']['mrs']['chosenDLPPolicies']]
        serializer = MRSTasksSerializer(data=data_pre)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        chosenGroups = data.pop('chosenGroups')
        for groupID in chosenGroups:
            update_task(pk="status", groupID=groupID, **data)
        return Response()


class TaskStatusViewSet(APIView):

    def get(self, request, deviceID):
        tasks = Tasks.objects.get(deviceID)
        serializer = TasksSerializer(tasks)
        return Response(serializer.data)


class EASAnomalyViewSet(APIView):

    def get(self, request, deviceID, anomalyID):
        return Response({anomalyID: get_anomaly(deviceID, anomalyID)})


class EASParametersViewSet(APIView):

    def get(self, request, deviceID, paramID=None):
        data = {}
        eas_parameters = ParametersORM()
        parameters = eas_parameters.get_obj_or_404(doc_id=deviceID)
        paramIDs = [i for i in parameters['parameters'] if parameters['parameters'][i].get('type') == 'built-in']
        parameters['parameters'] = {key: parameters['parameters'][key] for key in parameters['parameters'] if key not in paramIDs}
        if paramID:
            parameter = parameters['parameters'].get(paramID)
            if parameter and parameter['type'] != 'built-in':
                data.update(parameter)
        else:
            data.update(parameters)
        return Response(data)

    def post(self, request, deviceID):
        data = {}
        eas_parameters = ParametersORM()
        _parameters = request.data.get('parameters')
        _paramIDs = [i for i in _parameters if _parameters[i]['type'] == 'built-in']
        _parameters = {key: _parameters[key] for key in _parameters if key not in _paramIDs}
        if _parameters:
            updated = eas_parameters.update(doc_id=deviceID, row_obj={"parameters": _parameters})
            data["updated"] = updated
        return Response(data)
