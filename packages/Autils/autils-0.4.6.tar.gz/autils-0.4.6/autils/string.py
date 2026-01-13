#!/usr/bin/python3
# @Time    : 2018-11-13
# @Author  : Kevin Kong (kfx2007@163.com)

from string import ascii_letters, digits
from random import choice
from . import od

class randomstr(object):

    @classmethod
    def generate(cls, length=8):
        '''
        产出指定长度的随机字符串
        '''
        return ''.join([choice(ascii_letters + digits) for _ in range(length)])

    @classmethod
    def generate_digits(cls, length=8):
        '''
        指定长度的纯数字
        '''
        return ''.join(choice(digits) for _ in range(length))

    @classmethod
    def generate_strs(cls, length=8):
        '''
        指定长度的纯字母
        '''
        return "".join(choice(ascii_letters) for _ in range(length))

    @classmethod
    def get_alphabet_number(cls, char):
        """获取字母的数字序列"""
        if ord(char.lower()) < 97 or ord(char.lower()) > 123:
            raise Exception("Wrong Alphabet.")

        return ord(char.lower()) - 96