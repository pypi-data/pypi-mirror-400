#!/usr/bin/python3
# @Time    : 2018-11-16
# @Author  : Kevin Kong (kfx2007@163.com)

'''
数字相关类
'''
import decimal

class Digits(object):

    # create a new context for this task
    ctx = decimal.Context()
    # 20 digits should be enough for everyone :D
    ctx.prec = 20

    @classmethod
    def convert_float_to_str(cls,f):
        '''
        将浮点数类型转换为str类型
        浮点数大于4时，会以科学记数法显示，本方法就是不让结果以科学记数法显示
        '''
        d1 = cls.ctx.create_decimal(repr(f))
        return format(d1, 'f')