# -*- coding: utf-8 -*-
# @Author	: brotherbaby
# @Date		: 2025/8/22 10:15
# @Last Modified by:   brotherbaby
# @Last Modified time: 2025/8/22 10:15
# Thanks for your comments!

def singleton(clsname):
    instances = {}

    def getinstance(*args, **kwargs):
        if clsname not in instances:
            instances[clsname] = clsname(*args, **kwargs)
        return instances[clsname]

    return getinstance
