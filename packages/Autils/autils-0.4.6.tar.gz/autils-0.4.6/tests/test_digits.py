
from autils import Digits
import unittest


class TestSign(unittest.TestCase):

    def test_digits(self):
        self.assertEqual(Digits.convert_float_to_str(
            0.000000015), "0.000000015")


if __name__ == '__main__':
    unittest.main()
