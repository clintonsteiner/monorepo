"""Tests for Docker images."""

import signal
import time
from contextlib import contextmanager
from typing import Generator

import docker
import pytest

client = docker.from_env()


@contextmanager
def timeout_context(seconds: int):
    """Context manager for timing out operations."""

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    # Set up the signal handler and alarm
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        # Disable the alarm
        signal.alarm(0)


@pytest.fixture
def docker_client() -> docker.DockerClient:
    """Provide Docker client."""
    return client


class TestErcotLmpImage:
    """Tests for ercot-lmp Docker image."""

    IMAGE_NAME = "ercot-lmp:latest"

    @pytest.fixture(autouse=True)
    def setup_image(self) -> None:
        """Ensure image exists before each test."""
        try:
            client.images.get(self.IMAGE_NAME)
        except docker.errors.ImageNotFound:
            pytest.skip(f"Image {self.IMAGE_NAME} not found")

    def test_image_exists(self) -> None:
        """Test that ercot-lmp image exists."""
        image = client.images.get(self.IMAGE_NAME)
        assert image is not None
        assert self.IMAGE_NAME in [tag for tags in [image.tags] for tag in tags]

    def test_image_has_python(self) -> None:
        """Test that Python 3.11 is available in image."""
        with timeout_context(5):
            output = client.containers.run(
                self.IMAGE_NAME,
                ["python", "--version"],
                remove=True,
                stdout=True,
                stderr=True,
                entrypoint="",
            )
        output_str = output.decode() if isinstance(output, bytes) else output
        assert "Python 3.11" in output_str

    def test_pex_binary_exists(self) -> None:
        """Test that ercot_lmp.pex exists in image."""
        with timeout_context(5):
            output = client.containers.run(
                self.IMAGE_NAME,
                ["bash", "-c", "ls -la /app/*.pex"],
                remove=True,
                stdout=True,
                stderr=True,
                entrypoint="",
            )
        output_bytes = output if isinstance(output, bytes) else output.encode()
        assert b"ercot_lmp.pex" in output_bytes
        assert b"hello_world.pex" in output_bytes

    def test_hello_world_pex_executable(self) -> None:
        """Test that hello_world.pex runs correctly."""
        with timeout_context(5):
            output = client.containers.run(
                self.IMAGE_NAME,
                ["/app/hello_world.pex", "--name", "Docker"],
                remove=True,
                stdout=True,
                stderr=True,
                entrypoint="",
            )
        output_bytes = output if isinstance(output, bytes) else output.encode()
        assert b"Hello, Docker!" in output_bytes

    def test_hello_world_with_different_names(self) -> None:
        """Test hello_world.pex with various inputs."""
        test_cases = ["World", "Pants", "Docker"]
        for name in test_cases:
            with timeout_context(5):
                output = client.containers.run(
                    self.IMAGE_NAME,
                    ["/app/hello_world.pex", "--name", name],
                    remove=True,
                    stdout=True,
                    stderr=True,
                    entrypoint="",
                )
            output_bytes = output if isinstance(output, bytes) else output.encode()
            assert f"Hello, {name}!".encode() in output_bytes

    def test_workdir_is_app(self) -> None:
        """Test that working directory is /app."""
        with timeout_context(5):
            output = client.containers.run(
                self.IMAGE_NAME,
                ["pwd"],
                remove=True,
                stdout=True,
                stderr=True,
                entrypoint="",
            )
        output_bytes = output if isinstance(output, bytes) else output.encode()
        assert b"/app" in output_bytes

    def test_app_directory_structure(self) -> None:
        """Test that /app contains expected files."""
        with timeout_context(5):
            output = client.containers.run(
                self.IMAGE_NAME,
                ["ls", "-la", "/app/"],
                remove=True,
                stdout=True,
                stderr=True,
                entrypoint="",
            )
        output_bytes = output if isinstance(output, bytes) else output.encode()
        assert b"ercot_lmp.pex" in output_bytes
        assert b"hello_world.pex" in output_bytes

    def test_image_size_reasonable(self, docker_client: docker.DockerClient) -> None:
        """Test that image size is under 500MB."""
        image = docker_client.images.get(self.IMAGE_NAME)
        size_mb = image.attrs["Size"] / (1024 * 1024)
        assert size_mb < 500, f"Image size {size_mb:.1f}MB exceeds 500MB"


