#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import json
from cmd import Cmd
import readline
import signal
import time
import shutil

sys.path.append("/opt/skyguard/www/app")
SKYGUARD_CLI_ROOT = "/opt/skyguard/app/modules/cli/"
sys.path.append(SKYGUARD_CLI_ROOT)

import utils
import monitoring
import lc_check
from agent_client import AGENT_CLIENT, AGENT_ADDR, AGENT_PORT
from device_time_info import APP_TIMEZONE_TABLE
from redis_client import RedisClient
from sps_client import SPS_CLIENT, SPS_ADDR, SPS_PORT_SSL, CERT_PATH, LICENSE_CERT
from debinterface import interfaces
from common import *
from remote_control import RemoteControl


device_models = ["UCSS", "UCSG-DSG", "", "UCSG-HYBRID", "UCSSLITE", "UCSG-SWG", "UCWI", "", "", "", "UCSSLITE-HYBRID"]

license_product = ["DLP", "SWG", "终端DLP", "终端SWG", "Hybrid DLP", "Hybrid SWG", "Hybrid终端代理服务器", "OCR", "网络打印", "WebService Inspector"]

CLI_TIMEOUT_SECONDS = 300

banned_characters = [';', '&', '|', '<', '>', '`', '$', '(', ')', '{', '}']


def _print_collectlog_menu():
    #clear_screen()
    print u"\n -----------------------------------------"
    print u"|    1) 开始收集日志                      |"
    print u"|    2) 列出已收集的日志                  |"
    print u"|    3) 上传日志                          |"
    print u"|    4) 删除日志                          |"
    print u"|    5) 退出                              |"
    print u" -----------------------------------------"
    return my_prompt("请选择:", options=('1','2','3','4','5'))

def _get_collectlog_history():
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_collectlog_history())
    if resp["responseCode"] != 200:
        print u"获取日志失败"
    else:
        print u"序号\t名字\t\t\t\t\t\t\t大小"
        for i,log_item in enumerate(resp["data"],start=1):
            print i,"\t",log_item["name"],"\t",log_item["size"]

def _start_collectlog():
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    if utils.get_disk_stat()["available"] /1024/1024/1024 < 1:
        print u"空间不足，无法收集"
        return 
    print u"正在收集日志......"
    resp = json.loads(client.start_collectlog())
    if resp["responseCode"] != 200:
        print u"收集日志失败"
    else:
        print u"收集完成:",resp["data"]["name"]

def _upload_collectlog():
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_collectlog_history())
    if resp["responseCode"] != 200:
        print u"获取日志失败"
        return 
    else:
        print u"序号\t名字\t\t\t\t\t\t\t大小"
        for i,log_item in enumerate(resp["data"],start=1):
            print i,"\t",log_item["name"],"\t",log_item["size"]
    seq=my_prompt("请选择要上传的日志序号:", validate_func=_valid_prompt)
    if int(seq) > len(resp["data"]) or int(seq) <=0 :
        print u"请输入正确的日志序号"
        return
    log_id=resp["data"][int(seq)-1]["id"]
    ip=my_prompt("请输入FTP的地址:")
    username=my_prompt("请输入用户名:")
    #password=my_prompt("请输入FTP的密码:")
    import getpass
    password=getpass.getpass("请输入密码:")
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    print u"正在上传......"
    resp = json.loads(client.upload_collectlog(log_id,ip,username,password))
    if resp["resCode"] == 200:
        print u"上传成功"
    elif resp["resCode"] ==401:
        print u"ftp用户名或者密码错误"
    else:
        print u"文件没有找到"

def _delete_collectlog():
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_collectlog_history())
    if resp["responseCode"] != 200:
        print u"获取日志失败"
        return 
    else:
        print u"序号\t名字\t\t\t\t\t\t\t大小"
        for i,log_item in enumerate(resp["data"],start=1):
            print i,"\t",log_item["name"],"\t",log_item["size"]
    seq=my_prompt("请选择要删除的日志序号:", validate_func=_valid_prompt)
    if int(seq) > len(resp["data"]) or int(seq) <=0 :
        print u"请输入正确的日志序号"
        return
    log_id=resp["data"][int(seq)-1]["id"]
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    print u"正在删除......"
    resp = json.loads(client.delete_collectlog(log_id))
    if resp["responseCode"] != 200:
        print u"删除日志失败"
    else:
        print u"删除完成"

def _valid_prompt(data):
    if data == ""  or not data.isdigit():
        return False
    else:
        return True

def _update_nic_mtu(nic_name, mtu_value):
    if nic_name == "lo":
        return u"不能指定lo网卡的MTU"
    if not mtu_value.isdigit():
        return u"请指定MTU值为整数"
    intf = interfaces.Interfaces()
    adapter = intf.getAdapter(nic_name)
    if adapter is None:
        return u"指定的网卡不存在"
    nic_info = adapter.export()
    cmd = "ifconfig %s mtu %s" % (nic_name, str(mtu_value))
    if nic_info.has_key("post-up") and isinstance(nic_info["post-up"], list):
        nic_info["post-up"].append(cmd)
    else:
        nic_info["post-up"] = [cmd]
    intf.writeInterfaces()
    (ret, output) = utils.app_command(cmd)
    if ret == 0:
        return ""
    else:
        print u"设置网卡MTU失败"


