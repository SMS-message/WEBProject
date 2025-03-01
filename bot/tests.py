import unittest
from data.functions import make_queue


class MyTestCase(unittest.TestCase):
    def test_queue(self):
        result = [1, 2, 3, 4, 5, 6]
        self.assertEqual(make_queue(2140097795), result)


if __name__ == '__main__':
    unittest.main()