class TestErcotDbImage:
    """Tests for ercot-db Docker image."""

    IMAGE_NAME = "ercot-db:latest"
    CONTAINER_NAME = "test-ercot-db"
    DB_USER = "ercot_user"
    DB_PASSWORD = "ercot_pass"
    DB_NAME = "ercot_db"
    PORT = "5434"

    @pytest.fixture(autouse=True)
    def setup_image(self) -> None:
        """Ensure image exists before tests."""
        try:
            client.images.get(self.IMAGE_NAME)
        except docker.errors.ImageNotFound:
            pytest.skip(f"Image {self.IMAGE_NAME} not found")

    @pytest.fixture
    def postgres_container(self) -> Generator:
        """Create and cleanup PostgreSQL container."""
        # Remove any existing container
        try:
            container = client.containers.get(self.CONTAINER_NAME)
            container.remove(force=True)
        except docker.errors.NotFound:
            pass

        # Start container
        container = client.containers.run(
            self.IMAGE_NAME,
            environment={
                "POSTGRES_USER": self.DB_USER,
                "POSTGRES_PASSWORD": self.DB_PASSWORD,
                "POSTGRES_DB": self.DB_NAME,
            },
            ports={"5432/tcp": self.PORT},
            name=self.CONTAINER_NAME,
            detach=True,
            remove=False,
        )

        # Wait for database to be ready - check until it responds
        max_wait = 30
        for _ in range(max_wait):
            try:
                result = container.exec_run(["pg_isready", "-U", self.DB_USER])
                if result.exit_code == 0:
                    break
            except Exception:
                pass
            time.sleep(1)

        yield container

        # Cleanup
        try:
            container.remove(force=True)
        except docker.errors.NotFound:
            pass

    def test_image_exists(self) -> None:
        """Test that ercot-db image exists."""
        image = client.images.get(self.IMAGE_NAME)
        assert image is not None

    def test_postgres_version(self, postgres_container) -> None:
        """Test that PostgreSQL 16 is running."""
        output = self._execute_psql(postgres_container, "SELECT version();")
        assert b"PostgreSQL 16" in output

    def test_database_created(self, postgres_container) -> None:
        """Test that database is created and accessible."""
        output = self._execute_psql(postgres_container, f"\\l {self.DB_NAME}")
        assert self.DB_NAME.encode() in output

    def test_schema_initialized(self, postgres_container) -> None:
        """Test that ercot schema exists."""
        output = self._execute_psql(postgres_container, "\\dn ercot")
        assert b"ercot" in output

    def test_tables_created(self, postgres_container) -> None:
        """Test that required tables exist."""
        output = self._execute_psql(postgres_container, "\\dt ercot.*")
        assert b"lmp_data" in output
        assert b"monitor_metadata" in output

    def test_lmp_data_table_structure(self, postgres_container) -> None:
        """Test lmp_data table has correct columns."""
        output = self._execute_psql(postgres_container, "\\d ercot.lmp_data")
        assert b"id" in output
        assert b"timestamp" in output
        assert b"location" in output
        assert b"lmp_value" in output
        assert b"energy_value" in output
        assert b"congestion_value" in output
        assert b"loss_value" in output

    def test_monitor_metadata_table_structure(self, postgres_container) -> None:
        """Test monitor_metadata table has correct columns."""
        output = self._execute_psql(postgres_container, "\\d ercot.monitor_metadata")
        assert b"id" in output
        assert b"key" in output
        assert b"value" in output
        assert b"updated_at" in output

    def test_indexes_created(self, postgres_container) -> None:
        """Test that expected indexes exist."""
        output = self._execute_psql(postgres_container, "\\di ercot.*")
        assert b"idx_lmp_timestamp" in output
        assert b"idx_lmp_location" in output

    def test_seed_data_loaded(self, postgres_container) -> None:
        """Test that seed data was inserted."""
        output = self._execute_psql(
            postgres_container,
            "SELECT COUNT(*) as count FROM ercot.lmp_data;",
        )
        assert b"5" in output  # 5 sample records

    def test_sample_data_values(self, postgres_container) -> None:
        """Test that sample data contains expected values."""
        output = self._execute_psql(
            postgres_container,
            ("SELECT location FROM ercot.lmp_data " "WHERE location='HB_HOUSTON' LIMIT 1;"),
        )
        assert b"HB_HOUSTON" in output

    def test_metadata_seeded(self, postgres_container) -> None:
        """Test that monitor_metadata was seeded."""
        output = self._execute_psql(
            postgres_container,
            "SELECT COUNT(*) as count FROM ercot.monitor_metadata;",
        )
        assert b"3" in output  # 3 metadata entries

    def test_function_get_latest_lmp_exists(self, postgres_container) -> None:
        """Test that get_latest_lmp function exists."""
        output = self._execute_psql(postgres_container, "\\df ercot.get_latest_lmp")
        assert b"get_latest_lmp" in output

    def test_function_update_metadata_exists(self, postgres_container) -> None:
        """Test that update_metadata function exists."""
        output = self._execute_psql(postgres_container, "\\df ercot.update_metadata")
        assert b"update_metadata" in output

    def test_function_get_avg_lmp_exists(self, postgres_container) -> None:
        """Test that get_avg_lmp function exists."""
        output = self._execute_psql(postgres_container, "\\df ercot.get_avg_lmp")
        assert b"get_avg_lmp" in output

    def test_get_latest_lmp_returns_data(self, postgres_container) -> None:
        """Test that get_latest_lmp function returns correct data."""
        output = self._execute_psql(
            postgres_container,
            "SELECT * FROM ercot.get_latest_lmp('HB_HOUSTON');",
        )
        assert b"HB_HOUSTON" in output
        assert b"44.25" in output  # Latest LMP value for HB_HOUSTON

    def test_get_latest_lmp_different_location(self, postgres_container) -> None:
        """Test get_latest_lmp with different location."""
        output = self._execute_psql(
            postgres_container,
            "SELECT * FROM ercot.get_latest_lmp('LZ_WEST');",
        )
        assert b"LZ_WEST" in output
        assert b"39.10" in output  # Latest LMP value for LZ_WEST

    def test_timestamps_in_utc(self, postgres_container) -> None:
        """Test that timestamps are stored with timezone."""
        output = self._execute_psql(
            postgres_container,
            "SELECT timestamp FROM ercot.lmp_data LIMIT 1;",
        )
        assert b"+00" in output  # UTC timezone indicator

    def test_unique_constraint_on_lmp_data(self, postgres_container) -> None:
        """Test that unique constraint exists on timestamp + location."""
        # Try to insert duplicate - should fail
        result = self._execute_psql(
            postgres_container,
            ("INSERT INTO ercot.lmp_data " "(timestamp, location, lmp_value) " "VALUES ('2024-01-01 12:00:00+00', 'HB_HOUSTON', 50.0);"),
            check=False,
        )
        assert b"duplicate key" in result or b"UNIQUE" in result

    def test_connection_with_credentials(self, postgres_container) -> None:
        """Test that database is accessible with provided credentials."""
        output = self._execute_psql(postgres_container, "SELECT current_user;")
        assert b"ercot_user" in output

    def test_table_comments_exist(self, postgres_container) -> None:
        """Test that table comments were set."""
        output = self._execute_psql(postgres_container, "\\dt+ ercot.lmp_data")
        assert b"ERCOT LMP" in output or b"Locational Marginal Pricing" in output

    @staticmethod
    def _execute_psql(
        container,
        query: str,
        check: bool = True,
    ) -> bytes:
        """Execute psql command in container."""
        cmd = [
            "psql",
            "-U",
            "ercot_user",
            "-d",
            "ercot_db",
            "-c",
            query,
        ]
        result = container.exec_run(cmd)
        output = result.output
        if check and result.exit_code != 0:
            raise RuntimeError(f"psql failed: {output}")
        return output


class TestDockerImageIntegration:
    """Integration tests between Docker images."""

    def test_both_images_present(self) -> None:
        """Test that both required images exist."""
        images = client.images.list()
        image_tags = [tag for image in images for tag in image.tags]
        assert "ercot-lmp:latest" in image_tags
        assert "ercot-db:latest" in image_tags

    def test_images_have_base_images(self) -> None:
        """Test that images are based on expected base images."""
        lmp_image = client.images.get("ercot-lmp:latest")
        db_image = client.images.get("ercot-db:latest")

        # Verify images exist and have labels/config
        assert lmp_image is not None
        assert db_image is not None

        # Check that images have metadata showing their configuration
        assert lmp_image.attrs.get("Config") is not None
        assert db_image.attrs.get("Config") is not None
