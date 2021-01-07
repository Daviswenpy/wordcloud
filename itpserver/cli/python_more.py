# use to implement a simple more
# 1, space: next page
# 2, enter: next line
# 3, q: exit
"""python more implement."""
import os
import sys
import curses
import re
import signal
import fcntl
import termios
import struct


page_len = 0
line_len = 0
sig_up = 0
winsz_chg = 0

import commands

def get_current_terminal():
    (stat, output) = commands.getstatusoutput("tty")
    if stat:
        return None
    else:
        return output

def win_sz_chg(signum, frame):
    """the single handler for window change."""
    global page_len, line_len, winsz_chg
    winsz_chg = 1
    signal.signal(signal.SIGWINCH, signal.SIG_IGN)
    s = struct.pack("HHHH", 0, 0, 0, 0)
    a = struct.unpack(
        'hhhh',
        fcntl.ioctl(
            sys.stdout.fileno(),
            termios.TIOCGWINSZ, s))
    page_len = int(a[0]) - 1
    line_len = int(a[1])
    signal.signal(signal.SIGWINCH, win_sz_chg)


signal.signal(signal.SIGWINCH, win_sz_chg)


def term_do_exit(signum, frame):
    """the keyboard interrupt handler."""
    global sig_up
    sig_up = 1
    terminal = get_current_terminal()
    if terminal != None:
        os.system("/bin/stty -F %s echo" % terminal)
        os.system("/bin/stty -F %s -cbreak" % terminal)
    sys.exit()


signal.signal(signal.SIGINT, term_do_exit)
#signal.signal(signal.CTRL_C_EVENT, term_do_exit)


def usage():
    """usage function."""
    print "-----------------usage-----------------"
    print "1./more.py [+num] [+/pattern] filename"
    print "2 command | ./more.py"
    print "num: Start at line number num. "
    print "pattern:Start at line number num."
    print "space: next page"
    print "q :do_exit the program"
    print "enter:next line"
    print"----------------------------------------"
    sys.exit()


def do_exit():
    """use for system exit."""
    terminal = get_current_terminal()
    if terminal != None:
        os.system("/bin/stty -F %s echo" % terminal)
        os.system("/bin/stty -F %s -cbreak" % terminal)
    print "\033[20D\033[K"
    sys.exit()


def is_input():
    """
    check if any data from pipe.

    return:
    1:
    0:

    """
    try:
        f = sys.stdin.fileno()
        init_tty = termios.tcgetattr(f)
        return 0
    except:
        return 1


def get_line_num(args):
    """
    get the starting line number.

    return:
    line_num

    """
    line_num = 1
    for i in args:
        ln = re.search(r'\+\d+', str(i))
        if ln:
            line_num = int(ln.group().lstrip('+'))
            break
    return line_num


def get_patstr(args):
    """
    get patstr function.

    return:
    patstr

    """
    patstr = ""
    for i in args:
        pa = re.search(r'(\+\/\w*[^\s])', str(i))
        if pa:
            break
    if pa:
        patstr = str(pa.group().lstrip('+/'))
    return patstr


def get_args():
    """
    get args function.

    return:

    line_num, patstr, fp

    """
    line_num = 1
    patstr = ""
    args = sys.argv[1:]
    if not args:
        if is_input():
            fp = sys.stdin
            return (line_num, patstr, fp)
        else:
            usage()
    else:
        if args[-1] == "--help":
            usage()
        line_num = get_line_num(args)
        patstr = get_patstr(args)
        if '+' not in args[-1]:
            filename = args[-1]
            if not os.path.exists(filename):
                print " ........."
                do_exit()
            else:
                #import codecs
                #fp = codecs.open(filename, encoding='utf-8')
                fp = open(filename)
        else:
            if not is_input():
                usage()
            else:
                fp = sys.stdin
    return (line_num, patstr, fp)


def get_screen_size():
    """get screen size."""
    global page_len, line_len
    screen = curses.initscr()
    page_len, line_len = screen.getmaxyx()
    page_len = page_len - 2
    # for chinese
    line_len = line_len / 2 * 3
    curses.endwin()


def show_more(pre_pg_len):
    """
    show more function.

    return:
    1:
    0:

    """
    global sig_up, winsz_chg, page_len
    terminal = get_current_terminal()
    ft = open(terminal)
    #ft = open('/dev/tty')
    sys.stdout.flush()
    c = ''
    while True:
        try:
            c = ft.read(1)
        except IOError:
            if sig_up:
                do_exit()
        if c == " ":
            print "\033[20D\033[K"
            if winsz_chg:
                winsz_chg = 0
                return pre_pg_len
            else:
                return page_len
        elif c == "q":
            print "\033[20D\033[K"
            return 0
        elif c == '\n':
           # print "\033[20D\033[K",
            return 1


def skip_ln(fp, line_num):
    """skip column."""
    n = line_num - 1
    while n:
        fp.readline()
        if not fp:
            return
        n = n - 1


def search(fp, patstr):
    """search function."""
    global sig_up
    text = ' '
    while True:
        try:
            s = fp.read(1)
            if not s:
                print "can not find the string in the file"
                do_exit()
            text = text + s
            if patstr in text:
                return
        except IOError:
            if sig_up:
                do_exit()


def show_prog(read_size, total_size):
    """show program."""
    if total_size:
        prog = int(read_size * 100 / float(total_size))
        print "\033[7m --More--" + str(prog) + '%' + "\033[0m",
    else:
        print "\033[7m --More--" + "\033[0m",
    return

def is_start_of_chinese(char):
    if 0xe0 <= ord(char) and 0xef >= ord(char):
        return True
    else:
        return False

def is_full_chinese(word):
    if len(word) < 3:
        return 0
    if is_start_of_chinese(word[-1]):
        return 1
    elif is_start_of_chinese(word[-2]):
        return 2
    else:
        return 0

def do_more(fp, line_num, patstr):
    """more function."""
    global page_len, line_len
    read_size = 0
    total_size = 0
    terminal = get_current_terminal()
    if terminal != None:
        os.system("/bin/stty -F %s cbreak" % terminal)
        os.system("/bin/stty -F %s -echo " % terminal)
    if fp != sys.stdin:
            fp.seek(0, 2)
            total_size = fp.tell()
            fp.seek(0, 0)
    if line_num != 1:
        skip_ln(fp, line_num)
    if patstr:
        search(fp, patstr)
    try:
        line = fp.readline(line_len)
        # Modified by hdu
        current_pos = fp.tell()
        cursor_forward = is_full_chinese(line[-3:])
        if cursor_forward != 0:
            fp.seek(current_pos - cursor_forward)
            line = line.replace(' ','')[:-cursor_forward]
        read_size = len(line)
        num_lns = 0
        while line:
            if num_lns == page_len:
                pre_pg_len = page_len
                show_prog(read_size, total_size)
                reply = show_more(pre_pg_len)
                if reply == 0:
                    break
                num_lns -= reply
            print "\033[20D\033[K" + line.strip('\n')
            #print line.strip('\n')
            sys.stdout.flush()
            read_size = read_size + len(line)
            num_lns += 1
            line = fp.readline(line_len)
            # Modified by hdu
            current_pos = fp.tell()
            cursor_forward = is_full_chinese(line[-3:])
            if cursor_forward != 0:
                fp.seek(current_pos - cursor_forward)
                line = line.replace(' ','')[:-cursor_forward]
        fp.close()
    except IOError:
        if sig_up:
            do_exit()

if __name__ == '__main__':
    get_screen_size()
    (line_num, patstr, fp) = get_args()
    do_more(fp, line_num, patstr)
    do_exit()
