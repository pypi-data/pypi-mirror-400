# from autils import OST
from autils.ost import OST
import unittest

class TestOST(unittest.TestCase):

    def test_mac(self):
        self.assertTrue(isinstance(OST.get_mac(),str))

    def test_ip(self):
        self.assertTrue(isinstance(OST.get_address(),str))

if __name__ == '__main__':
    unittest.main()