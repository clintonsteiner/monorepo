"""Tests for example_lib.core module."""

from example_lib.core import ExampleClass, process_data


def test_example_class_init():
    """Test ExampleClass initialization."""
    obj = ExampleClass("test", 10)
    assert obj.name == "test"
    assert obj.value == 10


def test_example_class_default_value():
    """Test ExampleClass with default value."""
    obj = ExampleClass("test")
    assert obj.value == 0


def test_increment():
    """Test increment method."""
    obj = ExampleClass("test", 5)
    result = obj.increment(3)
    assert result == 8
    assert obj.value == 8


def test_increment_default():
    """Test increment with default amount."""
    obj = ExampleClass("test", 5)
    result = obj.increment()
    assert result == 6


def test_repr():
    """Test string representation."""
    obj = ExampleClass("test", 42)
    assert repr(obj) == "ExampleClass(name='test', value=42)"


def test_process_data():
    """Test process_data function."""
    result = process_data([1, 2, 3])
    assert result == [2, 4, 6]


def test_process_data_empty():
    """Test process_data with empty list."""
    result = process_data([])
    assert result == []
