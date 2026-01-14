from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


class Option(Generic[T]):
    def is_some(self) -> bool:
        raise NotImplementedError

    def is_none(self) -> bool:
        raise NotImplementedError

    def unwrap(self) -> T:
        raise NotImplementedError

    def unwrap_or(self, default: T) -> T:
        raise NotImplementedError

    def map(self, f: Callable[[T], U]) -> "Option[U]":
        raise NotImplementedError


class Some(Option[T]):
    __match_args__ = ("value",)

    def __init__(self, value: T):
        self.value = value

    def is_some(self) -> bool:
        return True

    def is_none(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value

    def map(self, f: Callable[[T], U]) -> "Option[U]":
        return Some(f(self.value))

    def __repr__(self):
        return f"Some({self.value!r})"

    def __eq__(self, other):
        return isinstance(other, Some) and self.value == other.value


class NothingType(Option[Any]):
    def is_some(self) -> bool:
        return False

    def is_none(self) -> bool:
        return True

    def unwrap(self) -> Any:
        raise ValueError("Called unwrap on Nothing")

    def unwrap_or(self, default: Any) -> Any:
        return default

    def map(self, f: Callable[[Any], U]) -> "Option[U]":
        return self

    def __repr__(self):
        return "Nothing"

    def __eq__(self, other):
        return isinstance(other, NothingType)


Nothing = NothingType()

# --- Result ---


class Result(Generic[T, E]):
    def is_ok(self) -> bool:
        raise NotImplementedError

    def is_err(self) -> bool:
        raise NotImplementedError

    def unwrap(self) -> T:
        raise NotImplementedError

    def unwrap_err(self) -> E:
        raise NotImplementedError


class Ok(Result[T, E]):
    __match_args__ = ("value",)

    def __init__(self, value: T):
        self.value = value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.value

    def unwrap_err(self) -> E:
        raise ValueError(f"Called unwrap_err on Ok: {self.value}")

    def __repr__(self):
        return f"Ok({self.value!r})"

    def __eq__(self, other):
        return isinstance(other, Ok) and self.value == other.value


class Err(Result[T, E]):
    __match_args__ = ("error",)

    def __init__(self, error: E):
        self.error = error

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> T:
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_err(self) -> E:
        return self.error

    def __repr__(self):
        return f"Err({self.error!r})"

    def __eq__(self, other):
        return isinstance(other, Err) and self.error == other.error
