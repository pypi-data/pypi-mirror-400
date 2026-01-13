#!/usr/bin/python3
# @Time    : 2022-06-23
# @Author  : Kevin Kong (kfx2007@163.com)

import datetime
import calendar
from dateutil.relativedelta import relativedelta


class dateutil(object):

    @classmethod
    def get_current_month_range(self):
        """获取当前月份范围"""
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        return self.get_first_and_last_day(year, month)

    @classmethod
    def get_season_range(self):
        """获取季度时间范围"""
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        quarter = int((month - 1) / 3) + 1
        if quarter == 1:
            return f"{year}-01-01", f"{year}-03-31"
        if quarter == 2:
            return f"{year}-04-01", f"{year}-06-30"
        if quarter == 3:
            return f"{year}-07-01", f"{year}-09-30"
        if quarter == 4:
            return f"{year}-10-01", f"{year}-12-31"

    @classmethod
    def get_first_and_last_day(self, year=None, month=None):
        """
        获取指定年月的第一天和最后一天

        :params
        :year: 年份
        :month :月份

        :Return 指定月份的第一天和最后一天.        
        """
        if year is None:
            year = datetime.datetime.now().year
        if month is None:
            month = datetime.datetime.now().month
        weekday, month_count_day = calendar.monthrange(year, month)
        first_day = datetime.date(year, month, day=1)
        last_day = datetime.date(year, month, day=month_count_day)
        return first_day, last_day

    @classmethod
    def get_week_range(self, date=None):
        if not date:
            date = datetime.date.today()
        index = date.isoweekday()
        left, right = 1 - index, 7 - index
        return date + relativedelta(days=left), date+relativedelta(days=right)
