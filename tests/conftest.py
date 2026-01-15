"""Shared pytest fixtures for all tests."""

from __future__ import annotations

import signal
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import docker
import pytest


@contextmanager
def timeout_context(seconds: int):
    """Context manager for timing out operations.

    Args:
        seconds: Timeout duration in seconds.

    Raises:
        TimeoutError: If operation exceeds timeout.
    """

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


@pytest.fixture(scope="session")
def docker_client() -> docker.DockerClient:
    """Provide Docker client for entire test session.

    Yields:
        Docker client instance.
    """
    return docker.from_env()


@pytest.fixture
def temp_csv_file(tmp_path: Path) -> Generator[str, None, None]:
    """Provide a temporary CSV file path.

    Args:
        tmp_path: pytest tmp_path fixture.

    Yields:
        Path to temporary CSV file.
    """
    csv_path = tmp_path / "test_data.csv"
    yield str(csv_path)
    # Cleanup (pytest handles tmp_path deletion)


@pytest.fixture
def sample_dataframe():
    """Provide a sample LMP dataframe for testing.

    Returns:
        DataFrame with mock LMP data.
    """
    import pandas as pd

    data = {
        0: ["Settlement Point", "HB_HOUSTON", "LZ_HOUSTON"],
        1: [50.0, 51.25, 48.75],
        3: [2.5, 2.75, 2.25],
    }
    return pd.DataFrame(data)
