#!/usr/bin/env python
# encoding: utf-8
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin MA
#   Email         : xxmawhu@163.com
#   File Name     : trashInfo.py
#   Created Time  : 2019-09-19 15:05
#   Last Modified : 2019-09-19 19:46
#   Describe      :
#
# ====================================================
import sys
import os
from linuxrecycle import argv
from linuxrecycle.config import local_config
from linuxrecycle.config import user
system_dir = ["etc", "bin", "dev", "lib", "lib32", "libx32", "lost+found", "usr", "mnt", "srv", "var"]


def getTrashAddress(afileName):
    """
    Warning: the file name can't contain ~, or $USER,
    please expand them
    1. split the name by $USER
    2. [0]/$USER/.trash
    3. begin with 'etc', 'src'
    """
    afileName = os.path.abspath(afileName)
    # print(afileName)
    file_head = afileName[1:].split('/')[0]
    # print('head', file_head)

    # case 3
    if file_head in system_dir:
        return local_config['core']['default_trash']
    elif file_head == 'media':
        ll = afileName[1:].split('/')[:3]
        # pint(ll)
        ll.append('.trash')
        return os.path.join(ll)

    if user in afileName:
        pp = afileName.split(user)
        return os.path.join(pp[0], user, '.trash')
    trs = "/" + afileName.split("/")[1] + '/.trash'
    return trs


def inTrash(afileName):
    """
    True if the afile is within a .trash
    False not
    Once found ${USER}/.trash in the path, then the path is determined within
    a trash
    """
    tak = '/.trash/'
    if tak in afileName:
        return True
    return False


def tmpFile(afileName):
    """
    True if the file is fileInfo.db
    """
    tak = afileName.split("/")[1]
    if afileName in ['tmp']:
        return True
    return False


def whiteFile(afileName):
    """
    True if the in /tmp/...
    """
    tak = afileName.split("/")[1]
    if tak in local_config['core']['white_files'].split(','):
        return True
    return False


if __name__ == "__main__":
    testf = os.environ["PWD"]
    print((getTrashAddress(testf)))
    ff = getTrashAddress(testf) + "/dada/dada"
    if inTrash(ff):
        print(ff)
        print("In trash")
