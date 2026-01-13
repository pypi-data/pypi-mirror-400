import unittest
from autils.datetime import timeutil
from datetime import datetime, date


class TestDateTime(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.date = timeutil("2019-12-31 00:00:00")

    def test_convert_utc(self):
        """测试转换UTC"""
        utc = self.date.to_utc_time()
        self.assertEqual(datetime.strftime(
            utc, '%Y-%m-%d %H:%M:%S'), "2019-12-31 00:00:00")

    def test_convert_utc_str(self):
        """测试转换UTC"""
        utc = self.date.to_utc_time_str()
        self.assertEqual(utc, "2019-12-31 00:00:00")

    def test_convert_local_time(self):
        """测试转换本地时间"""
        local = self.date.to_local_time()
        self.assertEqual(datetime.strftime(
            local, '%Y-%m-%d %H:%M:%S'), "2019-12-31 08:00:00")

    def test_current_week(self):
        """获取当前第几周"""
        print(timeutil.get_current_week())

if __name__ == "__main__":
    unittest.main()
