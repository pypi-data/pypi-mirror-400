import unittest

from rython import Nothing, RyIterator, Some


class TestIterators(unittest.TestCase):
    def test_basic_ops(self):
        data = [1, 2, 3, 4, 5]
        it = RyIterator(data)
        res = it.map(lambda x: x * 2).filter(lambda x: x > 5).collect()
        self.assertEqual(res, [6, 8, 10])

    def test_next_option(self):
        it = RyIterator([1])
        self.assertEqual(it.next(), Some(1))
        self.assertEqual(it.next(), Nothing)

    def test_fold(self):
        data = [1, 2, 3, 4]
        sum_val = RyIterator(data).fold(0, lambda acc, x: acc + x)
        self.assertEqual(sum_val, 10)

    def test_take_skip(self):
        data = [1, 2, 3, 4, 5]
        res = RyIterator(data).skip(2).take(2).collect()
        self.assertEqual(res, [3, 4])


if __name__ == "__main__":
    unittest.main()
