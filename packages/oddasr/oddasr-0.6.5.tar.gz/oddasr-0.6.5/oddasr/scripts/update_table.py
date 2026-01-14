import sys

import pymysql

import config

'''
用于更新数据库字段.
'''
if __name__ == '__main__':
    # create database
    usr = sys.argv[1]
    pwd = sys.argv[2]
    if not usr or not pwd:
        usr = config.Mysql_User
        pwd = config.Mysql_Pwd

    con = pymysql.connect(host=config.Mysql_Host,
                          user=usr,
                          password=pwd,
                          charset='utf8mb4')
    cur = con.cursor()
    with open('update_table.sql', 'r', True, 'UTF-8') as f:
        sql_list = f.read().split('$$')[:-1]

        for x in sql_list:
            line = x.split('\n')
            L = ''
            for y in line:
                l = y.split('#', 1)[0].split('-- ', 1)[0]
                L = L + ' ' + l
            # sql语句添加分号结尾
            sql_item = L + ';'
            print(sql_item)
            cur.execute(sql_item)
    con.commit()
    cur.close()
    con.close()