def _get_ip_info(type):
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_network_general())
    if resp["responseCode"] != 200:
        return ""
    if type == "address":
        return utils.get_ip_address(str(resp["network_general"]["niccard_name"]))
    elif type == "gateway":
        return str(resp["network_general"]["defaultgw"])
    elif type == "dns":
        ret = ""
        for dns in resp["network_general"]["dns"]:
            ret += str(dns) + "\n"
        return ret
    else:
        return ""


def _get_time_info(type=""):
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_device_time())
    if resp["responseCode"] != 200:
        return ""
    else:
        time_info = str(resp["device_time_info"]["time"])
        tz_index = resp["device_time_info"]["timezone"]
        if type == "date":
            return time_info.split()[0]
        elif type == "time":
            return time_info.split()[1]
        elif type == "timezone":
            for tz in APP_TIMEZONE_TABLE:
                if tz['zone_index'] == tz_index:
                    return tz["timezone"]
            return u"未找到任何时区信息"
        # elif type == "tzlist":
        #     tz_list = []
        #     for tz in APP_TIMEZONE_TABLE:
        #         del tz['zone_index']
        #         tz_list.append(tz)
        #     return tz_list
        else:
            return ""


def _set_time_info(data={}):
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_device_time())
    if resp["responseCode"] != 200:
        return ""
    else:
        update_info = resp["device_time_info"]
        for key in data.keys():
            if key == "date":
                time_info = str(update_info["time"])
                items = time_info.split()
                new_time_info = data.get(key) + " " + items[1]
                update_info["time"] = new_time_info
            elif key == "time":
                time_info = str(update_info["time"])
                items = time_info.split()
                new_time_info = items[0] + " " + data.get(key)
                update_info["time"] = new_time_info
            elif key == "tz":
                update_info["timezone"] = data.get(key)
        config = {"device_time_info": update_info}
        res = client.set_config(config)
        res_json = json.loads(res)
        if res_json["responseCode"] != 200:
            return ""
        else:
            return u"更新成功"


def _set_hostname(new_name):
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    config = {"device_base_info": {"hostname": new_name}}
    res = client.set_config(config)
    res_json = json.loads(res)
    if res_json["responseCode"] != 200:
        return ""
    else:
        return u"更新成功"


def _device_action(type):
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    if type == "reboot":
        action = {"object": "device", "action": "restart"}
    elif type == "shutdown":
        action = {"object": "device", "action": "stop"}
    res = client.system_action(action)
    res_json = json.loads(res)
    if res_json["responseCode"] != 200:
        return ""
    else:
        return u"操作成功"
    pass


def _services_action(type):
    requests = []
    if type == "start":
        action = {"object": "device", "action": "restart"}
    elif type == "stop":
        action = {"object": "device", "action": "stop"}
    elif type == "restart":
        pass

    try:
        client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
        res = client.system_action(requests)
    except Exception, e:
        client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
        res = client.system_action(requests)
    res_json = json.loads(res)
    if res_json["responseCode"] != 200:
        return ""
    else:
        return u"操作成功"


def _get_current_time():
    tnow = int(time.time())
    tnowst = time.localtime(tnow)
    return time.strftime('%Y-%m-%d %H:%M', tnowst)


def _get_license_info():
    redis_client = RedisClient()
    license_sig = redis_client.get(lc_check.redis_key_license_signature, is_json=False)
    if license_sig is not None and license_sig != "":
        license_info = utils.check_license_signature_valid(license_sig, CERT_PATH + LICENSE_CERT)
        if license_info != {} and license_info["deviceId"] == utils.get_device_uuid():
            products = []
            for product in license_info["products"]:
                product_id = product["product"]
                products.append(license_product[product_id-1])
            return license_info["licenseId"], products
        else:
            return "本机license不合法，license is: "+license_info["licenseId"], []
    else:
        return "本机并未指定license", []


def _get_version_info():
    ret = ""
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_information(["device_base_info"]))
    if resp["responseCode"] != 200:
        return ""
    else:
        device_info = resp["device_base_info"]
        ret += "天空卫士 " + device_models[device_info["deviceModel"] - 1] + " Release " + str(
            device_info["version"]) + " 版本\n"
        ret += "CPU:\t\t" + str(device_info["cpucore"]) + "核\n"
        ret += "Memory:\t\t" + str(device_info["memory"]) + "\n"
        ret += "启动时间:\t" + str(device_info["starttime"]) + "\n"
        ret += "当前时间:\t" + _get_current_time() + "\n"
        ret += "型号:\t\t" + device_models[device_info["deviceModel"] - 1] + "\n"
        try:
            license_id, products = _get_license_info()
        except:
            return ret
        ret += "License Key:\t" + str(license_id) + "\n"
        ret += "授权功能:\t" + ", ".join(products) + "\n"
        return ret


