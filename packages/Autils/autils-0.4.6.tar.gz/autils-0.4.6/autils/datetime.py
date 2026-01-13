#!/usr/bin/python3
# @Time    : 2020-01-02
# @Author  : Kevin Kong (kfx2007@163.com)

from datetime import datetime, date
import pytz


class timeutil(object):

    def __init__(self, src_date, format="%Y-%m-%d %H:%M:%S", tz="UTC"):
        if type(src_date) is datetime:
            self.naive_date = src_date
        elif type(src_date) is date:
            self.naive_date = datetime.combine(src_date, datetime.min.time())
        elif type(src_date) is float or type(src_date) is int:
            # 时间戳
            self.naive_date = datetime.fromtimestamp(src_date)
        else:
            self.naive_date = datetime.strptime(src_date, format)
        self.format = format
        local = pytz.timezone(tz)
        self.local_date = local.localize(self.naive_date, is_dst=None)

    def to_utc_time(self):
        """转换UTC时间"""
        return self.local_date.astimezone(pytz.utc)

    def to_utc_time_str(self,format=None):
        """转换UTC时间字符串"""
        if format is None:
            format = self.format
        return datetime.strftime(self.to_utc_time(), format)

    def to_utc_timstamp(self):
        """转换UTC时间戳"""
        return self.local_date.astimezone(pytz.utc).timestamp()

    def to_local_time(self, tz="Asia/Shanghai"):
        """转换本地时间"""
        return self.local_date.astimezone(pytz.timezone(tz))

    def to_local_time_str(self, tz="Asia/Shanghai"):
        return datetime.strftime(self.to_local_time(tz), '%Y-%m-%d %H:%M:%S')

    @classmethod
    def get_current_week(cls):
        """获取当前周number"""
        return date.today().isocalendar()[1]
