#!/usr/bin/env python
# encoding: utf-8
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin MA
#   Email         : xxmawhu@163.com
#   File Name     : main.py
#   Created Time  : 2019-09-19 19:46
#   Last Modified : 2019-10-07 11:08
#   Describe      :
#
# ====================================================
import glob
import time
import sys
from linuxrecycle.config import local_config
from linuxrecycle import DB
from linuxrecycle import oper

rmForce = False
if "-f" in sys.argv:
    rmForce = True


def Rm(afile):
    # rm one file for use of pool.map
    # rm_status is the status of oprater 'mv' or 'rm'
    rm_status = ()
    if rmForce:
        rm_status = oper.RmForce(afile)
    else:
        rm_status = oper.MoveToTrash(afile)
    return rm_status


def obtainAllFile():
    files = []
    for i in sys.argv[1:]:
        files += glob.glob(i)
    return files


USAGE = """
*  Delete a file or folder
```
del [options] filename
```
> * -f remove the file or dictory forcely without backing up.

* Show all files which have been deleted
```
del.printDB [options] [num]
```
For example, only show the last 10 file
```
del.printDB -n 5
```
you will see
```
1220 Tue Dec 29 13:46:50 2020 xxxxxxxxx
1221 Tue Dec 29 13:46:50 2020 xxxxxxxxx
1222 Tue Dec 29 13:46:50 2020 xxxxxxxxx
1223 Tue Dec 29 13:46:56 2020 xxxxxxxxx
1224 Tue Dec 29 13:46:56 2020 xxxxxxxxx
1225 Tue Dec 29 13:53:16 2020 oh-my-god
```

* Recovery the file that deleted
```
del.recover [num] # i.e 1225
```

* Clean the trash folder
```
del.clean
```

##  Configuration

The  configuration file is located in ~/.mtdb/ with name mtrc
```
[core]
num_processor = 10
keep_days = 30
default_trash = /home/user/.trash
```
* num_processor: the number of processors used. Only increase the processors if you want to del millions files.
* keep_days: In command `del.clean`, the file has been deleted more than 30 days will be deleted. Choose the best setting for you.
* default_trash: All deleted file will back-up in this file. If you have a large disk, the file deleted from the disk will be back up in
the disk. Such as the disk is /data, the trash folder will be /data/.trash or /data/user/.trash


## setup your crontab
* `crontab -e`
```
14 4 * * * python ~/.mtdb/clear.py
```
"""


def main():
    if "-h" in sys.argv[1:] and len(sys.argv) == 2:
        print(USAGE)
        return
    if rmForce:
        logs = list(map(oper.RmForce, obtainAllFile()))
    else:
        logs = list(map(oper.MoveToTrash, obtainAllFile()))
    logCol = []
    for log in logs:
        if log[-1] == "exits":
            logCol.append(log)
    DB.insertDB(logCol)


if __name__ == "__main__":
    main()
    exit(0)
