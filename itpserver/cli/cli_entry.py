#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import getpass
import spwd
import crypt
import sys

SKYGUARD_CLI_ROOT = "/opt/skyguard/app/modules/cli/"
#SKYGUARD_CLI_ROOT = "/root/sgcli/cli"
sys.path.append(SKYGUARD_CLI_ROOT)
from common import *
import firstboot
import time


def is_remote_loggin(user_name):
    stat, output = app_command("who")
    if stat == 0:
        for line in output:
            if line.find("pts") != -1 and line.find(user_name) != -1:
                return True
        return False
    else:
        return False

def print_login_page():
    try:
        print_top_banner()
        username = raw_input(get_message(0x01, messages.lang))
        #username = raw_input(u'用户名：'.encode('utf-8'))    
        if username != "itmadmin":
            print get_message(0x04, messages.lang)
            #print u'无效的用户名'.encode('utf-8')
            time.sleep(3)
            raise EOFError
        #password = getpass.getpass(u'密码：'.encode('utf-8'))
        password = getpass.getpass(get_message(0x02, messages.lang))
        return (username, password)
    except (KeyboardInterrupt, EOFError):
        return (None, None)
        #sys.exit(0)

def reset_password(device_type):
    print u'请将下面的编码提供给SkyGuard技术支持获取密钥'.encode('utf-8')
    passcode = utils.generate_random_str(6)
    print u'编码：%s'.encode('utf-8') % passcode
    password = getpass.getpass(u'密钥：'.encode('utf-8'))
    real_password = utils.password_hashing(utils.encode(passcode))[:8]
    if device_type == 1 or device_type == 5 or device_type == 11:
        adminuser = "ucssadmin"
        device = "UCSS"
    else:
        adminuser = "ucsgadmin"
        device = "UCSG"
    if password == real_password:
        print u'\n请输入新的%s密码'.encode('utf-8') % adminuser
        password = input_password(u'密码：'.encode("utf-8"), 16)
        password_confirm = input_password(u'确认密码：'.encode("utf-8"), 16)
        while password != password_confirm:
            print u'两次密码输入不同，请重新输入'.encode("utf-8")
            password = input_password(u'密码：'.encode("utf-8"), 16)
            password_confirm = input_password(u'确认密码：'.encode("utf-8"), 16)

        if password != "":
            utils.app_command_quiet('echo "%s:%s" | chpasswd' % (adminuser, password))
        print_top_banner(u'密码重置成功'.encode('utf-8'))
        print u'描述：'.encode('utf-8')
        print u'\t%s设备密码已经重置完成，请按任意键返回登录界面尝试使用新的密码登录。'.encode('utf-8') % device
        print u'----------密码重置成功---------\n'.encode("utf-8")
        my_prompt(u'\t按回车键返回主菜单'.encode("utf-8"))


def auth_admin(username, password):
    cryptedpasswd = spwd.getspnam(username)[1]

    if crypt.crypt(password, cryptedpasswd) == cryptedpasswd:
        return True
    else:
        return False
 
def print_menu():
    clear_screen()
    print_top_banner()
    print "1) " + get_message(0x10, messages.lang) + "\n"
    print "2) " + get_message(0x12, messages.lang) + "\n"
#    print "1) 初始化\n"
#    print "2) 退出\n"

    print DASH_INTERRUPTER % ''
    return my_prompt(get_message(0x13, messages.lang), default='1', options=('1','2'))

def run_firstboot():
    cls = firstboot.Firstboot()
    cls.run()
    pass

def run_cli(userconf):
    clear_screen()
    print_top_banner(u'命令控制台'.encode("utf-8"))

    from appliance_cli import ApplianceCli, ApplianceCliTimeOut
    try:
        cli = ApplianceCli()
        cli.cmdloop()
    except (KeyboardInterrupt, EOFError):
        sys.stdout.write('\nExited on user request\n')
    except ApplianceCliTimeOut:
        sys.stdout.write('\nTime is up.\n')

def disable_complete(text, status):
    return None

def disable_auto_complete():
    import readline
    readline.set_completer(disable_complete)

def choose_language():
    clear_screen()
    print_top_banner()

    print "请选择语言:\n"
    print "1) 中文\n"
    print "2) English\n"

    lang_index = my_prompt(get_message(0x13, messages.lang), default='1', options=('1','2'))
    if lang_index == '1':
        lang = "zh_CN"
    elif lang_index == '2':
        lang = "en"

    #utils.app_conf_write({"firstboot_language" : lang})
    messages.lang = lang
    return lang

if __name__ == "__main__":
    disable_auto_complete()
    username = "itmadmin"

    lang = choose_language()
    if is_remote_loggin(username):
        while True:
            try:
                function = print_menu()
                if int(function) == 1:
                    run_firstboot()
                elif int(function) == 2:
                    sys.exit(0)
                else:
                    continue
            except KeyboardInterrupt:
                continue
            except TimeoutError:
                break
    else:
        while True:
            clear_screen()
            (username, password) = print_login_page()
            if password == None:
                continue
            # Pass authentication
            if auth_admin(username, password) == True:
                while True:
                    try:
                        function = print_menu()
                        if int(function) == 1:
                            run_firstboot()
                        elif int(function) == 2:
                            sys.exit(0)
                        else:
                            continue
                    except KeyboardInterrupt:
                        continue
                    except TimeoutError:
                        break
            else:
                print get_message(0x0f, messages.lang)
                #print u'\n密码错误'.encode("utf-8")
                import time
                time.sleep(3)
