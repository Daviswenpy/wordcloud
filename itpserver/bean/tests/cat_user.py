# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-11-24 18:04:14
File Name: add_user.py @v2.0
"""
import sqlite3


def opendata():
    # /opt/skyguard/itpserver/db.sqlite3
    # bean/db.sqlite3
    conn = sqlite3.connect("/opt/skyguard/itpserver/db.sqlite3")
    return conn


def show():
    cur = opendata().cursor()
    cur.execute("select * from auth_user")
    user_lines = cur.fetchall()
    cur.execute("select * from itm_userprofile")
    itm_lines = cur.fetchall()

    data = {}
    for user_line in user_lines:
        password = None
        if user_line[-1] == 'itm-admin':
            for itm_line in itm_lines:
                if user_line[0] == itm_line[0]:
                    password = itm_line[1]
                    data["id"] = user_line[0]
                    data["date_joined"] = user_line[9][:19]
                    data["password"] = password
                    data["username"] = user_line[-1]
    cur.close()
    return data


def update(**user):
    users = show()
    changechoice = str(1)
    if users['username'] == 'itm-admin':
        changechoice = str(users['id'])
    conn = opendata()
    username = user.get("username")
    password = user.get("password")

    if isinstance(username, str) and isinstance(password, str):
        error_list = set(["\\", "'", "\"", "=", "|", "?", "/", ">", "<", ".", ">=", "<=", "_", "%", "\"\"", ",", "<>", ";", "||", "&", "[", "]", " ", "*", "!", "@"])
        if len(set(list(username)) & error_list) == 0 and len(set(list(password)) & error_list) == 0:
            # print len(set(list(username)) & error_list)
            conn.execute("update auth_user set username=? where id=" + changechoice, (username,))
            conn.execute("update itm_userprofile set passwordHash=? where user_id=" + changechoice, (password,))
            conn.commit()
            # show()
            conn.close()
        else:
            # print "Error"
            return "Error"


# import hashlib
# user = {"username": "itm-admin", "password": hashlib.sha256("itm-admin").hexdigest()}
# print user
# update(**user)
print show()
