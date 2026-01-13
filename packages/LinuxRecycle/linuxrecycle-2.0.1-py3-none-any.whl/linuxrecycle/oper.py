#!/usr/bin/env python
# encoding: utf-8
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin MA
#   Email         : xxmawhu@163.com
#   File Name     : oper.py
#   Created Time  : 2019-09-19 15:05
#   Last Modified : 2019-10-07 11:10
#   Describe      :
#
# ====================================================
import os
import time
from linuxrecycle import trashInfo
import subprocess as sp
import shutil
import glob


def RmForce(fileName):
    """
    if -f in opt, rm the file directly
    """
    fileName = os.path.expanduser(fileName)
    address = os.path.abspath(fileName)
    exits = "removed"
    Type = "f"
    date = time.strftime("%Y-%m-%d:%H:%M:%S", time.localtime())
    try:
        os.remove(address)
    except OSError as e:
        # [Error 21] Is directory: ...
        if e.args[0] == 21:
            Type = "d"
            shutil.rmtree(address)
        else:
            raise e
    finally:
        return (address, "", Type, time.time(), date, exits)


# @profile
def MoveToTrash(address):
    """
    Warning: the file must be an exact file or directory. The following cases
    are not allowed
    jobs/*,  *.py, jobs_00?.txt, */*.py
    staus will be returned, like
    (address, trashAddress, type, time, date, exits)
    """
    address = os.path.expanduser(address)
    address = os.path.abspath(address)
    # print("address :", address)
    trashName = trashInfo.getTrashAddress(address)
    # print("trash name: " + trashName)
    exits = "exits"
    Type = "f"
    if os.path.isdir(address):
        Type = "d"
    date = time.strftime("%y%m%d_%H%M%S", time.localtime())
    if trashInfo.inTrash(address) or trashInfo.tmpFile(address):
        exits = "removed"
        RmForce(address)
        return (address, "", Type, time.time(), date, exits)
    if trashInfo.whiteFile(address):
        return (address, address, Type, time.time(), date, exits)
    else:
        trashAddress = os.path.join(trashName, address.split("/")[-1] + "." + date)
        # print("Address in trash : ", trashAddress)
        # print("mv  {} {}".format(address, trashAddress))
        try:
            shutil.move(address, trashAddress)
            return (address, trashAddress, Type, time.time(), date, exits)
        except PermissionError as e:
            return (address, address, Type, time.time(), date, exits)
        except IOError as e:
            # print(e)
            os.mkdir(trashName)
            shutil.move(address, trashAddress)
            return (address, trashAddress, Type, time.time(), date, exits)
        except OSError as e:
            # print(e)
            return (address, address, Type, time.time(), date, exits)

    return ()


if __name__ == "__main__":
    testf = os.environ["PWD"] + "/dada.txt"
    os.system("touch {}".format(testf))
    RmForce(testf)
    exit()
    os.system("touch {}".format(testf))
    print((MoveToTrash(testf)))
    for ff in glob.glob("dada*"):
        # print ff
        MoveToTrash(ff)
