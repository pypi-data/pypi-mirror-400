#!/usr/bin/env python3
# encoding: utf-8
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin MA
#   Email         : xxmawhu@163.com
#   File Name     : config.py
#   Created Time  : 2019-09-19 23:52
#   Last Modified : 2019-09-26 16:00
#   Describe      :
#
# ====================================================
import os
from configparser import ConfigParser

local_config = ConfigParser()
if os.path.exists(os.path.expanduser("~/.mtdb/mtrc")):
    local_config.read(os.path.expanduser("~/.mtdb/mtrc"))
else:
    mtdbDir = os.path.expanduser("~/.mtdb")
    if not os.path.exists(mtdbDir):
        os.mkdir(mtdbDir)
    local_config.add_section("core")
    local_config.set("core", "Num_Processor", "100")
    local_config.set("core", "Keep_data_base", "1")
    local_config.set("core", "keep_days", "30")
    local_config.set("core", "default_trash", os.path.expanduser("~/.trash"))
    local_config.set(
        "core", "data_base_file", os.path.expanduser("~/.mtdb/fileInfo.db")
    )
    local_config.set(
        "core", "white_files", os.path.expanduser("~/.mtdb/fileInfo.db") + ","
    )
    with open(os.path.expanduser("~/.mtdb/mtrc"), "w") as configFile:
        local_config.write(configFile)
user = ""
if "USER" in os.environ:
    user = os.environ["USER"]
elif "LOGNAME" in os.environ:
    user = os.environ["LOGNAME"]
elif "USERNAME" in os.environ:
    user = os.environ["USERNAME"]
else:
    print("Error, can not find USER, LOGNAME, or USERNAME")


def makeAutoClear():
    mtdbDir = os.path.expanduser("~/.mtdb")
    f = open(mtdbDir + "/clear.py", "w")
    f.write("#!/usr/bin/env python3\n")
    f.write("import linuxrecycle.auto_clear as cl\n")
    f.write("cl.main()\n")
    f.close()


autoClear = os.path.expanduser("~/.mtdb/clear.py")
if not os.path.exists(autoClear):
    makeAutoClear()

if __name__ == "__main__":
    print(local_config["core"]["Num_Processor"])
    print(local_config["core"]["keep_days"])
    print(local_config["core"]["data_base_file"])
    print(local_config["core"]["default_trash"])
    print("USER {}".format(user))
# print local_config.get('core', 'white_file')
