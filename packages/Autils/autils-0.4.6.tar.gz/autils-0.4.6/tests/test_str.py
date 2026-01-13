import unittest
from autils import randomstr


class Str(unittest.TestCase):

    def test_gen(self):
        self.assertEqual(len(randomstr.generate(16)), 16)

    def test_gen_digits(self):
        print(randomstr.generate_digits(16))

    def test_gen_strs(self):
        print(randomstr.generate_strs(32))

    def test_alphabet_number(self):
        self.assertEqual(randomstr.get_alphabet_number("Z"), 26)


if __name__ == "__main__":
    unittest.main()
