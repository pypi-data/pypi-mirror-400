import unittest

from rython import Default, From, derive, impl


@impl(From, for_type=int)
class IntFromString:
    def from_(self, s: str) -> int:
        return int(s)


@derive(Default)
class MyConfig:
    host: str = "localhost"
    port: int = 8080


class TestTraits(unittest.TestCase):
    def test_from(self):
        val = From(int).from_("42")
        self.assertEqual(val, 42)

    def test_default(self):
        c = Default(MyConfig).default()
        self.assertEqual(c.host, "localhost")
        self.assertEqual(c.port, 8080)

    def test_default_type_error(self):
        # We need to derive Default to register the implementation
        @derive(Default)
        class NoDefaults:
            def __init__(self, x):
                self.x = x

        # Now Default(NoDefaults) should find the impl, but default() should fail
        with self.assertRaises(TypeError):
            Default(NoDefaults).default()


if __name__ == "__main__":
    unittest.main()
