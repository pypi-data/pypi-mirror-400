# Rython 🐍🦀

**Rython** is a Python framework that brings the power and safety of Rust's trait system and functional programming patterns to Python. It provides a robust way to define interfaces, implement them for existing types, and leverage monadic error handling and iterator adapters.

## ✨ Features

- **Traits & Implementations**: Define strict interfaces (`@trait`) and implement them for any type (`@impl`), even built-ins like `int` or `str`.
- **Introspection**: Check if an object implements a trait at runtime.
- **Derive Macros**: Automatically generate implementations for common traits (e.g., `@derive(Debug, Default)`).
- **Monads**: strictly typed `Option[T]` and `Result[T, E]` for safer control flow.
- **Iterators**: Rust-style lazy iterators (`RyIterator`) with chainable methods like `.map()`, `.filter()`, `.collect()`.
- **Type Safety**: Fully typed and compatible with static analysis tools like `mypy` and `pyrefly`.

## 📦 Installation

Rython is managed with `uv`. You can install it or add it to your project:

```bash
# Using uv
uv add rython

# Or install locally for development
git clone https://github.com/WeiNyn/rython.git
cd rython
uv sync
```

## 🚀 Quick Start

### Defining and Implementing Traits

To define a trait, decorate a class with `@trait` and inherit from `Trait`. This ensures full compatibility with static type checkers.

```python
from rython import trait, impl, Trait

# 1. Define a Trait
@trait
class Speak(Trait):
    def speak(self) -> str:
        raise NotImplementedError

class Dog:
    pass

class Cat:
    pass

# 2. Implement the Trait for types
@impl(Speak, for_type=Dog)
class DogSpeak:
    def speak(self) -> str:
        return "Woof!"

@impl(Speak, for_type=Cat)
class CatSpeak:
    def speak(self) -> str:
        return "Meow!"

# 3. Use the Trait
def make_it_speak(obj):
    # Syntax: Trait(object).method()
    print(Speak(obj).speak())

make_it_speak(Dog()) # Output: Woof!
make_it_speak(Cat()) # Output: Meow!
```

### Derive Macros

Automatically implement standard traits for your classes.

```python
from rython import derive, Debug, Default

@derive(Debug, Default)
class Config:
    host: str = "localhost"
    port: int = 8080

c = Default(Config).default()
print(Debug(c).fmt()) 
# Output: Config(host='localhost', port=8080)
```

### Monads: Option & Result

Replace `None` checks and exceptions with safe, expressive types.

```python
from rython import Option, Some, Nothing, Result, Ok, Err

# Option
def divide(a, b) -> Option[float]:
    if b == 0:
        return Nothing
    return Some(a / b)

result = divide(10, 2).map(lambda x: x * 2).unwrap_or(0.0)
print(result) # 10.0

# Result
def parse_int(s: str) -> Result[int, str]:
    try:
        return Ok(int(s))
    except ValueError:
        return Err(f"Invalid integer: {s}")

match parse_int("42"):
    case Ok(val): print(f"Parsed: {val}")
    case Err(e): print(f"Error: {e}")
```

### Iterators

Chainable, lazy transformations on collections.

```python
from rython import RyIterator

data = [1, 2, 3, 4, 5]
squared_evens = (
    RyIterator(data)
    .filter(lambda x: x % 2 == 0)
    .map(lambda x: x * x)
    .collect(list)
)
print(squared_evens) # [4, 16]
```

## 🛠️ Development

This project uses `uv` for dependency management and `just` as a command runner.

```bash
# Install dependencies
uv sync

# Run all checks (lint, format, types, tests)
just check

# Run tests only
just test

# Fix linting issues
just lint
```

## 📄 License

MIT
