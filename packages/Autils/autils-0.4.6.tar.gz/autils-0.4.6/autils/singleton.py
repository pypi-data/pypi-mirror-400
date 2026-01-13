#!/usr/bin/python3
# @Time    : 2018-12-18
# @Author  : Kevin Kong (kfx2007@163.com)

'''
元类实现的单例模式
'''


class Singleton(type):
    '''
    单例模式
    '''
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance
