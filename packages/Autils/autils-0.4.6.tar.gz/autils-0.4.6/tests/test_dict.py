from autils.dict import Dict
import unittest


class TestDict(unittest.TestCase):

    def test_reverse_dict(self):
        d = {"a": "A", "b": "B"}
        b = Dict.reverse_dict(d)
        self.assertDictEqual(b, {"A": "a", "B": "b"})


if __name__ == "__main__":
    unittest.main()
