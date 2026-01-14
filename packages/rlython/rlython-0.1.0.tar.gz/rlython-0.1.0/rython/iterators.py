from typing import Callable, Iterable, TypeVar, cast

from .monads import Nothing, Option, Some

T = TypeVar("T")
U = TypeVar("U")


class RyIterator(Iterable[T]):
    """
    A Rust-like Iterator wrapper around Python iterables.
    """

    def __init__(self, iterable: Iterable[T]):
        self._iter = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self) -> T:
        return next(self._iter)

    def map(self, f: Callable[[T], U]) -> "RyIterator[U]":
        return RyIterator(map(f, self._iter))

    def filter(self, f: Callable[[T], bool]) -> "RyIterator[T]":
        return RyIterator(filter(f, self._iter))

    def collect(self, type_ctor: Callable[[Iterable[T]], U] = cast(Callable, list)) -> U:
        return type_ctor(self._iter)

    def next(self) -> Option[T]:
        try:
            return Some(next(self._iter))
        except StopIteration:
            return Nothing

    def fold(self, init: U, f: Callable[[U, T], U]) -> U:
        acc = init
        for item in self._iter:
            acc = f(acc, item)
        return acc

    def take(self, n: int) -> "RyIterator[T]":
        def _take_gen():
            for _, item in zip(range(n), self._iter):
                yield item

        return RyIterator(_take_gen())

    def skip(self, n: int) -> "RyIterator[T]":
        try:
            for _ in range(n):
                next(self._iter)
        except StopIteration:
            pass
        return self
