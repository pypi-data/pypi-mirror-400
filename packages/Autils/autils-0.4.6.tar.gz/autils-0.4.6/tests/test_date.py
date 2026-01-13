#!/usr/bin/python3
# @Time    : 2022-06-23
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from autils.date import datetool

class TestDateTool(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.year = 2020
        cls.month = 2

    def test_get_month_range(self):
        first_day, last_day = datetool.get_first_and_last_day(self.year,self.month)
        print(first_day,last_day)

    def test_get_season_range(self):
        first_day, last_day = datetool.get_season_range()
        print(first_day,last_day)


    def test_get_week_range(self):
        start, end = datetool.get_week_range()
        print(start, end)
    

if __name__ == "__main__":
    unittest.main()