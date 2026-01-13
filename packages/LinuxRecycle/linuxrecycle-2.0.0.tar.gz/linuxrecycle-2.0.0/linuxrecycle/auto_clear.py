#!/usr/bin/env python
# encoding: utf-8
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin MA
#   Email         : xxmawhu@163.com
#   File Name     : auto_clear.py
#   Created Time  : 2019-09-27 20:05
#   Last Modified : 2019-10-08 09:54
#   Describe      :
#
# ====================================================
import time
import sqlite3
import shutil
import os
from linuxrecycle import config


def delete_old_file(raws):
    """
    delete the file in the .trash
    info[2]
    """
    if raws:
        print("remove :")
    for info in raws:
        file_name = info[2]
        print(file_name)
        if info[3] != 'd':
            try:
                os.remove(file_name)
            except OSError:
                pass
        else:
            try:
                shutil.rmtree(file_name)
            except OSError:
                pass
    return


def update(rows):
    """
    func: update the record information to 'removed'
    """
    update_state = 'UPDATE fileInfo SET exits="removed" WHERE id==?'
    conn = sqlite3.connect(config.local_config.get('core', 'data_base_file'))
    try:
        cursor = conn.cursor()
        # print([int(i[0]) for i in rows])
        cursor.executemany(update_state, [(str(i[0]),) for i in rows])
        # rows = cursor.fetchall()
        conn.commit()
        cursor.close()
    finally:
        conn.close()
    return


def main():
    """
    1. select the record with time less than t_0 and exits = ""exits
    2. delete them and update the data base
    """
    conn = sqlite3.connect(config.local_config.get('core', 'data_base_file'))
    t0 = time.time() - 3600.0 * 24.0 * config.local_config.getint('core', 'keep_days')
    print("delete files more than {} days".format(config.local_config.get('core', 'keep_days')))
    # t0 = time.time() - 3600.0 * 24.0 * 1.0
    # config.local_config.getint('core', 'keep_days')
    query = "SELECT * FROM fileInfo "
    query += ' WHERE  time < {} AND exits!="removed"'.format(t0)
    raws = []
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        raws = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    # print rows
    if not raws:
        print("[Info] no files are needed to be removed!")
    delete_old_file(raws)
    update(raws)
    # write log
    log_file = os.path.expanduser('~/.mtdb/log')
    f = open(log_file, 'a')
    date = time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime())
    f.write('auto clear trash @ {}\n'.format(date))
    f.close()
    return


if __name__ == "__main__":
    main()
