"""Yadu4ever package example."""
__all__ = ["say_hello", "__version__"]

__version__ = "0.0.2"

def say_hello(name: str = "world") -> str:
    """Return a greeting string."""
    return f"Hello, {name}! from Yadu4ever pkg."