def _get_device_info(type):
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_information(["device_base_info"]))
    if resp["responseCode"] != 200:
        return ""
    else:
        device_info = resp["device_base_info"]
        if type == "model":
            return device_models[device_info["deviceModel"] - 1]
        elif type == "hostname":
            return device_info["hostname"]
        elif type == "device-id":
            return device_info["serials"]
        else:
            return ""


def _get_monitoring_info(type):
    if type == "cpu":
        return u"CPU使用率:\t" + str(monitoring.get_cpu_usage()) + "%"
    elif type == "memory":
        mem_used, mem_free, mem_buffer, mem_cached = monitoring.get_memory_current_load()
        return u"内存使用率:\t" + str(mem_used) + "%"
    elif type == "disk":
        disks = monitoring.get_disk_usage_percent()
        ret = ""
        for disk in disks:
            if disk["disk_type"] == "system":
                display = "系统磁盘使用率: " + str(disk["usage_percent"]) + "%\n"
                ret += display
            elif disk["disk_type"] == "data":
                display = "数据磁盘使用率: " + str(disk["usage_percent"]) + "%\n"
                ret += display
        return ret
    else:
        return ""


def _get_services_info():
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_information(["service_status"]))
    if resp["responseCode"] != 200:
        return ""
    else:
        ret = ""
        status_info = resp["service_status"]
        for key in status_info.keys():
            display = "-----" + key + "-----\n"
            mods = status_info.get(key)
            for mod in mods:
                display += str(mod["name"])
                display += ":\t"
                status = "running" if mod["status"] == 0 else "stopped"
                display += status
                display += "\n"
            ret += display
        return ret


def _get_route_info():
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_information(["route_information"]))
    if resp["responseCode"] != 200:
        return ""
    else:
        ret = "目标网络\t子网掩码\t网关\t\t网卡\t类型\n"
        for route in resp["route_information"]["route"]:
            ret += str(route["destination"]) + "\t"
            ret += str(route["netmask"]) + "\t"
            ret += str(route["gateway"]) + "\t"
            if str(route["device"]) == "eth1":
                ret += "MTA\t"
            elif str(route["device"]) == "br0":
                ret += "Br0\t"
            else:
                ret += "Mgmt\t"
            if route["type"] == 1:
                ret += "静态路由"
            else:
                ret += "策略路由"
            ret += "\n"
        return ret


def _get_interface_info():
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_information(["interfaces"]))
    if resp["responseCode"] != 200:
        return ""
    else:
        ret = "名称\tip地址\t\t状态\t模式\t速度\t双工模式\n"
        interfaces = resp["interfaces"]
        for interface in interfaces:
            eth = str(interface["device"])
            if (utils.get_device_type() == 1 or utils.get_device_type() == 5 or utils.get_device_type() == 11) and eth != "eth0":
                continue
            if eth == "eth0":
                ret += "Mgmt\t"
            elif eth == "eth1":
                ret += "MTA\t"
            elif eth == "eth2":
                ret += "P1\t"
            elif eth == "eth3":
                ret += "P2\t"
            elif eth == "br0":
                ret += "BR0\t"
            else:
                ret += "Other\t"

            if str(interface["ip"]) == "":
                ret += "\t\t"
            else:
                ret += str(interface["ip"]) + "\t"
            status = str(interface["action"])
            if status == "enable":
                ret += "已连接\t"
            else:
                ret += "未连接\t"

            mode = str(interface["role"])
            if mode == "monitoring":
                ret += "监控\t"
            elif mode == "bridge":
                ret += "桥接\t"
            else:
                ret += "网络\t"

            if not "unknown" in interface["speed"].lower():
                ret += str(interface["speed"]) + "\t"
                ret += str(interface["duplex"]) + "\n"
            else:
                ret += "\t\n"
        return ret


def _set_route_info(route_type, action, **kwargs):
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    resp = json.loads(client.get_information(["route_information"]))
    if resp["responseCode"] != 200:
        routes_str = ""
    else:
        routes_str = json.dumps(resp["route_information"]["route"])
    if routes_str == "":
        return ""
    routes = json.loads(routes_str)
    route_info = {}
    route_info["type"] = 1 if route_type == "static" else 2
    route_info["destination"] = kwargs["destination"]
    route_info["netmask"] = kwargs["netmask"]
    route_info["gateway"] = kwargs["gateway"]
    route_info["device"] = kwargs["device"]

    if action == "add":
        routes.append(route_info)
    elif action == "del":
        before = len(routes)
        for r in routes:
            if r["type"] == route_info["type"] \
                    and r["destination"] == route_info["destination"] \
                    and r["netmask"] == route_info["netmask"] \
                    and r["gateway"] == route_info["gateway"] \
                    and r["device"] == route_info["device"]:
                routes.remove(r)
                break
        after = len(routes)
        if before == after:
            return u"您要删除的路由并不存在"
    else:
        return ""
    # update routes of device
    client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
    config = {"route_information": {"route": routes}}
    res = client.set_information(config)
    res_json = json.loads(res)
    if res_json["responseCode"] != 200:
        return ""
    else:
        return u"操作成功"


