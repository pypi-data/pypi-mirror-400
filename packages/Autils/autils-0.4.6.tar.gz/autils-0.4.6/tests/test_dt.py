#!/usr/bin/python3
# @Time    : 2020-02-08
# @Author  : Kevin Kong (kfx2007@163.com)

from autils.datetime import DateTime
from datetime import datetime
import unittest


class TestDateTime(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.local = DateTime(datetime(2020, 1, 1, 0, 0, 0), tz="Asia/Shanghai")

    def test_to_utc(self):
        self.assertEqual(self.local.to_utc_time_str(), "2019-12-31 16:00:00")


if __name__ == "__main__":
    unittest.main()
