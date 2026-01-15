"""Tests for example_lib.utils module."""

from example_lib.utils import format_output, validate_input


def test_validate_input_valid():
    """Test validate_input with valid input."""
    assert validate_input("test") is True
    assert validate_input("hello world") is True


def test_validate_input_invalid():
    """Test validate_input with invalid input."""
    assert validate_input("") is False
    assert validate_input("   ") is False


def test_format_output():
    """Test format_output function."""
    data = {"name": "test", "value": "123"}
    result = format_output(data)
    assert "name: test" in result
    assert "value: 123" in result


def test_format_output_empty():
    """Test format_output with empty dict."""
    result = format_output({})
    assert result == ""
