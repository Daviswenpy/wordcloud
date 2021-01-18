#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

SKYGUARD_CLI_ROOT = "/opt/skyguard/itpcli/"
#SKYGUARD_CLI_ROOT = "/root/sgcli/cli/"
sys.path.append(SKYGUARD_CLI_ROOT)
from common import *
import messages
import utils

CLI_EULA_CN_FILE = SKYGUARD_CLI_ROOT + "EULA_CN.txt"
CLI_EULA_EN_FILE = SKYGUARD_CLI_ROOT + "EULA_EN.txt"
FIRSTBOOT_CONF = SKYGUARD_CLI_ROOT + "firstboot.conf"
#EULA_QUESTION = u'\n请确认是否同意所有许可协议内容？Y/N(No):'.encode('utf-8')
EULA_QUESTION = get_message(0x14, messages.lang)

import socket
import fcntl
import struct

import json
import time
from debinterface import interfaces
import shutil
import tempfile
import stat
import os

from netaddr import IPNetwork, IPAddress
import add_user

from OpenSSL import crypto

etc_resolv = "/etc/resolvconf/resolv.conf.d/base"
etc_hostname = "/etc/hostname"
etc_hosts = "/etc/hosts"
ca_file = "/opt/skyguard/itpserver/cert/dlp-intermediate.crt"
ca_key = "/opt/skyguard/itpserver/cert/dlp-intermediate.key"
server_crt = "/opt/skyguard/itpserver/cert/server.pem"
server_key = "/opt/skyguard/itpserver/cert/server.key"
iptable_restore_file = "/opt/skyguard/itpcli/iptables-restore.sh"

def generate_private_key(key_type, bits):
    pkey = crypto.PKey()
    pkey.generate_key(key_type, bits)
    return pkey

def generate_request(pkey, digest="sha256", **name):
    req = crypto.X509Req()
    subj = req.get_subject()
    for key, value in name.items():
        setattr(subj, key, value)
    req.set_pubkey(pkey)
    req.sign(pkey, digest)
    return req

def issue_certificate(cafile, cakey, digest, server_ip):
    private_key = generate_private_key(crypto.TYPE_RSA, 2048)
    csr = generate_request(private_key, digest, CN=server_ip)
    private_key_str = crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key)
    csr_str = crypto.dump_certificate_request(crypto.FILETYPE_PEM, csr)

    with open(cafile) as cafile:
        cafile_str = cafile.read()
    with open(cakey) as cakey:
        cakey_str = cakey.read()

    ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cafile_str)
    ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, cakey_str)
    req_cert = crypto.load_certificate_request(crypto.FILETYPE_PEM, csr_str)
    
    cert = crypto.X509()
    cert.set_subject(req_cert.get_subject())
    cert.set_serial_number(1)
    # before one year ago
    cert.gmtime_adj_notBefore(-31536000)
    # after 10 years
    cert.gmtime_adj_notAfter(315360000)
    cert.set_issuer(ca_cert.get_subject())
    cert.set_pubkey(req_cert.get_pubkey())
    cert.sign(ca_key, digest)
    server_cert_str = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

    with open(server_crt, "w") as server_crt_fd:
        server_crt_fd.write(server_cert_str)
    with open(server_key, "w") as server_key_fd:
        server_key_fd.write(private_key_str)

    os.system("systemctl daemon-reload")
    os.system("systemctl restart itpserver")

def list_available_nic_cards():
        # Only eth0 as management interfaces
        return ['eth0']

def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    except IOError:
        return ""

def set_network(device, ip, netmask, gw):
    intf = interfaces.Interfaces()
    adapter = intf.getAdapter(device)
    nic_info = adapter.export()
    nic_info["addrFam"] = "inet"
    nic_info["auto"] = True
    nic_info["source"] = "static"
    nic_info["address"] = ip
    nic_info["netmask"] = netmask
    nic_info["gateway"] = gw
    adapter.set_options(nic_info)
    intf.writeInterfaces()

    # Kill DHCP client
    os.system("ps -ef | grep dhcp | grep %s | awk '{print $2}' | xargs kill -9" % device)

    os.system("ip addr flush eth0 && systemctl restart networking.service")

    issue_certificate(ca_file, ca_key, "sha256", ip)

def get_nic_status(ifname):
    nic_status_path = "/sys/class/net/%s/operstate" % ifname
    fd = open(nic_status_path)
    status = fd.readline()
    fd.close()
    if status.strip() == "up":
        return "Linked"
    else:
        return "No Link"

