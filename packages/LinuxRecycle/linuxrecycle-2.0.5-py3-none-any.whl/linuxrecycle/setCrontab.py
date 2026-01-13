#!/usr/bin/env python3
# encoding: utf-8
# coding style: pep8
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin Ma
#   Email         : xxmawhu@163.com
#   File Name     : setCrontab.py
#   Last Modified : 2019-11-05 11:26
#   Describe      :
#
# ====================================================

# import sys
import os
import subprocess as sp
from AutoRegularTask import AutoRegularTask
if __name__ == "__main__":
    crontab = AutoRegularTask()
    crontab.Add("python {}".format(os.path.abspath("auto_clear.py")),
            hour = "4")
    crontab.setup()
