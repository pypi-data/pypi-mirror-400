import inspect
from typing import Any, Callable, Dict, Type

from .monads import (
    Err as Err,
)
from .monads import (
    Nothing as Nothing,
)
from .monads import (
    Ok as Ok,
)
from .monads import (
    Option as Option,
)
from .monads import (
    Result as Result,
)
from .monads import (
    Some as Some,
)

# Registry to store implementations: {TraitClass: {Type: ImplementationClass}}
_IMPL_REGISTRY: Dict[Type, Dict[Type, Type]] = {}
# Registry for derive handlers: {TraitClass: HandlerFunction}
_DERIVE_REGISTRY: Dict[Type, Callable] = {}


class Trait:
    """
    Base class for all traits.
    Provides the correct __init__ signature for static analysis.
    """

    def __init__(self, obj: Any) -> None:
        pass


def trait(cls: Type) -> Any:
    """
    Decorator to mark a class as a Trait.
    Returns a Proxy class that wraps an object and finds the correct implementation.
    Dispatches methods to the implementation for that object's type.
    """

    class TraitProxy:
        def __init__(self, obj: Any):
            self._obj = obj

        def __getattr__(self, name: str):
            # Find implementation for type(self._obj)
            obj_type = type(self._obj)

            # Look up in registry
            impls = _IMPL_REGISTRY.get(self.__class__)
            if not impls:
                raise NotImplementedError(
                    f"No implementations found for trait {self.__class__.__name__}"
                )

            # 1. Try exact match for type(obj)
            impl_cls = impls.get(obj_type)

            # 2. If obj is itself a type (e.g. From(int)), check if implementations exists for obj
            if not impl_cls and isinstance(self._obj, type):
                impl_cls = impls.get(self._obj)

            # 3. MRO Lookup (for type(obj))
            if not impl_cls:
                for base in inspect.getmro(obj_type):
                    if base in impls:
                        impl_cls = impls[base]
                        break

            if not impl_cls:
                raise NotImplementedError(
                    f"Trait {self.__class__.__name__} not implemented for type {obj_type.__name__}"
                )

            # Get the method from the implementation class
            attr = getattr(impl_cls, name, None)
            if not attr:
                raise AttributeError(f"Trait {self.__class__.__name__} has no method {name}")

            # Return a wrapper that passes self._obj as the first argument
            return lambda *args, **kwargs: attr(self._obj, *args, **kwargs)

    # Copy name and module to make it look like the original class
    TraitProxy.__name__ = cls.__name__
    TraitProxy.__qualname__ = cls.__qualname__
    TraitProxy.__module__ = cls.__module__

    return TraitProxy


def impl(trait_cls: Type, for_type: Type) -> Callable[[Type], Type]:
    """
    Decorator to register an implementation of a trait for a specific type.
    """

    def wrapper(impl_cls):
        if trait_cls not in _IMPL_REGISTRY:
            _IMPL_REGISTRY[trait_cls] = {}

        # Register the implementation
        _IMPL_REGISTRY[trait_cls][for_type] = impl_cls
        return impl_cls

    return wrapper


def derive(*traits: Type) -> Callable[[Type], Type]:
    """
    Decorator to automatically derive implementations for the given traits.
    """

    def wrapper(cls):
        for t in traits:
            handler = _DERIVE_REGISTRY.get(t)
            if handler:
                impl_cls = handler(cls)
                # Register the derived implementation
                if t not in _IMPL_REGISTRY:
                    _IMPL_REGISTRY[t] = {}
                _IMPL_REGISTRY[t][cls] = impl_cls
            else:
                raise NotImplementedError(f"No derive handler registered for trait {t.__name__}")
        return cls

    return wrapper


def register_derive(trait_cls, handler: Callable[[Type], Type]):
    _DERIVE_REGISTRY[trait_cls] = handler


# --- Built-in Debug Trait ---


@trait
class Debug(Trait):
    def fmt(self) -> str:
        raise NotImplementedError


def _derive_debug(cls):
    class DebugImpl:
        def fmt(self) -> str:
            # Simple default debug format: ClassName(attr=val, ...)
            attrs = vars(self)
            attrs_str = ", ".join(f"{k}={v!r}" for k, v in attrs.items())
            return f"{cls.__name__}({attrs_str})"

    return DebugImpl


register_derive(Debug, _derive_debug)


def has_impl(obj_or_type: Any, trait_cls: Type) -> bool:
    """
    Check if a type or object implements a specific trait.
    """
    if isinstance(obj_or_type, type):
        target_type = obj_or_type
    else:
        target_type = type(obj_or_type)

    impls = _IMPL_REGISTRY.get(trait_cls)
    if not impls:
        return False

    # Check exact match or MRO
    if target_type in impls:
        return True

    for base in inspect.getmro(target_type):
        if base in impls:
            return True

    return False


# noqa: E402
from .basic_traits import Default as Default  # noqa: E402
from .basic_traits import From as From  # noqa: E402
from .basic_traits import Into as Into  # noqa: E402
from .iterators import RyIterator as RyIterator  # noqa: E402
