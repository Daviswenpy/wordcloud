#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal
import os
import readline
import sys
import commands
import messages

MSG_INFO_INPUT_INVALID = u'输入错误\n'.encode('utf-8')

class TimeoutError(Exception):

    """Timeout exception."""

    pass

def alarm_handler(*args):
    raise TimeoutError

def new_timeout_input(prompt):
    signal.signal(signal.SIGALRM, alarm_handler)
    timeout_val = 300
    signal.alarm(timeout_val)
    try:
        line = raw_input(prompt)
    except EOFError:
        line = 'EOF'
    except TimeoutError:
        raise TimeoutError
#        sys.exit(0)
    signal.alarm(0)
    return line

def my_raw_input(prompt, default=''):
    if default:
        readline.set_startup_hook(lambda: readline.insert_text(default))
        try:
            return new_timeout_input(prompt)
        finally:
            readline.set_startup_hook()
    else:
        return new_timeout_input(prompt)

TOP_BANNER_UCSS = u'欢迎使用SkyGuard UCSS统一内容安全管理平台控制台\n'.encode('utf-8')
TOP_BANNER_UCSS_LITE = u'欢迎使用SkyGuard UCSS Lite统一内容安全扩展服务器控制台\n'.encode('utf-8')
TOP_BANNER_UCSG = u'欢迎使用SkyGuard UCSG统一内容安全网关控制台\n'.encode('utf-8')

DEVICE_INFO = u'    版本: %s，设备ID: %s\n'.encode('utf-8')

DASH_INTERRUPTER = "--------------------%s---------------------\n"

def clear_screen():
    os.system(['clear','cls'][os.name == 'nt'])

def print_top_banner(message=''):
#    print TOP_BANNER_UCSS
    print get_message(0x183, messages.lang)
    print DASH_INTERRUPTER % message

def app_command(command, err_exit=False):
    # app_logger(command)
    (stat, cmd_output) = commands.getstatusoutput(command)
    if stat:
        if err_exit:
            sys.exit(254)
        return (os.WEXITSTATUS(stat), [cmd_output])
    else:
        return (0, cmd_output.split("\n"))


def my_prompt(prompt, default='', options=(), validate_func=None, args=None):
    """
    The prompt function.

    return:
    string

    """
    while True:
#        opt = my_raw_input(prompt + ' ', default).lower()
        if options == ():
            opt = new_timeout_input(prompt + ' ')
        else:
            opt = new_timeout_input(prompt + ' ').lower()
        if opt == '' and default:
            opt = default
        if validate_func != None:
            if args == None:
                if validate_func(opt) == False:
                    print MSG_INFO_INPUT_INVALID
                    continue
            else:
                if validate_func(opt, args) == False:
                    print MSG_INFO_INPUT_INVALID
                    continue
        if options == ():
            return opt
        elif opt in options:
            return opt
        else:
            print MSG_INFO_INPUT_INVALID

import termios
import string
LEGAL_CHAR = string.ascii_letters + string.digits + "~`!@#$%^&*()_+-={}[]\\|;:'\",<.>/?"
CHAR_BUF=""
MAX_PASSWORD = 2000
MAX_PASSWD_GENERAL = 64

def get_char():
    """Get char from input."""
    global CHAR_BUF

    if len(CHAR_BUF)>0:
        res = CHAR_BUF[0]
        CHAR_BUF = CHAR_BUF[1:len(CHAR_BUF)]
        return res

    fd = sys.stdin.fileno()

    if os.isatty(fd):
        old = termios.tcgetattr(fd)
        new = termios.tcgetattr(fd)
        new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
        new[6][termios.VMIN] = 1
        new[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, new)
        termios.tcsendbreak(fd, 0)
        try:
            CHAR_BUF = os.read(fd, MAX_PASSWORD)
        except KeyboardInterrupt:
            termios.tcsetattr(fd, termios.TCSAFLUSH, old)
            raise KeyboardInterrupt
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)
    else:
        CHAR_BUF = os.read(fd, 7)

    if len(CHAR_BUF)>0:
        res = CHAR_BUF[0]
        CHAR_BUF = CHAR_BUF[1:len(CHAR_BUF)]
        return res
    return ('\x00')

def get_next_char():
    """Get next meaningful character from input."""
    c1 = get_char()
    while True:
        # 0x1b - Escape
        if '\x1b' == c1:
            c2 = get_char()
            if '[' == c2:
                c3 = get_char()
                # ignore arrow key
                # ignore 'insert','home','pageup','pagedown' and etc.
                # ignore F1-F12
                if c3 in ['A', 'B', 'C', 'D']:
                    c1 = get_char()
                    continue
                elif c3 in ['1', '2', '3', '4', '5', '6']:
                    c4 = get_char()
                    if '~' == c4:
                        c1 = get_char()
                        continue
                    elif c3 not in ['1', '2']:
                        c1 = c4
                        continue
                    if "".join([c3,c4]) not in ["11","12","13","14","16","17","18","19","20","21","23","24"]:
                        c1 = c4
                        continue
                    c5 = get_char()
                    if '~' != c5:
                        c1 = c5
                    else:
                        c1 = get_char()
                    continue
                else:
                    return c3
            # ignore small key board
            elif 'O' == c2:
                c3 = get_char()
                if c3 not in ['M','P','Q','R','S','m','n','p','q','r','s','t','u','v','w','y']:
                    c1 = c3
                else:
                    c1 = get_char()
                continue
            else:
                c1 = c2
                continue
        else:
            return c1

def input_password(str, maxc):
    """Get Password from Input."""
    res = []
    print "\r%s" % (str),
    sys.stdout.flush()

    while True:
        c = get_next_char()
        bc = ord(c)
        if '\n' == c:
            print ""
            return "".join(res)
        if '\x08' != c and (bc>127 or bc<33):
            continue
        if c in LEGAL_CHAR and len(res)<maxc:
            res.append(c)
            sys.stdout.write("*")
        else:
            if '\x7f' == c or '\x08' == c:
                if len(res) > 0:
                    del res[-1]
                    sys.stdout.write("\b \b")
        sys.stdout.flush()

    return res

def get_message(messageid, lang):
    return messages.messages[messageid][lang]

if __name__ == "__main__":
    print input_password("password", 10)
