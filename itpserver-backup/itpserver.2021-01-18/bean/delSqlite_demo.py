# -*- coding: utf-8 -*-
'''
User Name: wendong@skyguard.com.cn
Date Time: 1/16/21 11:41 AM
File Name: /
Version: /
'''

import sqlite3
import os
import datetime

db = 'db.sqlite3'

class SqlOperate:
    """
    table_name: "itm_session"
    sessionID char
    clientIP char
    created datetime
    sessionTimeout int
    """

    def __init__(self, tableName="itm_session"):
        self.table = tableName
        self.c = self.create_connect()

    def create_connect(self):
        self.conn = sqlite3.connect(db)
        print 'opened database successfully...'
        return self.conn.cursor()

    def get_table_info(self):
        """get table info, limit 5, created desc"""
        select_sql = 'select * from {0} order by created desc limit 5'.format(self.table)
        cursor = self.c.execute(select_sql)
        return self.get_lst(cursor)

    def get_lst(self,cursor):
        """return db info, list"""
        db_info_lst = []
        for row in cursor:
            info = {}
            info["id"] = row[0]
            info["sessionID"] = row[1]
            info["clientIP"] = row[2]
            info["created"] = row[3]
            info["sessionTimeout"] = row[4]
            db_info_lst.append(info)
        self.conn.close()
        return db_info_lst

    def del_db(self):
        """del former-day record"""
        today = datetime.datetime.now().date()
        del_sql = 'delete from {0} where datetime(created)<datetime({1})'.format(self.table, today)
        self.c.execute(del_sql)
        self.conn.commit()
        self.conn.close()



if __name__ == '__main__':
    sqlite = SqlOperate()
    # sqlite.del_db()
    print sqlite.get_table_info()