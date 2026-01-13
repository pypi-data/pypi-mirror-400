import pytest
from yadu4ever import say_hello, __version__


def test_say_hello_default():
    """Test say_hello with default argument."""
    result = say_hello()
    assert result == "Hello, world! from Yadu4ever pkg."


def test_say_hello_custom_name():
    """Test say_hello with a custom name."""
    result = say_hello("Alice")
    assert result == "Hello, Alice! from Yadu4ever pkg."


def test_say_hello_return_type():
    """Test that say_hello returns a string."""
    result = say_hello("Bob")
    assert isinstance(result, str)


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.0.2"