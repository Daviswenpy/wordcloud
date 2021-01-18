# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-01-25 13:01:38
File Name: utils.py @v4.1
"""
from __future__ import unicode_literals

import os
import sys
import json
import time
import socket
import hashlib
import httplib
import datetime
import commands
import xmlrpclib
import collections
import base64 as b64


def json_print(data, **kwargs):
    print(json.dumps(data, sort_keys=True, indent=4, separators=(', ', ': ')))


def get_ip(request):
    return request.META.get('HTTP_IP', request.META.get('HTTP_X_REAL_IP', request.META.get('REMOTE_ADDR', None)))


# Added by hdu to manapulate iptable
IPTABLES_RULES = "/sbin/iptables -t nat -A PREROUTING -i eth0 -p udp -m udp -s %s --dport %s -j DNAT --to-destination 172.238.238.241:5000 -m comment --comment itp-%s"
FIRSTBOOT_CONF = "/opt/skyguard/itpcli/firstboot.conf"
IPTABLES_RESTORE_FILE = "/opt/skyguard/itpcli/iptables-restore.sh"


def app_command(command, err_exit=False):
    (stat, cmd_output) = commands.getstatusoutput(command)
    if stat:
        if err_exit:
            sys.exit(254)
        return (os.WEXITSTATUS(stat), [cmd_output])
    else:
        return (0, cmd_output.split("\n"))


def returnNotMatches(a, b):
    return [[x for x in a if x not in b], [x for x in b if x not in a]]


def get_itms_port():
    if os.path.isfile(FIRSTBOOT_CONF):
        with open(FIRSTBOOT_CONF) as config_fd:
            config = json.load(config_fd)
        if "port" in config:
            return config["port"]
        else:
            return 514
    else:
        return 514


# action - enable/disalbe deviceId - ucss deviceId logsource - logSource
def update_iptables(action, deviceId, logSource):
    existed_logsource = []
    itms_port = get_itms_port()
    (ret, outputs) = app_command("/sbin/iptables-save | grep itp-%s" % deviceId)
    if outputs[0] is not None and outputs[0] != "":
        for rule in outputs:
            attrs = rule.split(" ")
            if "-s" in attrs:
                existed_logsource.append(attrs[attrs.index("-s") + 1].split("/")[0])
    if action == "enable":
        (added_devices, removed_devices) = returnNotMatches(logSource, existed_logsource)
    elif action == "disable":
        added_devices = []
        removed_devices = existed_logsource
    for device in added_devices:
        os.system(IPTABLES_RULES % (device, str(itms_port), deviceId))
        os.system("echo \"%s\" >> %s" % (IPTABLES_RULES % (device, str(itms_port), deviceId), IPTABLES_RESTORE_FILE))
    for device in removed_devices:
        os.system((IPTABLES_RULES % (device, str(itms_port), deviceId)).replace("-A", "-D"))
        os.system("sed -i \'/%s/d\' %s" % (device, IPTABLES_RESTORE_FILE))
    # flush conntrack table
    os.system("/usr/sbin/conntrack -F conntrack")
    os.system("sed -i \'/conntrack/d\' %s" % IPTABLES_RESTORE_FILE)
    os.system("echo \"/usr/sbin/conntrack -F conntrack\" >> %s" % IPTABLES_RESTORE_FILE)
    return action

# ended Added by hdu


# Added by gaiyongchao to update task xmrpc
ZODIAC_OK = "OK"


class ZodiacTimeoutTransport(xmlrpclib.Transport):
    timeout = 0.5

    def set_timeout(self, timeout):
        self.timeout = timeout

    def make_connection(self, host):
        h = httplib.HTTPConnection(host, timeout=self.timeout)
        return h


class ZodiacClient(object):

    def __init__(self, url):
        t = ZodiacTimeoutTransport()
        t.set_timeout(2)
        self.client = xmlrpclib.ServerProxy(url, transport=t, allow_none=True)

    def add_device(self, device_id):
        return ZODIAC_OK == self.client.add_device(device_id, "async")

    def remove_device(self, device_id):
        return ZODIAC_OK == self.client.remove_device(device_id, "async")

    def update_config(self, device_id):
        return ZODIAC_OK == self.client.update_config(device_id, "async")

    def update_custom_ers_models(self, operate, device_id, modelID_list):
        return ZODIAC_OK == self.client.update_custom_ers_models(operate, device_id, modelID_list, "async")


# ended Added by gaiyongchao


def simple_datetime(t=None, expect_type=str, is_format_str=False, short_format='%Y-%m-%d %H:%M:%S', **replace_field):
    """
    Conversion time with string, int, datetime type.

    Parameters
    ----------
    t : str, datetime, int or float, default None
        Converted time, if `None` is for the current hour.

    expect_type : str, datetime or int, default str
        Expected time type.

    is_format_str : bool, default False
        When returning the string type, choose whether to use "T" and "+0800" formatting.
        e.g. returns "2018-01-01T01:00:00+0800" when `is_format_str=True`.
    replace_field : dict kwargs
        datetime.datetime.replace(self, year=None, month=None, day=None, hour=None,
                                  minute=None, second=None, microsecond=None, tzinfo=True,
                                  *, fold=None)

    Returns
    -------
    out : str, datetime or int
        The time after the conversion.

    Examples
    --------

    >>> simple_datetime("2018-05-14  08:00:00", str)
    Traceback (most recent call last):
    ValueError

    >>> t = simple_datetime("2018-05-24 08:00:00", datetime.datetime)
    >>> simple_datetime(t, str)
    '2018-05-24 08:00:00'

    >>> simple_datetime(t, str, True)
    '2018-05-24T08:00:00+0800'

    >>> simple_datetime(t, int)
    1527120000

    >>> simple_datetime(int(time.mktime(t.timetuple())), str)
    '2018-05-24 08:00:00'

    >>> simple_datetime("2018-07-17 10:00:00", int)
    1531792800

    >>> simple_datetime(expect_type=str, is_format_str=True, minute=0, second=0, microsecond=0) # doctest: +SKIP
    '2019-01-15T17:00:00+0800' # doctest: +SKIP
    """

    def replace_time(t):
        if replace_field:
            zero_t = t.replace(**replace_field)
        else:
            zero_t = t
        return zero_t

    if expect_type not in [str, int, datetime.datetime]:
        raise TypeError

    if isinstance(t, str):
        t = t[:-5] if len(t) == 24 else t
        t = t.replace("T", " ")

        if len(t) != 19:
            raise ValueError

    if t is None:
        date_now = datetime.datetime.now()

        zero_t = replace_time(date_now)

        _t = datetime.datetime.strftime(zero_t, short_format)

    else:
        _t = t

    if isinstance(_t, expect_type):
        # we have a fast-path here.
        # same type
        if expect_type == str and is_format_str:
            _t = _t.replace(" ", "T") + "+0800"
        return _t

    if isinstance(_t, datetime.datetime):
        _t = replace_time(_t)
        if expect_type == int:
            # datetime to int
            return int(time.mktime(_t.timetuple()))
        else:
            # datetime to str
            result = datetime.datetime.strftime(_t, short_format)
            if is_format_str:
                result = result.replace(" ", "T") + "+0800"
            return result

    if isinstance(_t, str):
        __t = datetime.datetime.strptime(_t, short_format)
        __t = replace_time(__t)
        if expect_type == int:
            # str to int
            return int(time.mktime(__t.timetuple()))
        else:
            # str to datetime
            return __t

    if isinstance(_t, (int, float)):
        __t = datetime.datetime.fromtimestamp(int(_t))
        __t = replace_time(__t)
        if expect_type == str:
            # int to str
            result = datetime.datetime.strftime(__t, short_format)
            if is_format_str:
                result = result.replace(" ", "T") + "+0800"
            return result
        else:
            # int to datetime
            return __t


def is_valid_ip(ip):
    """
    Determine whether IP is valid.
    Supports IPv4 and IPv6.

    Parameters
    ----------
    ip : str
        IP string.

    Returns
    -------
    out : bool
        Returns true if the given string is a well-formed IP address.

    Examples
    --------
    >>> is_valid_ip("172.22.22.22")
    True
    >>> is_valid_ip("172.22.22.256")
    False
    >>> is_valid_ip("fec0:0:0:ffff::3%1")
    True
    >>> is_valid_ip("fec0::0:0:ffff::3%1")
    False
    """
    if not ip or '\x00' in ip:
        # Get addr info resolves empty strings to localhost, and truncates on zero bytes.
        return False

    try:
        res = socket.getaddrinfo(ip, 0, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_NUMERICHOST)
        return bool(res)
    except socket.gaierror as e:
        if e.args[0] == socket.EAI_NONAME:
            return False
        raise
    return True


def encrypt(passwd, key):
    """
    encrypt
    """
    key_len = len(key)
    secret = []
    num = 0
    for each in passwd:
        if num >= key_len:
            num = num % key_len
        secret.append(chr(ord(each) ^ ord(key[num])))
        num += 1
    return b64.b64encode("".join(secret).encode()).decode()


def concat_dict(x, y):
    """
    Join two dictionaries with similar structures.
    """
    assert isinstance(x, dict)
    assert isinstance(y, dict)
    for key in x:
        if isinstance(x[key], (int, float, list, str)):
            x[key] = x[key] + y[key]
        if isinstance(x[key], dict):
            if key != "_shards":
                concat_dict(x[key], y[key])
    return x


def gengerate_doc_id(selected_str):
    """
    Using the `selected_str` to compute the document ID.

    Parameters
    ----------
    selected_str : str
        In the fun `bulk_features_and_scores`, use `data["sip"] + str(step) + feature + stand_datetime + deviceID`.
        In the fun `get_score`, use `deviceID + _index + stand_datetime`.
        Encode with utf-8.

    Returns
    -------
    doc_id : hashlib.md5 uuid string.

    Examples
    --------
    # print gengerate_doc_id("2019-01-10T00:00:00+0800" + deviceID + "d4805d42-431d-4c59-b4b6-d28fb7735955" + "ee0e7a4f-5dfc-5240-9aff-ed870fffb615")
    >>> doc_id('python')
    '23eeeb4347bdd26bfc6b7ee9a3b755dd'
    """
    doc_id = hashlib.md5(selected_str.encode("utf-8")).hexdigest()
    return doc_id


def dict_merge(tar_dct, merge_dct, copy_dict=False):
    """
    Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: dct
    """
    if copy_dict:
        import copy
        dct = copy.deepcopy(tar_dct)
    else:
        dct = tar_dct
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
    return dct
