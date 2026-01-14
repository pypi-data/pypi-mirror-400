import unittest

from rython import Err, Nothing, Ok, Result, Some


class TestMonads(unittest.TestCase):
    def test_option(self):
        x = Some(10)
        self.assertTrue(x.is_some())
        self.assertFalse(x.is_none())
        self.assertEqual(x.unwrap(), 10)

        y = Nothing
        self.assertTrue(y.is_none())
        self.assertFalse(y.is_some())
        self.assertEqual(y.unwrap_or(5), 5)

    def test_option_map(self):
        x = Some(10)
        y = x.map(lambda v: v * 2)
        self.assertEqual(y, Some(20))

        z = Nothing.map(lambda v: v * 2)
        self.assertEqual(z, Nothing)

    def test_result(self):
        x: Result[int, str] = Ok(200)
        self.assertTrue(x.is_ok())
        self.assertEqual(x.unwrap(), 200)

        e: Result[int, str] = Err("Bad Request")
        self.assertTrue(e.is_err())
        self.assertEqual(e.unwrap_err(), "Bad Request")
        with self.assertRaises(ValueError):
            e.unwrap()


if __name__ == "__main__":
    unittest.main()