def get_network_mask(ifname):
    try:
        return socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 35099, struct.pack('256s', ifname))[20:24])
    except IOError:
        return ""

def validate_ip_address(sIP):
    if len(sIP) < 7:
        return False
    try:
        socket.inet_pton(socket.AF_INET, sIP)
    except socket.error:
        return False

    return True

def validate_gateway_address(gateway, network_set):
    if network_set[0] == network_set[1] and gateway == "":
        return True
    if len(gateway) < 7:
        return False
    try:
        socket.inet_pton(socket.AF_INET, gateway)
    except socket.error:
        return False

    if IPAddress(gateway) in network_set[0]:
        return True
    else:
        return False

def validate_non_empty_input(input_str):
    if len(input_str) > 0:
        return True
    else:
        return False

def validate_port_input(port):
    try:
        if int(port) > 0 and int(port) < 65535:
            return True
        else:
            return False
    except:
        return False

#transform decimal to bin format
def bin(x):
    result = ''
    x = int(x)
    while x > 0:
        mod = x % 2
        x /= 2
        result = str(mod) + result
    if len(result) < 8:
        result = (8-len(result))*'0' + result
    return result

def validate_netmask(sIP):
    if len(sIP) < 7:
        return False
    try:
        maskString = socket.inet_pton(socket.AF_INET, sIP)
    except socket.error:
        return False
    loopNum = 0
    maskstr = ''
    while loopNum < len(maskString):
      #  print  bin(ord(maskString[loopNum]))
        maskstr = maskstr + bin(ord(maskString[loopNum]))
        loopNum = loopNum + 1
    if maskstr.find('0') == -1 or maskstr.find('1') == -1:
        return True
    elif maskstr.index('0') == maskstr.count('1'):
        return True
    else:
        return False

def validate_hostname(hostname):

    import re
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        return False
        #hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))

def validate_ucss_input(ucsshost):
    if validate_ip_address(ucsshost) == True:
        return True
    if validate_hostname(ucsshost) == True:
        return True

    return False

# input multiple dns servers seperated by ','
def validate_dns_server(dns_servers):
    dns_list = dns_servers.split(',')
    for dns in dns_list:
        if validate_ip_address(dns):
            continue
        else:
            return False

    return True

# year-month-day
def validate_date(date):
    try:
        time.strptime(date, '%Y-%m-%d')
    except ValueError:
        return False
    return True

# hour:minute:second
def validate_time(new_time):
    try:
        time.strptime(new_time, '%H:%M:%S')
    except ValueError:
        return False
    return True

