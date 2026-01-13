#!/usr/bin/python3
# @Time    : 2018-12-14
# @Author  : Kevin Kong (kfx2007@163.com)

from .excepts import AutilsDictException


class Dict(object):

    @classmethod
    def reverse_dict(cls,dic):
        '''
        翻转字典，将key和value换位
        '''
        if not isinstance(dic,dict):
            raise AutilsDictException("reverse_dict方法要求一个字典，传入的参数不是字典")
        return dict(zip(dic.values(),dic.keys()))