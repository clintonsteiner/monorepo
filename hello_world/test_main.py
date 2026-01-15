"""Tests for hello_world."""

import pytest
from hello_world.main import hello


def test_hello(capsys):
    """Test hello function."""
    hello("Test")
    captured = capsys.readouterr()
    assert captured.out == "Hello, Test!\n"


def test_hello_world(capsys):
    """Test hello with World."""
    hello("World")
    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\n"
