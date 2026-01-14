import unittest

from rython import Trait, has_impl, impl, trait


@trait
class Speak(Trait):
    def speak(self) -> str:
        raise NotImplementedError


class Dog:
    pass


class Cat:
    pass


@impl(Speak, for_type=Dog)
class DogSpeak:
    def speak(self) -> str:
        return "Woof"


@impl(Speak, for_type=Cat)
class CatSpeak:
    def speak(self) -> str:
        return "Meow"


class TestCore(unittest.TestCase):
    def test_basic_trait(self):
        d = Dog()
        c = Cat()
        self.assertEqual(Speak(d).speak(), "Woof")
        self.assertEqual(Speak(c).speak(), "Meow")

    def test_missing_impl(self):
        class Bird:
            pass

        b = Bird()
        with self.assertRaises(NotImplementedError):
            Speak(b).speak()

    def test_introspection(self):
        d = Dog()
        self.assertTrue(has_impl(d, Speak))
        self.assertTrue(has_impl(Dog, Speak))

        class Bird:
            pass

        self.assertFalse(has_impl(Bird(), Speak))


if __name__ == "__main__":
    unittest.main()