def get_default_gateway():
    """Read the default gateway directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            return (fields[0], socket.inet_ntoa(struct.pack("<L", int(fields[2], 16))))
    return (None, None)

def get_dns_server():

    dns_list = []
    f_n = open("/etc/resolv.conf", "r")
    for line in f_n:
        kv = [word.strip() for word in line.split()]
        if len(kv) and kv[0] == "nameserver":
            dns_list.append(kv[1])

    f_n.close()
    return dns_list

def set_dns_server(dnslist):
    #backup ownership and permission
    stres = os.stat(etc_resolv)

    f_n = open(etc_resolv)
    (tmp_fd, tmp_path) = tempfile.mkstemp(prefix="resolv.", dir="/tmp")
    tmp_f = os.fdopen(tmp_fd, "w")
    for line in f_n:
        kv = [word.strip() for word in line.split()]
        if len(kv) and not kv[0] == "nameserver":
            tmp_f.write("%s" % line)
    for dns in dnslist:
        tmp_f.write("nameserver %s\n" % dns)
    tmp_f.close()
    f_n.close()
    shutil.copyfile(tmp_path, etc_resolv)
    os.unlink(tmp_path)

    #restore ownership and permission
    os.chown(etc_resolv, stres[stat.ST_UID], stres[stat.ST_GID])
    os.chmod(etc_resolv, stres[stat.ST_MODE])
    os.system("/sbin/resolvconf -u")

def get_network_general():
    (nic, gw) = get_default_gateway()
    dns = get_dns_server()
    return {"gw" : gw, "nic" : nic, "dns" : dns}

def write_firstboot_conf(modules):
    if os.path.isfile(FIRSTBOOT_CONF):
        with open(FIRSTBOOT_CONF) as config_data:
            config = json.load(config_data)
            config_data.close()
    else:
        config = {}

    for key in modules.keys():
        config[key] = modules[key]
    
    with open(FIRSTBOOT_CONF, 'w') as config_data:
        json.dump(config, config_data, indent=4)
        config_data.close()

def reset_mgmt_interface(ifname, ip, netmask):
    return {"ip" : ip, "netmask" : netmask, "device" : "eth0"}

def save_network_settings_to_conf(ifname, ip, netmask, gateway, niccard, dns):

    dns_list = dns.split(",")
    config= {"interfaces" : reset_mgmt_interface(ifname, ip, netmask), "network_general" : {"defaultgw" : gateway, "niccard_name" : niccard, "dns" : dns_list}}
    write_firstboot_conf(config)
    
def get_hostname():
    return socket.gethostname()

def _parse_hostname(hostname):
    i = hostname.find(".")
    if i < 0:
        return (hostname, None)
    elif (i + 1) == len(hostname):
        return (hostname[0:i], None)
    else:
        return (hostname[0:i], hostname[i + 1:])
def _update_hostname_file(hostname):
    #backup ownership and permission
    stres = os.stat(etc_hostname)

    (tmp_fd, tmp_path) = tempfile.mkstemp(prefix="hostname.", dir="/tmp")
    tmp_f = os.fdopen(tmp_fd, "w")
    tmp_f.write(hostname)
    tmp_f.close()
    shutil.copyfile(tmp_path, etc_hostname)
    os.unlink(tmp_path)

    #restore ownership and permission
    os.chown(etc_hostname, stres[stat.ST_UID], stres[stat.ST_GID])
    os.chmod(etc_hostname, stres[stat.ST_MODE])

def _update_host_file(host, domain):
    #backup ownership and permission
    stres = os.stat(etc_hosts)

    f_n = open(etc_hosts)
    (tmp_fd, tmp_path) = tempfile.mkstemp(prefix="hosts.", dir="/tmp")
    tmp_f = os.fdopen(tmp_fd, "w")
    for line in f_n:
        kv = [word.strip() for word in line.split()]

        if len(kv) and kv[0] == "127.0.0.1":
            if domain:
                tmp_f.write("127.0.0.1\t%s.%s %s localhost.localdomain localhost\n" % (host, domain, host) )
            else:
                tmp_f.write("127.0.0.1\t%s localhost.localdomain localhost\n" % (host) )
        else:
            tmp_f.write("%s" % line)

    tmp_f.close()
    f_n.close()
    shutil.copyfile(tmp_path, etc_hosts)
    os.unlink(tmp_path)

    #restore ownership and permission
    os.chown(etc_hosts, stres[stat.ST_UID], stres[stat.ST_GID])
    os.chmod(etc_hosts, stres[stat.ST_MODE])
    return 0


def set_hostname(hostname):
    (host, domain) = _parse_hostname(hostname)
    #update run time hostname
    os.system("hostname %s" % hostname)

    #update /etc/hostname
    _update_hostname_file(hostname)

    #update /etc/hosts
    _update_host_file(host, domain)

    os.system("/etc/init.d/rsyslog restart > /dev/null 2>&1")

def set_device_time(timestamp):
    # get current time, if the difference is less than 1 min, skip
    tnow = int(time.time())
    tnew = int(time.mktime(time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')))
    if abs(tnew - tnow) < 60:
        return 0
    #os.system("date \'+%%Y-%%m-%%d %%H:%%M:%%S\' -s \"%s\" > /dev/null" % timestamp)
    os.system("timedatectl set-ntp 0; timedatectl set-time \"%s\"" % timestamp)
    os.system("hwclock --systohc")
    os.system("systemctl restart cron")
    os.system("systemctl restart rsyslog")
    return 1

def init_itp_compose():
    initialized = True
    if os.path.isfile("/opt/skyguard/itpimages/itpelk.tar"):
        os.system("docker load < /opt/skyguard/itpimages/itpelk.tar > /dev/null 2>&1")
        os.unlink("/opt/skyguard/itpimages/itpelk.tar")
        initialized = False
    if os.path.isfile("/opt/skyguard/itpimages/itpxrs.tar"):
        os.system("docker load < /opt/skyguard/itpimages/itpxrs.tar > /dev/null 2>&1")
        os.unlink("/opt/skyguard/itpimages/itpxrs.tar")
        initialized = False
    if os.path.isfile("/opt/skyguard/itpimages/itp-kafka.tar"):
        os.system("docker load < /opt/skyguard/itpimages/itp-kafka.tar > /dev/null 2>&1")
        os.unlink("/opt/skyguard/itpimages/itp-kafka.tar")
        initialized = False

    #if initialized == False:
    if True: # restart docker compose for every firstboot
        current_path = os.getcwd()
        os.chdir("/opt/skyguard/itpcompose")
        os.system("docker-compose stop > /dev/null 2>&1")
        os.system("docker-compose up -d > /dev/null 2>&1")
        os.chdir(current_path)

def set_itms_config(itms_config, password):
    #TODO port -> iptables
    os.system("/sbin/iptables -t filter -C FORWARD -d 172.238.238.241/32 -p udp -m udp --dport 5000 -j ACCEPT > /dev/null 2>&1 || /sbin/iptables -t filter -A FORWARD -d 172.238.238.241/32 -p udp -m udp --dport 5000 -j ACCEPT")
    if os.path.isfile(iptable_restore_file):
        os.system("sed -i \'/-t filter/d' %s" % iptable_restore_file)
    os.system("echo \"/sbin/iptables -t filter -A FORWARD -d 172.238.238.241/32 -p udp -m udp --dport 5000 -j ACCEPT\" >> %s" % iptable_restore_file)
    (ret, output) = utils.app_command("/sbin/iptables-save | grep itp-")
    if not output[0] == "":
        port = get_port_from_rule(output[0])
        if not port == itms_config["port"]:
            # remove all nat rules from restore file
            if os.path.isfile(iptable_restore_file):
                os.system("sed -i \'/-t nat/d\' %s" % iptable_restore_file)
            for rule in output:
                utils.app_command("/sbin/iptables -t nat %s" % rule.replace("-A", "-D"))
                new_rule = rule.replace("--dport %d" % port, "--dport %d" % itms_config["port"])
                utils.app_command("/sbin/iptables -t nat %s" % new_rule)
                os.system("echo \"iptables -t nat %s\" >> %s" % (new_rule, iptable_restore_file))
    if not password == "":
        import hashlib
        itm_user = {"username": itms_config["username"].encode("utf-8"), "password": hashlib.sha256(password).hexdigest()}
        add_user.update(**itm_user)
    # create crontab to rotate ES index
    os.system("echo \"13 1 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh network http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" > /etc/cron.d/rotateES")
    os.system("echo \"23 1 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh swg http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"33 1 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh incidentlog http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"43 1 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh dns http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"48 1 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh endpoint http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"53 1 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh aclog http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"58 1 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh ssl http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"10 2 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh ep_dlp http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"15 2 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh ep_others http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"20 2 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh ep_process http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"25 2 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh ep_system http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"30 2 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index.sh ep_systemlog http://172.238.238.239:9200 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    # clean itp results
    os.system("echo \"35 2 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index-ts.sh ers_results http://172.238.238.239:9200 timestamp 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"40 2 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index-ts.sh ers_interval_results http://172.238.238.239:9200 timestamp 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"45 2 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index-ts.sh anomalies_scores http://172.238.238.239:9200 timestamp 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"45 2 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index-ts.sh ars_scores http://172.238.238.239:9200 timestamp 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"45 2 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index-ts.sh ars_result http://172.238.238.239:9200 timestamp 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("echo \"45 2 * * * root bash /opt/skyguard/itpcli/rotate-elasticsearch-index-ts.sh eas_result http://172.238.238.239:9200 timestamp 30 >> /var/log/esrotate.log\" >> /etc/cron.d/rotateES")
    os.system("systemctl restart cron")

    #load docker images and start docker-compose
    init_itp_compose()

def save_hostname_to_conf(hostname):
    config = {"device_base_info" : {"hostname" : hostname}}
    write_firstboot_conf(config)

def save_time_to_conf(date, time):
    time_str = date + " " + time
    config = {"device_time_info" : {"time" : time_str, "ntp" : False}}
    write_firstboot_conf(config)

def get_port_from_rule(rule):
    attrs = rule.split(" ")
    if "--dport" in attrs:
        return int(attrs[attrs.index("--dport") + 1])
    else:
        return 514

def get_itm_conf():
    #TODO get port from iptables
    (ret, output) = utils.app_command("/sbin/iptables-save | grep itp-")
    if not output[0] == "":
        port = get_port_from_rule(output[0])
    else:
        port = 514
    user = add_user.show()
    return {"port" : port, "username" : user["username"]}

def save_itm_to_conf(port, username):
    config = {"itms_config" : {"port" : port, "username" : username.encode("utf-8")}}
    write_firstboot_conf(config)

'''
def get_ip_address(ifname):
    import fcntl
    import struct
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
'''
class Firstboot(object):
    def __init__(self):
        pass

    def run(self):
        # 1. print eula
        self.print_eula()
        res = my_prompt(get_message(0x14, messages.lang), default='n', options=('yes','y','no','n'))
        #res = my_prompt(EULA_QUESTION, default='n', options=('yes','y','no','n'))
        #res = 'y' # Disable eula
        if res == 'y' or res == 'yes':
            # 2. list all nic cards
            nics = self.print_available_nics()
            network_general = get_network_general()
            self.print_network_choices(nics, network_general)
            self.print_device_hostname()
            self.print_time_settings()
            password = self.print_itms_config()
            if self.confirm_settings_input() == True:
                if self.config_appliance_settings(password) == True:
                    print "ITM Server" + get_message(0x17, messages.lang)
                    #print u"ITM Server初始化成功".encode("utf-8")
            #my_prompt(u'\t按回车键返回主菜单'.encode("utf-8"))
            my_prompt("\t"+get_message(0x4e, messages.lang))
            return 0
        else:
            return 0           
 
    def print_eula(self):
        import subprocess
        try:
            clear_screen()
            print_top_banner(get_message(0x1a, messages.lang))
            #print_top_banner("请阅读许可协议")
            if messages.lang == "zh_CN":
                args = ['/usr/bin/python',
                    SKYGUARD_CLI_ROOT + 'python_more.py',
                    CLI_EULA_CN_FILE]
            else:
                args = ['/usr/bin/python',
                    SKYGUARD_CLI_ROOT + 'python_more.py',
                    CLI_EULA_EN_FILE]
            co = subprocess.Popen(args)
            (output, errstr) = co.communicate()
            res = co.wait()
        except:
            if co:
                co.terminate()
                utils.app_command_quiet("/bin/stty -F /dev/tty echo")
                utils.app_command_quiet("/bin/stty -F /dev/tty -cbreak")

    def print_available_nics(self):
        clear_screen()
        print_top_banner(get_message(0x1b, messages.lang) % (1, 6))
        #print_top_banner("(第1步，共6步)")
        print '    ' + get_message(0x1c, messages.lang)
        #print u'    任何状态下按(Ctrl+C)键退回到主菜单\n'.encode("utf-8")
        nics = list_available_nic_cards()
        nics_info = []
        order = 1
        for nic in nics:
            info = {}
            info["ifname"] = nic
            info["status"] = get_nic_status(nic)
            if info["status"] == "Linked":
                info["ip"] = get_ip_address(nic)
                info["netmask"] = get_network_mask(nic)
            else:
                info["ip"] = ""
                info["netmask"] = ""
            info["order"] = order
            nics_info.append(info)
            order = order + 1
        for nic in nics_info:
            print "%d. %s(%s): %s\n" % (nic["order"], nic["ifname"], nic["ip"], nic["status"])

        return nics_info
 
    def print_network_choices(self, nics, network_general):
        while True:
            list = range(1, len(nics) + 1)
            options = tuple([format(x,'d') for x in list])
#            res = my_prompt(u'选择要配置的网卡 1-%d (1):'.encode("utf-8") % len(nics), default="1", options=options)
            res = 1
            for nic in nics:
                if nic["order"] == int(res):
                    ip = my_prompt(get_message(0x1d, messages.lang) + '(%s):'% nic["ip"], default=nic["ip"], validate_func=validate_ip_address)
                    netmask = my_prompt(get_message(0x1e, messages.lang) + '(%s):' % nic["netmask"], default=nic["netmask"], validate_func=validate_netmask)
                    #ip = my_prompt(u'IP地址(%s):'.encode("utf-8") % nic["ip"], default=nic["ip"], validate_func=validate_ip_address)
                    #netmask = my_prompt(u'掩码(%s):'.encode("utf-8") % nic["netmask"], default=nic["netmask"], validate_func=validate_netmask)
                    network = IPNetwork(ip+'/'+netmask)
                    if nic["ip"] == "" or nic["netmask"] == "":
                        network_old = IPNetwork("0.0.0.0/0.0.0.0")
                    else:
                        network_old = IPNetwork(nic["ip"]+'/'+nic["netmask"])
                    gateway = my_prompt(get_message(0x1f, messages.lang) + '(%s):' % network_general['gw'].encode("utf-8"), validate_func=validate_gateway_address, args=(network, network_old))
                    #gateway = my_prompt(u'网关(%s):'.encode("utf-8") % network_general['gw'], validate_func=validate_gateway_address, args=(network, network_old))
                    if gateway == "":
                        # Do not change gateway if it doesn't change
                        gateway = str(network_general['gw'])
                        niccard = str(network_general['nic'])
                    else:
                        niccard = "eth0"
                    dns_server = ""
                    for dns in network_general["dns"]:
                        if dns_server == "":
                            dns_server = str(dns)
                        else:
                            dns_server = dns_server + ',' + str(dns)
                    #dns = my_prompt(u'DNS服务器(%s):'.encode("utf-8") % dns_server, default=dns_server, validate_func=validate_dns_server)
                    dns = my_prompt(get_message(0x20, messages.lang) + '(%s):' % dns_server, default=dns_server, validate_func=validate_dns_server)
                    #print ip, netmask, gateway, dns
                    '''
                    print u'\n请确认您当前的网络配置信息：'.encode("utf-8")
                    print u'管理网卡: %s'.encode("utf-8") % nic['ifname']
                    print u'IP地址: %s'.encode("utf-8") % ip
                    print u'掩码: %s'.encode("utf-8") % netmask
                    print u'网关: %s'.encode("utf-8") % gateway
                    print u'DNS服务器: %s'.encode("utf-8") % dns
                    res = my_prompt(u'请确认是否保存这些配置？Y/N(No):'.encode("utf-8"), default='n', options=('y', 'yes', 'n', 'no'))
                    '''
                    print '\n' + get_message(0x21, messages.lang)
                    print get_message(0x22, messages.lang) + '%s' % nic['ifname']
                    print get_message(0x1d, messages.lang) + ':%s' % ip
                    print get_message(0x1e, messages.lang) + ':%s' % netmask
                    print get_message(0x1f, messages.lang) + ':%s' % gateway
                    print get_message(0x20, messages.lang) + ':%s' % dns
                    res = my_prompt(get_message(0x23, messages.lang), default='n', options=('y', 'yes', 'n', 'no'))
                    if res == 'y' or res == 'yes':
                        save_network_settings_to_conf(nic['ifname'], ip, netmask, gateway, niccard, dns)
                        return 0
                    else:
                        # TODO reconfig network settings
                        self.print_available_nics()
                        break

    def print_device_hostname(self):
        while True:
            clear_screen()
            print_top_banner(get_message(0x1b, messages.lang) % (2, 6))
            #print_top_banner(u'(第2步 共6步)'.encode("utf-8"))
            #print u'    任何状态下按(Ctrl+C)键退回到主菜单\n'.encode("utf-8")
            #print u'修改主机名称'.encode("utf-8")
            print '    ' + get_message(0x1c, messages.lang)
            print get_message(0x24, messages.lang)
            old_hostname = get_hostname()
            '''
            hostname = my_prompt(u'主机名(%s):'.encode("utf-8") % old_hostname, default=old_hostname, validate_func=validate_hostname)
            print u'您输入的主机名称：'.encode("utf-8")
            print u'主机名: %s'.encode("utf-8") % hostname
            res = my_prompt(u'请确认是否变更主机名称？Y/N(No):'.encode("utf-8"), default='n', options=('y', 'yes', 'n', 'no'))
            '''
            hostname = my_prompt(get_message(0x25, messages.lang) + '(%s):' % old_hostname, default=old_hostname, validate_func=validate_hostname)
            print get_message(0x26, messages.lang)
            print get_message(0x25, messages.lang) + ':%s' % hostname
            res = my_prompt(get_message(0x27, messages.lang), default='n', options=('y', 'yes', 'n', 'no'))
            if res == 'y' or res == 'yes':
                save_hostname_to_conf(hostname)
                return 0
            else:
                # TODO reconfig hostname
                continue

    def print_time_settings(self):
        while True:
            clear_screen()
            print_top_banner(get_message(0x1b, messages.lang) % (3, 6))
            print '    ' + get_message(0x1c, messages.lang)
            #print_top_banner(u'(第3步 共6步)'.encode("utf-8"))
            #print u'    任何状态下按(Ctrl+C)键退回到主菜单\n'.encode("utf-8")
            tnow = int(time.time())
            tnowst = time.localtime(tnow)
            current_date = time.strftime('%Y-%m-%d', tnowst)
            current_time = time.strftime('%H:%M:%S', tnowst)

            '''
            print u'当前日期: %s'.encode("utf-8") % current_date
            new_date = my_prompt(u'请输入新的日期，格式(年-月-日)：'.encode("utf-8"), default=current_date, validate_func=validate_date)

            print u'\n当前时间: %s'.encode("utf-8") % current_time
            new_time = my_prompt(u'请输入新的时间，格式(时:分:秒)：'.encode("utf-8"), default=current_time, validate_func=validate_time)

            res = my_prompt(u'请确认是否变更日期时间？Y/N(No):'.encode("utf-8"), default='n', options=('y','yes','n','no'))
            '''
            print get_message(0x28, messages.lang)+ '%s' % current_date
            new_date = my_prompt(get_message(0x29, messages.lang), default=current_date, validate_func=validate_date)

            print get_message(0x2a, messages.lang) + '%s' % current_time
            new_time = my_prompt(get_message(0x2b, messages.lang), default=current_time, validate_func=validate_time)

            res = my_prompt(get_message(0x2c, messages.lang), default='n', options=('y','yes','n','no'))
            if res == 'y' or res == 'yes':
                save_time_to_conf(new_date, new_time)
                return 0
            else:
                # TODO reconfig time settings
                continue

    def print_itms_config(self):
        while True:
            clear_screen()
            print_top_banner(get_message(0x1b, messages.lang) % (4, 6))
            print '    ' + get_message(0x1c, messages.lang)
            #print_top_banner(u'(第4步 共6步)'.encode("utf-8"))
            #print u'    任何状态下按(Ctrl+C)键退回到主菜单\n'.encode("utf-8")
            print get_message(0x186, messages.lang) + "\n"
            #print u'请配置ITM服务器\n'.encode("utf-8")
            itm_conf = get_itm_conf()
            port = my_prompt(get_message(0x189, messages.lang) % itm_conf["port"], default=itm_conf["port"], validate_func=validate_port_input)
            username = my_prompt(get_message(0x18a, messages.lang) % itm_conf["username"].encode("utf-8"), default=itm_conf["username"].encode("utf-8"))
            #port = my_prompt(u'服务端口(%d)：'.encode("utf-8") % itm_conf["port"], default=itm_conf["port"], validate_func=validate_port_input)
            #username = my_prompt(u'用户名(%s)：'.encode("utf-8") % itm_conf["username"].encode("utf-8"), default=itm_conf["username"].encode("utf-8"))
            #password = input_password(u'密码：'.encode("utf-8"), 16)
            password = input_password(get_message(0x02, messages.lang), 16)
            while password == "" and (not username == itm_conf["username"].encode("utf-8")):
                print get_message(0x188, messages.lang)
                #print u'密码不能为空，请重新输入'.encode("utf-8")
                password = input_password(get_message(0x02, messages.lang), 16)
                #password = input_password(u'密码：'.encode("utf-8"), 16)
            #password_confirm = input_password(u'确认密码：'.encode("utf-8"), 16)
            password_confirm = input_password(get_message(0x03, messages.lang), 16)
            while password != password_confirm:
                print get_message(0x2e, messages.lang)
                password = input_password(get_message(0x02, messages.lang), 16)
                password_confirm = input_password(get_message(0x03, messages.lang), 16)
                '''
                print u'两次密码输入不同，请重新输入'.encode("utf-8")
                password = input_password(u'密码：'.encode("utf-8"), 16)
                password_confirm = input_password(u'确认密码：'.encode("utf-8"), 16)
                '''
            res = my_prompt(get_message(0x187, messages.lang), default='n', options=('y','yes','n','no'))
            if res == 'y' or res == 'yes':
                save_itm_to_conf(int(port), username)
                return password
            else:
                continue

    def confirm_settings_input(self):
        clear_screen()
        '''
        print_top_banner(u'(第5步 共6步)'.encode("utf-8"))
        print u'    任何状态下按(Ctrl+C)键退回到主菜单\n'.encode("utf-8")
        '''
        print_top_banner(get_message(0x1b, messages.lang) % (5, 6))
        print '    ' + get_message(0x1c, messages.lang)

        with open(FIRSTBOOT_CONF) as config_data:
            config = json.load(config_data)

        print get_message(0x30, messages.lang)
        print '1)' + get_message(0x31, messages.lang)
        mgmt_nic_setting = config["interfaces"]
        print get_message(0x32, messages.lang) + '%s' % str(mgmt_nic_setting["device"])
        print '\t' + get_message(0x33, messages.lang) + '%s' % str(mgmt_nic_setting["ip"])
        print '\t' + get_message(0x34, messages.lang) + '%s' % str(mgmt_nic_setting["netmask"])
        network_general = config["network_general"]
        print '\t' + get_message(0x35, messages.lang) + '%s' % str(network_general["defaultgw"])
        dns_list = ""
        for dns in network_general["dns"]:
            if dns_list == "":
                dns_list = dns_list + str(dns)
            else:
                dns_list = dns_list + "," + str(dns)
        print '\t' + get_message(0x20, messages.lang) + ':%s' % dns_list

        hostname = str(config["device_base_info"]["hostname"])
        print '2)' + get_message(0x25, messages.lang) + ':%s' % hostname

        current_time = str(config["device_time_info"]["time"])
        print '3)' + get_message(0x36, messages.lang) + '%s' % current_time

        itms_config = config["itms_config"]
        print '4)' + get_message(0x18b, messages.lang) + ":"
        print '\t' + get_message(0x3d, messages.lang) + '%d:' % itms_config['port']
        print '\t' + get_message(0x01, messages.lang) + '%s:' % itms_config['username'].encode("utf-8")
        print '\t' + get_message(0x02, messages.lang) + '******'

        # added by wendong, compatible with ver 3.3
        ucss_33 = "/opt/skyguard/itpserver/ucss_3.3"
        res_ver = my_prompt(get_message(0x18c, messages.lang), default='n', options=('y','yes','n','no'))
        if res_ver == 'y' or res_ver == 'yes':
            f = open(ucss_33, "w")
            f.close()
        else:
            if os.path.exists(ucss_33):
                os.remove(ucss_33)

        res = my_prompt(get_message(0x184, messages.lang), default='n', options=('y','yes','n','no'))
        '''
        print u'初始化信息确认：'.encode("utf-8")
        print u'1)网络配置：'.encode("utf-8")
        mgmt_nic_setting = config["interfaces"]
        print u'\t管理网卡名称：%s'.encode("utf-8") % str(mgmt_nic_setting["device"])
        print u'\t管理网卡IP地址： %s'.encode("utf-8") % str(mgmt_nic_setting["ip"])
        print u'\t管理网卡掩码： %s'.encode("utf-8") % str(mgmt_nic_setting["netmask"])
        network_general = config["network_general"]
        print u'\t默认网关： %s'.encode("utf-8") % str(network_general["defaultgw"])
        dns_list = ""
        for dns in network_general["dns"]:
            if dns_list == "":
                dns_list = dns_list + str(dns)
            else:
                dns_list = dns_list + "," + str(dns)

        print u'\tDNS服务器： %s'.encode("utf-8") % dns_list

        hostname = str(config["device_base_info"]["hostname"])
        print u'2)主机名称： %s'.encode("utf-8") % hostname

        current_time = str(config["device_time_info"]["time"])
        print u'3)日期时间： %s'.encode("utf-8") % current_time

        itms_config = config["itms_config"]
        print u'4)ITM服务器配置：'.encode("utf-8")
        print u'\t服务端口：%d'.encode("utf-8") % itms_config['port']
        print u'\t用户名：%s'.encode("utf-8") % itms_config['username'].encode("utf-8")
        print u'\t密码：******'.encode("utf-8")

        res = my_prompt(u'请确认是否保存变更？Y/N(No)'.encode("utf-8"), default='n', options=('y','yes','n','no'))
        '''
        if res == 'y' or res == 'yes':
            return True
        else:
            return False

    def config_appliance_settings(self, password):
        #TODO
        clear_screen()
        print_top_banner(get_message(0x1b, messages.lang) % (6, 6))
        print '    ' + get_message(0x1c, messages.lang)
        #print_top_banner(u'(第6步 共6步)'.encode("utf-8"))
        #print u'    任何状态下按(Ctrl+C)键退回到主菜单\n'.encode("utf-8")

        #print u'描述：\n\t配置中...'.encode("utf-8")
        print get_message(0x0b, messages.lang) + '\n\t' + get_message(0x44, messages.lang)
        with open(FIRSTBOOT_CONF) as config_data:
            config = json.load(config_data)
        set_network("eth0", config["interfaces"]["ip"], config["interfaces"]["netmask"], config["network_general"]["defaultgw"])
        set_dns_server(config["network_general"]["dns"])
        set_hostname(config["device_base_info"]["hostname"])
        set_device_time(config["device_time_info"]["time"])
        set_itms_config(config["itms_config"], password)
        return True

if __name__ == "__main__":
    try:
        cls = Firstboot()
        cls.run()
    except KeyboardInterrupt:
        pass
