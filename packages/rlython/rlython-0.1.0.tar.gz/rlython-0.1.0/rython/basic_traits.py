from typing import Any, Generic, Type, TypeVar

from . import Trait, trait

T = TypeVar("T")

# --- Default ---


@trait
class Default(Generic[T], Trait):
    def default(self) -> T:
        raise NotImplementedError


# --- From / Into ---


@trait
class From(Generic[T], Trait):
    def from_(self, value: Any) -> T:
        raise NotImplementedError


@trait
class Into(Generic[T], Trait):
    def into(self, target_type: Type[T]) -> T:
        raise NotImplementedError


# Blanket Implementation: If From is implemented, Into is automatically implemented.
# This is tricky because `Into` works on the SOURCE object, while `From` works on the TARGET type.
# e.g.
# class UserFromDict(From): ... -> User.from_(dict)
# we want dict.into(User) -> User

# To support `obj.into(TargetType)`, we need to find if `TargetType`
# implements `From` for `type(obj)`.
# This is "blanket implementation" which our current simple registry doesn't fully support yet.
# We will implement `Into` manually or via a helper for now.

# Let's implement a 'smart' Into that looks up From.
# But Into needs to be implemented for the source type.


def _into_impl_handler(obj, target_type):
    # Check if target_type implements From for type(obj)
    # We need to look up: Impl(From, for_type=target_type) ?? No.
    # From is: class XFromY: def from_(self, y) -> X
    # It is usually: Impl(From, for_type=X) ? NO.

    # Rust: impl From<Y> for X.
    # Rython: @impl(From, for_type=X) class XFromY: def from_(self, y): ...

    # Wait, Rython `trait` dispatch is: Trait(obj).method()
    # So `From(X).from_(y)`

    # If we want `y.into(X)`:
    # It should mean `Into(y).into(X)`
    # And we want that to call `From(X).from_(y)`

    # Let's see if we can implement a generic Into for everything that has a matching From?
    # In Rython, we can't easily iterate all types.
    # But `Into` logic can be dynamic.

    # If we use `Into(y).into(X)`:
    # The implementation for `Into` for type `type(y)` could be dynamic?
    pass


def _derive_default(cls):
    """
    Derive Default for a class by calling its constructor with no arguments
    OR using field defaults (if dataclass-like).
    """
    # For simplicity, let's assume it initializes with default values of fields
    # if they are annotated and have defaults.

    # 1. Check if it has type hints and defaults
    # sig = inspect.signature(cls)

    class DefaultImpl:
        def default(self) -> Any:
            # We want to return a NEW instance of cls.
            # Does cls() work?
            try:
                # Try calling constructor with no args
                return cls()
            except TypeError:
                # If that fails, maybe we can construct it using parameter defaults?
                # But python's default args are handled by cls() if they exist.
                # If cls() failed, it means required args are missing.
                raise TypeError(
                    f"Cannot derive Default for {cls.__name__}: "
                    "constructor requires arguments without defaults."
                )

    return DefaultImpl


from . import register_derive  # noqa: E402

register_derive(Default, _derive_default)
