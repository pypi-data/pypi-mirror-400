#!/usr/bin/env python
# encoding: utf-8
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin MA
#   Email         : xxmawhu@163.com
#   File Name     : printDB.py
#   Created Time  : 2019-09-27 14:37
#   Last Modified : 2019-10-07 13:27
#   Describe      :
#
# ====================================================
import time
import sys
from termcolor import colored
from linuxrecycle import DB


def init():
    """
    show help 
    """
    if '-h' in sys.argv[1:]:
        print("usage : show the last #n records") 
        print("    rm.printDB n") 
        exit(0)
    return

def main():
    '''
    function:
        print the last #n record information about the files deleted
    '''
    init()
    n = 100
    try:
        n = int(sys.argv[1])
    except IndexError as e:
        pass
    except ValueError as e:
        print("Error:: Please input a integer!!! .> -> {}".format(sys.argv[1]))
        raise e
    for inf in sorted(DB.getLastRecord(n, "exits='exits'"), key=lambda x:x[0]):
        # print(inf)
        date = time.asctime(time.localtime(inf[4])).replace("Sat", "@")
        print (" ".join([colored(inf[0], 'blue','on_grey', attrs=['bold']), colored(date,'green'
                ), inf[1]]))
if __name__ == "__main__":
    main()
