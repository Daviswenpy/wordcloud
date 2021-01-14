# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2019-02-19 16:20:21
File Name: comuserinfobackend.py @v2.1
"""
from IPy import IP
import requests as req
from functools import partial
from requests.auth import HTTPBasicAuth

from django.utils.translation import ugettext_lazy as _

from config import config
from utils import is_valid_ip


req.packages.urllib3.disable_warnings()


__all__ = ['UserInfo']


class _UserInfo(object):
    """
    Get user information from userservice.

    Attributes
    ----------
    auth : HTTPBasicAuth
        The default authentication method.
    uus_url : str, default '{url}search/users_uuid/{deviceID}'
        User service full url.
        '{url}search/users_uuid/{deviceID}' for search user.
        '{url}search/users_uuid/{deviceID}' for get all users information.

    Examples
    --------
    In the test environment.

    Code initialization.
    >>> deviceID = "6a6887d4-b195-7ceb-f1d3-4d66eaf164a9"
    >>> user_service_url = 'https://172.22.111.247:5001/'
    >>> us = _UserInfo(deviceID=deviceID, url=user_service_url, timeout=10)

    Search all user logonName and userId mappings.
    >>> us.get_user_map() # doctest: +SKIP
    ... # doctest: +SKIP

    Search users based on logonName expressions.
    >>> us.get_user_info("*lianpengcheng", "by_username")
    ['ee0e7a4f-5dfc-5240-9aff-ed870fffb615']

    Search users based on full logonName.
    >>> us.get_user_info("skyguardmis.com\\zhaomingjun", "by_username")
    ['fc4824a3-189f-514b-831a-e51515406bca']

    Search all userId lists in a group or ou.
    >>> us.get_user_info("c67d6169-eab0-bc47-85b7-570b6ff5882a", "by_group_uuid") # doctest: +SKIP +REPORT_NDIFF
    ['f9e141e0-063f-8b44-acb8-74fda347cef8', 'ea3679a6-0dea-3349-a025-b89b5b31d580',
    '8e79e4e9-7612-f148-98d3-d7a348ad28f2', 'f9e927ad-067a-f142-8b62-f9f9d984de0c',
    'ac3f7edd-02d8-7e4e-8765-27b75aec8b60', '239871d4-3b56-bb4c-82ef-6197da179073',
    'fc4824a3-189f-514b-831a-e51515406bca', '4378602c-e669-ef4e-905d-3ed40b5e616d',
    '2022f708-f4b4-1941-afb4-cb6c3d5dd908', 'cce59f8e-8015-b04f-b2f8-a8c549783aa6',
    'f8208f11-a7af-d940-9e3c-1be9f8940f74', 'ee0e7a4f-5dfc-5240-9aff-ed870fffb615']

    Note
    ----
    Returns a null value of the corresponding type if an exception occurs.
    """

    def __init__(self, url=None, deviceID=None, timeout=10):
        """
        Parameters
        ----------
        url : str
            User service url, must end with a backslash. eg: 'https://172.22.111.247:5001/'.
        deviceID : str
            Device ID.
        timeout : int, float, default 10
            Request timeout.
        """
        self.uus_url = "{}search/users_uuid/{}".format(url, deviceID)
        self.timeout = timeout
        self.auth = HTTPBasicAuth('search', 'search_pass')

    def get_user_map(self):
        """
        Returns
        -------
        out : dict
            Return the dict of the relationship between the userId and logonName, just like {"userId1": "logonName1"}.
        """
        try:
            response = req.get(self.uus_url + '/useridmap/all', auth=self.auth, verify=False, timeout=self.timeout).json()
        except:
            response = {}
        return response

    def get_user_info(self, keyword='*', query_type='by_username'):
        """
        Parameters
        ----------
        keywork : str, default '*'
            Keyword for query search, it can be full logonName, logonName re expressions or group_uuid.
        query_type : {default 'by_username', 'by_group_uuid'}, optional
            If query_type invalid, raise ValueError.

        Returns
        -------
        out : list
            Default returns all users list in gruop or ou, just like ["userId1", "userId2"].
        """
        if query_type not in ['by_username', 'by_group_uuid']:
            raise ValueError(_("Invalid value for 'query_type' parameter, valid options are: by_username, by_group_uuid"))
        data = {"query_type": query_type, "query_string": keyword}
        try:
            response = req.post(self.uus_url, auth=self.auth, json=data, verify=False, timeout=self.timeout).json()
        except:
            response = []
        return response


UserInfo = partial(_UserInfo, config.USER_SERVICE)


class ResolveBlacklist(object):
    """
    Resolve blacklist
    """

    def __init__(self, deviceID, blacklist):
        self.res = []
        self._us_client = UserInfo(deviceID=deviceID)
        for i in range(1, 5 + 1):
            sub = [sub['value'] for sub in blacklist if sub['type'] == i][0]
            if sub == []:
                self.res.append(sub)
            else:
                self.res.append(eval('self.sub_' + str(i))(sub))

    def sub_1(self, sub):
        return list(set([ip for ip in sub if is_valid_ip(ip)]))

    def sub_2(self, sub):
        return [[str(IP(ips)[0]), str(IP(ips)[-1])] if '/' in ips else ips.split('-') for ips in sub]

    def sub_3(self, sub):
        res = []
        for i in sub:
            res += self._us_client.get_user_info(keyword=i, query_type='by_username')
        return res

    def sub_4(self, sub):
        return sub

    def sub_5(self, sub):
        res = []
        for i in sub:
            res += self._us_client.get_user_info(keyword=i, query_type='by_group_uuid')
        return res

    @property
    def ip(self):
        return self.res[0]

    @property
    def iprange(self):
        return self.res[1]

    @property
    def users(self):
        return list(set(self.res[2] + self.res[3] + self.res[4]))

    @property
    def ip_query(self):
        return [{"terms": {'sourceIp': self.ip}}] if self.ip != [] else []

    @property
    def iprange_query(self):
        return [{"range": {'sourceIp': {"gte": i[0], "lte": i[1]}}} for i in self.iprange]

    @property
    def users_query(self):
        return [{'terms': {'userId.keyword': self.users}}]

    @property
    def blacklist_query(self):
        return self.ip_query + self.iprange_query + self.users_query

    def get_user_and_blacklist_query(self, group_id):
        group_id = None if "not" in group_id else group_id

        if group_id:
            group_user_list = self._us_client.get_user_info(keyword=group_id, query_type='by_group_uuid')
            filter_group_user_list = list(set(group_user_list).difference(self.users))
            user_query = [{'terms': {'userId.keyword': filter_group_user_list}}]
        else:
            user_query = []
        blacklist_query = self.blacklist_query
        return user_query, blacklist_query


def get_must_list(must):
    must_list = [
        {"type": 1, "value": []},
        {"type": 2, "value": []},
        {"type": 3, "value": []},
        {"type": 4, "value": []},
        {"type": 5, "value": []}
    ]
    for i in must:
        for j in [3, 4, 5]:
            if i["type"] == j:
                must_list[j - 1]["value"] = i["value"]
    return must_list


def get_filter_query(deviceID, must):
    if must == [{"type": 3, "value": ["*"]}]:
        return []
    must_list = get_must_list(must)
    rb = ResolveBlacklist(deviceID, must_list)
    _, must_query = rb.get_user_and_blacklist_query("not")
    return must_query


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)
    import pydoc
    pydoc.doc(_UserInfo)
