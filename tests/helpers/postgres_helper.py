"""PostgreSQL database test helper."""

from __future__ import annotations

import time

import docker


class PostgresTestHelper:
    """Helper for testing PostgreSQL containers."""

    def __init__(
        self,
        container: docker.models.containers.Container,
        db_user: str = "ercot_user",
        db_name: str = "ercot_db",
        max_wait_seconds: int = 30,
    ):
        """Initialize PostgreSQL test helper.

        Args:
            container: Running PostgreSQL container.
            db_user: Database username.
            db_name: Database name.
            max_wait_seconds: Max seconds to wait for DB readiness.
        """
        self.container = container
        self.db_user = db_user
        self.db_name = db_name
        self.max_wait = max_wait_seconds
        self._ensure_ready()

    def _ensure_ready(self) -> None:
        """Wait for database to be ready."""
        for attempt in range(self.max_wait):
            try:
                result = self.container.exec_run(["pg_isready", "-U", self.db_user])
                if result.exit_code == 0:
                    return
            except Exception:
                pass
            time.sleep(1)
        raise TimeoutError(f"PostgreSQL not ready after {self.max_wait} seconds")

    def execute_query(self, query: str, check: bool = True) -> bytes:
        """Execute SQL query in database.

        Args:
            query: SQL query or psql command to execute.
            check: If True, raise on non-zero exit code.

        Returns:
            Command output as bytes.

        Raises:
            RuntimeError: If query execution fails and check=True.
        """
        cmd = ["psql", "-U", self.db_user, "-d", self.db_name, "-c", query]
        result = self.container.exec_run(cmd)

        if check and result.exit_code != 0:
            raise RuntimeError(f"psql failed with code {result.exit_code}: {result.output}")

        return result.output

    def assert_query_contains(self, query: str, expected: bytes | str) -> None:
        """Assert that query output contains expected text.

        Args:
            query: SQL query or psql command.
            expected: Expected text (as bytes or str).

        Raises:
            AssertionError: If expected text not in output.
        """
        output = self.execute_query(query)
        expected_bytes = expected if isinstance(expected, bytes) else expected.encode()
        assert expected_bytes in output, f"Expected {expected_bytes} not found in {output}"

    def assert_query_not_contains(self, query: str, unexpected: bytes | str) -> None:
        """Assert that query output does NOT contain text.

        Args:
            query: SQL query or psql command.
            unexpected: Text that should NOT appear.

        Raises:
            AssertionError: If unexpected text found in output.
        """
        output = self.execute_query(query)
        unexpected_bytes = unexpected if isinstance(unexpected, bytes) else unexpected.encode()
        assert unexpected_bytes not in output, f"Unexpected {unexpected_bytes} found in {output}"