# def _operate_ts_account(action):
#     client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
#     enable = True if action == "enable" else False
#     res = client.enable_remoteControl("ts", enable)
#     res_json = json.loads(res)
#     if res_json["responseCode"] != 200:
#         return ""
#     else:
#         if enable:
#             return u"启用技术支持帐户成功, 六位登录码: " + str(res_json["passcode"])
#         else:
#             return u"禁用技术支持帐户成功"


def _operate_ts_account(action):
    enable = True if action == "enable" else False
    rc = RemoteControl()
    res_json = rc.enable_remote_control("ts", {"enable": enable, "timeout": {"duration": 0}})
    if res_json["responseCode"] != 200:
        return ""
    else:
        if enable:
            return u"启用技术支持帐户成功, 六位登录码: " + str(res_json["passcode"])
        else:
            return u"禁用技术支持帐户成功"


class ApplianceCliTimeOut(Exception):
    """ Custum exception used for timer timeout
    """

    def __init__(self, value="Timed Out"):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ApplianceCli(Cmd, object):
    prompt = "# "

    def __init__(self):
        Cmd.__init__(self)
        self.mytimer(CLI_TIMEOUT_SECONDS)

    def emptyline(self):
        pass

    def default(self, line):
        self.stdout.write('*** 未定义的命令: %s\n' % line)

    def do_help(self, arg):
        if arg:
            # XXX check arg syntax
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc = getattr(self, 'do_' + arg).__doc__
                    if doc:
                        self.stdout.write("%s\n" % str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n" % str(self.nohelp % (arg,)))
                return
            func()
        else:
            device_type = utils.get_device_type()
            if device_type == 1:
                print u'SkyGuard UCSS统一内容安全管理平台控制台命令列表'
            elif device_type == 2:
                print u'SkyGuard UCSG统一内容安全网关控制台命令列表'
            elif device_type == 5:
                print u'SkyGuard UCSS Lite统一内容安全扩展服务器控制台命令列表'
            elif device_type == 7:
                print u'SkyGuard WebService Inspector控制台命令列表'
            elif device_type == 6:
                print u'SkyGuard SWG统一内容安全网关控制台命令列表'
            elif device_type == 11:
                print u'SkyGuard MAG统一内容安全网关控制台命令列表'
            print u"通过help <command>查看使用帮助"
            print "=============================="
            print u"activeOCR           激活OCR"
            print u"backup              备份当前设备配置"
            print u"coredump            开启/关闭/清除coredump"
            print u"date <yyyymmdd>     更新日期"
            print u"disableBonding      关闭网卡绑定"
            #print u"factoryReset        恢复出厂设置"
            print u"firstboot           运行初始化脚本"
            print u"history             查看历史命令"
            print u"hostname <主机名称>  更新主机名称"
            print u"mtu <网卡> <MTU值>   更新网卡的MTU"
            print u"nc                  执行系统nc命令"
            print u"nslookup            执行系统nslookup命令"
            print u"ping                执行系统ping命令"
            print u"quit                退出命令行控制界面"
            print u"reboot              重启主机"
            print u"register <UCSS_IP>  注册当前设备至UCSS (注:UCSS设备无法使用此命令)"
            print u"restore             从备份列表中恢复设备配置"
            print u"route add-policy|del-policy <destination> <netmask> <gateway> <device_type>\t 添加|删除策略路由"
            print u"route add-static|del-static <destination> <netmask> <gateway> <device_type>\t 添加|删除静态路由"
            print u"services            查看/启动/停止DLP服务"
            print u"show cpu            显示CPU使用率"
            print u"show date           显示当前日期"
            print u"show device-id      显示设备ID"
            print u"show disk           显示硬盘使用率"
            print u"show dns            显示DNS"
            print u"show gateway        显示网关"
            print u"show hostname       显示主机名"
            print u"show interface      显示管理口IP, 网关等信息"
            print u"show memory         显示内存使用率"
            print u"show model          显示设备型号"
            print u"show mtu            显示网卡的MTU"
            print u"show route          显示路由信息"
            print u"show time           显示当前时间"
            print u"show timezone       显示当前时区"
            print u"show version        显示系统版本"
            print u"shutdown            关闭主机"
            print u"telnet              执行系统telnet命令"
            print u"time <hh:mm:ss>     更新时间"
            print u"traceroute          执行系统traceroute命令"
            print u"ts <enable>|<disable> 启用|禁用技术支持帐户"
            print u"cleartrustip        删除所有授信地址"
            print u"collectlog        收集日志"
            print u"synctime        立即同步时间"

    def help_introduction(self):
        print u"欢迎使用天空卫士DLP产品命令行控制界面"
        print u"通过help <command>查看使用帮助"

    def onecmd(self, line):
        return super(ApplianceCli, self).onecmd(line)
        # r = super(ApplianceCli, self).onecmd(line)
        # if r and (self.can_quit() or
        #           raw_input('exit anyway ? (yes/no):') == 'yes'):
        #     return True
        # return False

    def do_quit(self, s):
        return True

    def do_exit(self, s):
        return True

    def help_quit(self):
        print u"退出命令行控制界面"

    # do_EOF = do_quit
    # help_EOF = help_quit

    def do_history(self, s):
        for i in range(1, readline.get_current_history_length()):
            print readline.get_history_item(i)

    def do_date(self, paras):
        '''
        date <yyyymmdd> 更新日期
        e.g. date 20160630
        '''
        try:
            args = paras.strip().split()
            if utils.get_device_type() != 1:
                print u"此设备不支持更新日期"
                return
            if len(args) != 1:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            date_str = utils.get_str_match_filter(
                r'(?<!\d)(?:(?:(?:1[6-9]|[2-9]\d)?\d{2})(?:(?:(?:0[13578]|1[02])31)|(?:(?:0[1,3-9]|1[0-2])(?:29|30)))|(?:(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00)))0229)|(?:(?:1[6-9]|[2-9]\d)?\d{2})(?:(?:0?[1-9])|(?:1[0-2]))(?:0?[1-9]|1\d|2[0-8]))(?!\d)',
                args[0])
            if date_str == "" or len(date_str) != 8:
                print u"输入日期格式不合法, 格式应为yyyymmdd"
                return
            else:
                new_date = args[0][:4] + '-' + args[0][4:6] + '-' + args[0][-2:]
                ret = _set_time_info(data={"date": new_date})
                print ret if ret != "" else u"更新日期失败, 请联系技术支持人员"
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message

    def do_time(self, paras):
        '''
        time <hh:mm:ss> 更新时间
        e.g. time 18:30:00
        '''
        try:
            args = paras.strip().split()
            if utils.get_device_type() != 1:
                print u"此设备不支持更新时间"
                return
            if len(args) != 1:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            time_str = utils.get_str_match_filter(r'^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$', args[0])
            if time_str == "":
                print u"输入时间格式不合法, 格式应为hh:mm:ss"
                return
            else:
                ret = _set_time_info(data={"time": args[0]})
                print ret if ret != "" else u"更新时间失败, 请联系技术支持人员"
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message

    def do_hostname(self, paras):
        '''
        hostname <主机名称> 更新主机名称
        '''
        try:
            args = paras.strip().split()
            if len(args) != 1:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            ret = _set_hostname(args[0])
            print ret if ret != "" else u"更新主机名称失败, 请联系技术支持人员"
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message

    def do_reboot(self, paras):
        try:
            args = paras.strip().split()
            if len(args) > 0:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            res = my_prompt(u'请确认是否重启？Y/N(No):'.encode("utf-8"), default='n', options=('y', 'yes', 'n', 'no'))
            if res == 'y' or res == 'yes':
                ret = _device_action("reboot")
                print ret if ret != "" else u"重启失败, 请联系技术支持人员"
            else:
                pass
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message

    def do_shutdown(self, paras):
        try:
            args = paras.strip().split()
            if len(args) > 0:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            res = my_prompt(u'请确认是否关机？Y/N(No):'.encode("utf-8"), default='n', options=('y', 'yes', 'n', 'no'))
            if res == 'y' or res == 'yes':
                ret = _device_action("shutdown")
                print ret if ret != "" else u"关机失败, 请联系技术支持人员"
            else:
                pass
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message

    def do_services(self, paras):
        '''
        services 用于启动/停止DLP服务
        '''
        try:
            args = paras.strip().split()
            if len(args) > 0:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            os.system("python /opt/skyguard/app/modules/cli/service.py")
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message

    def do_firstboot(self, paras):
        '''
        运行初始化脚本
        '''
        try:
            args = paras.strip().split()
            if len(args) > 0:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            os.system("python /opt/skyguard/app/modules/cli/firstboot.py")
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message

    def do_show(self, paras):
        try:
            args = paras.strip().split()
            if len(args) != 1:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            if args[0] == "model" or args[0] == "hostname" or args[0] == "device-id":
                info = _get_device_info(args[0])
                print info if info != "" else u"获取信息失败, 请联系技术支持人员"
            elif args[0] == "cpu" or args[0] == "memory" or args[0] == "disk":
                info = _get_monitoring_info(args[0])
                print info if info != "" else u"获取信息失败, 请联系技术支持人员"
            elif args[0] == "date" or args[0] == "time" or args[0] == "timezone":
                info = _get_time_info(args[0])
                print info if info != "" else u"获取信息失败, 请联系技术支持人员"
            elif args[0] == "route":
                info = _get_route_info()
                print info if info != "" else u"获取路由信息失败, 请联系技术支持人员"
            elif args[0] == "interface":
                info = _get_interface_info()
                print info if info != "" else u"获取interface信息失败, 请联系技术支持人员"
            elif args[0] == "gateway":
                gateway = _get_ip_info("gateway")
                print gateway if gateway != "" else u"获取gateway失败, 请联系技术支持人员"
            elif args[0] == "dns":
                dns = _get_ip_info("dns")
                print dns if dns != "" else u"获取DNS失败, 请联系技术支持人员"
            elif args[0] == "version":
                info = _get_version_info()
                print info if info != "" else u"获取版本信息失败, 请联系技术支持人员"
            elif args[0] == "mtu":
                (ret, output) = utils.app_command("netstat -i | awk -F' ' '{print $1,$2}' | tail -n +3")
                if ret == 0:
                    print output
                else:
                    print u"获取网卡MTU失败, 请联系技术支持人员"
            else:
                print u"输入不合法, 请参考帮助文档"
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message

    def help_show(self):
        print u"show cpu            显示CPU使用率"
        print u"show date           显示当前日期"
        print u"show device-id      显示设备ID"
        print u"show disk           显示硬盘使用率"
        print u"show dns            显示DNS"
        print u"show gateway        显示网关"
        print u"show hostname       显示主机名"
        print u"show interface      显示管理口IP, 网关等信息"
        print u"show memory         显示内存使用率"
        print u"show model          显示设备型号"
        print u"show mtu            显示网卡的MTU"
        print u"show route          显示路由信息"
        print u"show time           显示当前时间"
        print u"show timezone       显示当前时区"
        print u"show version        显示系统版本"

    def show_matches(self, text):
        matches = []
        n = len(text)
        for word in ["gateway", "dns", "cpu", "memory", "date", "device-id", "disk", "domain", "hostname",
                     "interface", "model", "route", "time", "timezone", "version", "mtu"]:
            if word[:n] == text:
                matches.append(word)
        return matches

    def help_mtu(self):
        print u"mtu <nic_name> <mtu_value>"
        print u"使用范例: mtu eth0 1500"

    def do_mtu(self, paras):
        try:
            args = paras.strip().split()
            if len(args) != 2:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            info = _update_nic_mtu(args[0], args[1])
            print info if info != "" else u"设置成功"
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message

    def do_route(self, paras):
        try:
            args = paras.strip().split()
            if utils.get_device_type() == 1 or utils.get_device_type() == 5 or utils.get_device_type() == 11:
                print u"此设备不支持添加和删除路由"
                return
            if len(args) != 5:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            if args[4].lower() != "mgmt" and args[4].lower() != "mta" and args[4].lower() != "br0":
                print u"输入的网卡参数不合法, 应为mgmt/mta/br0中的一项"
                return
            if args[4].lower() == "mta":
                device_nic = "eth1"
            elif args[4].lower() == "br0":
                device_nic = "br0"
            else:
                device_nic = "eth0"
            if args[0] == "add-static":
                info = _set_route_info("static", "add", destination=args[1], netmask=args[2],
                                       gateway=args[3], device=device_nic)
                print info if info != "" else u"添加静态路由失败, 请联系技术支持人员"
                return
            elif args[0] == "del-static":
                info = _set_route_info("static", "del", destination=args[1], netmask=args[2],
                                       gateway=args[3], device=device_nic)
                print info if info != "" else u"删除静态路由失败, 请联系技术支持人员"
                return
            if args[0] == "add-policy":
                info = _set_route_info("policy", "add", destination=args[1], netmask=args[2],
                                       gateway=args[3], device=device_nic)
                print info if info != "" else u"添加策略路由失败, 请联系技术支持人员"
                return
            elif args[0] == "del-policy":
                info = _set_route_info("policy", "del", destination=args[1], netmask=args[2],
                                       gateway=args[3], device=device_nic)
                print info if info != "" else u"删除策略路由失败, 请联系技术支持人员"
                return
            else:
                print u"输入不合法, 请参考帮助文档"
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message

    def help_route(self):
        print u"route add-static <destination> <netmask> <gateway> <device_type>\t 添加静态路由"
        print u"route del-static <destination> <netmask> <gateway> <device_type>\t 删除静态路由"
        print u"route add-policy <destination> <netmask> <gateway> <device_type>\t 添加策略路由"
        print u"route del-policy <destination> <netmask> <gateway> <device_type>\t 删除策略路由"
        print u"<device_type> 支持三种类型: Mgmt MTA Br0"
        print u"使用范例: route add-static 192.168.1.0 255.255.255.0 192.168.1.1 Mgmt"

    def route_matches(self, text):
        matches = []
        n = len(text)
        for word in ["add-static", "del-static", "add-policy", "del-policy"]:
            if word[:n] == text:
                matches.append(word)
        return matches

    def do_ts(self, paras):
        try:
            args = paras.strip().split()
            if len(args) != 1:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            if args[0] == "enable" or args[0] == "disable":
                info = _operate_ts_account(args[0])
                print info if info != "" else u"启用或禁用技术支持帐户失败, 请联系技术支持人员"
            else:
                print u"输入不合法, 请参考帮助文档"
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message

    def help_ts(self):
        print u"ts <enable>|<disable> \t 启用|禁用技术支持帐户"
        print u"技术支持帐户的登录名称为skyguardts, 启用后会返回6位登录码"

    def ts_matches(self, text):
        matches = []
        n = len(text)
        for word in ["enable", "disable"]:
            if word[:n] == text:
                matches.append(word)
        return matches

    def do_cleartrustip(self,paras):
        args = paras.strip().split()
        if len(args) > 0:
            print u"输入参数数目不合法, 请参考帮助文档"
            return
        client = SPS_CLIENT(SPS_ADDR, SPS_PORT_SSL)
        sps_res = client.clear_auth_address()
        if sps_res["responseCode"] == 200:
            print u"删除所有授信地址成功"
        else:
            print u"删除所有授信地址失败"

    def help_cleartrustip(self):
        print u"删除所有的授信地址, 不需要ip地址参数"

    def do_collectlog(self,paras):
        args = paras.strip().split()
        if len(args) > 0:
            print u"输入参数数目不合法, 请参考帮助文档"
            return
        clear_screen()
        while True:
            try:
                choice=_print_collectlog_menu()
                if int(choice) == 1:
                    _start_collectlog()
                elif int(choice) == 2:
                    _get_collectlog_history()
                elif int(choice) == 3:
                    _upload_collectlog()
                elif int(choice) == 4:
                    _delete_collectlog()
                elif int(choice) == 5:
                    break
                else:
                    continue
            except KeyboardInterrupt:
                continue
            except TimeoutError:
                break
    
    def help_collectlog(self):
        print u"日志的收集，查看，上传，删除"

    def do_synctime(self,paras):
        args = paras.strip().split()
        if len(args) > 0:
            print u"输入参数数目不合法, 请参考帮助文档"
            return
        client = AGENT_CLIENT(AGENT_ADDR, AGENT_PORT)
        resp = json.loads(client.synctime_now())
        if resp["responseCode"] == 200:
            print u"同步时间成功"
        else:
            print u"同步时间失败"

    def help_synctime(self):
        print u"立即同步时间"

    def do_register(self, paras):
        '''
        register <UCSS_IP>  注册当前设备至UCSS
                            UCSS设备无法使用此命令
        '''
        if utils.get_device_type() == 1:
            print u'UCSS设备无法使用register命令'
            return
        try:
            args = paras.strip().split()
            if len(args) != 1:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            if utils.get_ipAddr(args[0]) == "":
                print u"输入IP地址不合法, 请重新输入"
                return
            ret = os.system("/opt/skyguard/www/app/register.py %s" % args[0])
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message
            return
        if ret == 0:
            print u"注册成功"
        elif ret == 2:
            pass
        else:
            print u"注册失败"

    def do_backup(self, paras):
        '''
        backup  备份当前设备配置
        '''
        try:
            args = paras.strip().split()
            if len(args) > 0:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            os.system("/opt/skyguard/app/modules/cli/backup.py backup")
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message
            return

    def do_restore(self, paras):
        '''
        restore  从备份列表中恢复设备配置
        '''
        try:
            args = paras.strip().split()
            if len(args) > 0:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            os.system("/opt/skyguard/app/modules/cli/backup.py restore")
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message
            return

    def do_ping(self, paras):
        '''
        ping  执行系统ping命令
        '''
        try:
            os.system("ping " + paras)
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message
            return

    def do_traceroute(self, paras):
        '''
        traceroute  执行系统traceroute命令
        '''
        try:
            os.system("traceroute " + paras)
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message
            return

    def do_nc(self, paras):
        '''
        nc  执行系统nc命令
        '''
        try:
            os.system("nc " + paras)
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message
            return

    def do_nslookup(self, paras):
        '''
        nslookup  执行系统nslookup命令
        '''
        try:
            os.system("nslookup " + paras)
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message
            return

    def do_telnet(self, paras):
        '''
        telnet  执行系统telnet命令
        '''
        try:
            if len(paras) == 0:
                print "Usage: telnet [-4] [-6] [-8] [-E] [-L] [-a] [-d] [-e char] [-l user]\n[-n tracefile] [ -b addr ] [-r] [host-name [port]]\n"
                return
            os.system("telnet " + paras)
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message
            return

    def do_coredump(self, paras):
        '''
        Enable/Disable/Clear coredump
        '''
        try:
            ret = utils.app_command_quiet("python /opt/skyguard/www/app/coredump.py " + paras)
            if ret == 0:
                print u"操作成功"
            elif ret == 1:
                print u"操作失败"
            elif ret == 2:
                print "Usage: coredump enable/disable/clear"
            return
        except Exception, e:
            print u"操作失败"
            return

    def do_activeOCR(self, paras):
        '''
        Enable OCR
        '''
        try:
            ret = utils.app_command_quiet("python /opt/skyguard/www/app/activeOCR.py " + paras)
            if ret == 0:
                print u"激活成功"
            elif ret == 1:
                print u"激活失败"
            elif ret == 2:
                print u"无法连接网络"
            elif ret == 3:
                print "Usage: activeOCR <OCR license>"
            return
        except Exception, e:
            print u"激活失败"
            return 

    def do_disableBonding(self, paras):
        '''
        Disable Nic teaming
        '''
        try:
            args = paras.strip().split()
            if len(args) > 0:
                print u"输入参数数目不合法, 请参考帮助文档"
                return
            os.system("/usr/bin/python /opt/skyguard/app/modules/cli/bonding.py disable")
        except Exception, e:
            print u"执行命令失败, 请联系技术支持人员。错误内容: " + e.message
            return
    '''
    def do_factoryReset(self, paras):
        try:
            res = my_prompt(u'恢复出厂设置将导致所有配置丢失，并自动重启设备，请确认？Y/N(No):'.encode("utf-8"), default='n', options=('y', 'yes', 'n', 'no'))
            if res == 'y' or res == 'yes':
                # Remove new created files
                if os.path.isdir("/etc/trafficserver"):
                    shutil.rmtree("/etc/trafficserver")
                if os.path.isdir("/opt/skyguard/ucs/etc"):
                    shutil.rmtree("/opt/skyguard/ucs/etc")
                if os.path.isfile("/var/lib/redis/dump.rbd"):
                    os.unlink("/var/lib/redis/dump.rbd")
                if os.path.exists("/opt/skyguard/download/blockpage/for_spe_ats"):
                    os.remove("/opt/skyguard/download/blockpage/for_spe_ats")
                    os.system("ln -s /opt/skyguard/download/blockpage/default /opt/skyguard/download/blockpage/for_spe_ats")
                os.system("/usr/bin/redis-cli flushall")
                os.system("update-rc.d -f snmpd remove")
                os.system("update-rc.d -f ssh remove")
                device_type = utils.get_device_type()
                if device_type == 1 or device_type == 5: # UCSS and UCSSLITE restore var partition
                    if not os.path.isfile("/backupvar.tar.gz"):
                        print u"备份文件不存在"
                        return
                    else:
                        os.system("service postgresql stop > /dev/null 2>&1")
                        # Remove new created files
                        if os.path.isdir("/etc/trafficserver"):
                            shutil.rmtree("/etc/trafficserver")
                        if os.path.isdir("/opt/skyguard/ucs/etc"):
                            shutil.rmtree("/opt/skyguard/ucs/etc")
                        if os.path.isfile("/var/lib/redis/dump.rbd"):
                            os.unlink("/var/lib/redis/dump.rbd")
                        if os.path.exists("/opt/skyguard/download/blockpage/for_spe_ats"):
                            os.remove("/opt/skyguard/download/blockpage/for_spe_ats")
                            os.system("ln -s /opt/skyguard/download/blockpage/default /opt/skyguard/download/blockpage/for_spe_ats")
                        os.system("/usr/bin/redis-cli flushall > /dev/null 2>&1")
                        os.system("update-rc.d -f snmpd remove > /dev/null 2>&1")
                        os.system("update-rc.d -f ssh remove > /dev/null 2>&1")
                        os.system("cd / ; tar xfz /backupvar.tar.gz > /dev/null 2>&1")
                if not os.path.isfile("/backup.tar.gz"):
                    print u"备份文件不存在"
                    return
                else:
                    if os.path.isdir("/var/skyguard/sps/"):
                        shutil.rmtree("/var/skyguard/sps/")
                    os.system("cd / ; tar xfz /backup.tar.gz > /dev/null 2>&1")
                #_device_action("reboot")
                if os.path.isfile("/opt/skyguard/www/app/system_backup.py"):
                    os.rename("/opt/skyguard/www/app/system_backup.py", "/opt/skyguard/www/app/system_backup.py.disable")
                os.system("/sbin/reboot")
                return
        except Exception, e:
            print u"恢复出厂设置失败，请联系技术支持人员。错误内容：" + e.message
            return
    '''
    def completedefault(self, text, line, begidx, endidx):
        tokens = line.split()
        if tokens[0].strip() == "show":
            return self.show_matches(text)
        if tokens[0].strip() == "route":
            return self.route_matches(text)
        if tokens[0].strip() == "ts":
            return self.ts_matches(text)
        return []

    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        """

        import readline
        readline.clear_history()
        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey + ": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro) + "\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = raw_input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                        except KeyboardInterrupt:
                            line = '\r\n'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line.rstrip('\r\n')
                self.cleartimer()
                self.mytimer(CLI_TIMEOUT_SECONDS)
                if any(x in line for x in banned_characters):
                    print u'错误的命令'.encode("utf-8")
                else:
                    line = self.precmd(line)
                    stop = self.onecmd(line)
                    stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    def mytimer(self, timeout):
        signal.signal(signal.SIGALRM, self._timererror)
        signal.alarm(timeout)

    def cleartimer(self):
        signal.alarm(0)

    def _timererror(self, signum, frame):
        raise ApplianceCliTimeOut, "ApplianceCli timer timeout"


if __name__ == "__main__":
    cli = ApplianceCli()
    if len(sys.argv) > 1:
        cli.onecmd(' '.join(sys.argv[1:]))
    else:
        cli.cmdloop()
