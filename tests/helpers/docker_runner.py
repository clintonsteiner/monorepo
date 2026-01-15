"""Docker container execution helpers for tests."""

from __future__ import annotations

import docker


class DockerContainerRunner:
    """Helper for running commands in Docker containers."""

    def __init__(self, client: docker.DockerClient, image_name: str, timeout_seconds: int = 5):
        """Initialize container runner.

        Args:
            client: Docker client.
            image_name: Name of the Docker image to run.
            timeout_seconds: Command execution timeout in seconds.
        """
        self.client = client
        self.image_name = image_name
        self.timeout = timeout_seconds

    def run_command(self, command: list[str]) -> bytes:
        """Run a command in the container.

        Args:
            command: Command and arguments to execute.

        Returns:
            Command output as bytes.

        Raises:
            TestError: If command execution fails.
        """
        try:
            output = self.client.containers.run(
                self.image_name,
                command,
                remove=True,
                stdout=True,
                stderr=True,
                entrypoint="",
            )
            return self._to_bytes(output)
        except docker.errors.ContainerError as e:
            raise TestError(f"Container command failed: {e}") from e
        except docker.errors.ImageNotFound:
            raise TestError(f"Docker image not found: {self.image_name}") from None

    @staticmethod
    def _to_bytes(output: bytes | str) -> bytes:
        """Convert output to bytes.

        Args:
            output: Output from Docker.

        Returns:
            Output as bytes.
        """
        return output if isinstance(output, bytes) else output.encode()

    @staticmethod
    def to_str(output: bytes | str) -> str:
        """Convert output to string.

        Args:
            output: Output from Docker.

        Returns:
            Output as string.
        """
        return output.decode() if isinstance(output, bytes) else output


class TestError(Exception):
    """Base test error."""

    pass
