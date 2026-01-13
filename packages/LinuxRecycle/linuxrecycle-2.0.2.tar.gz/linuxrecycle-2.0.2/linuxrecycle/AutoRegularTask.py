#!/usr/bin/env python3
# encoding: utf-8
# coding style: pep8
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin Ma
#   Email         : xxmawhu@163.com
#   File Name     : setCrontab.py
#   Last Modified : 2019-11-05 10:41
#   Describe      :
#
# ====================================================

# import sys
import os
import subprocess as sp
from linuxrecycle import config


class AutoRegularTask:
    """
    regular execute a command by `crontab`
    """

    def __init__(self):
        self._newCommand = set()
        self._oldCommand = ''
        self._tmpFile = []

    def Add(self, command, hour="3", minute="14", month="*", day="*", week="*"):
        new_command = "{Minute} {Hour} {Day} {Month} {Week} {Command}".format(
            Minute=minute, Hour=hour, Command=command, Month=month, Day=day, Week=week
        )
        self._newCommand.add(new_command)

    def _getOldCrontab(self):
        """
        return crontab -l
        """
        process = sp.Popen(['crontab', '-l'], stdout=sp.PIPE, stderr=sp.PIPE)
        out, err = process.communicate()
        self._oldCommand = out.decode()

    def setAllCommands(self):
        """
        add the commands on one by one
        """
        self._getOldCrontab()
        f = open("tmp.txt", 'w')
        f.write(self._oldCommand)
        for new_command in self._newCommand:
            if new_command in self._oldCommand:
                continue
            f.write("{}\n".format(new_command))
        f.close()
        self._tmpFile.append("tmp.txt")
        process = sp.Popen(['crontab', '-u', config.user, "tmp.txt"], stdout=sp.PIPE, stderr=sp.PIPE)
        out, err = process.communicate()

    def removeTmpFile(self):
        """
        As its name, remove all tmp file such as "tmp.txt"
        """
        for f in self._tmpFile:
            try:
                os.remove(f)
            except Exception as e:
                raise e
            finally:
                pass

    def setup(self):
        self.setAllCommands()
        self.removeTmpFile()
        print("setup sucessful!")
        self._getOldCrontab()
        print(self._oldCommand)
