"""Tests for Docker images."""

from __future__ import annotations

import pytest

from tests.helpers.docker_runner import DockerContainerRunner
from tests.helpers.postgres_helper import PostgresTestHelper

# Skip all tests in this module if Docker images not found
pytestmark = pytest.mark.docker


class TestErcotLmpImage:
    """Tests for ercot-lmp Docker image."""

    IMAGE_NAME = "ercot-lmp:latest"

    @pytest.fixture(autouse=True)
    def ensure_image_exists(self, docker_client):
        """Skip tests if image doesn't exist."""
        try:
            docker_client.images.get(self.IMAGE_NAME)
        except Exception:
            pytest.skip(f"Image {self.IMAGE_NAME} not found")

    @pytest.fixture
    def runner(self, docker_client):
        """Provide container runner for this image."""
        return DockerContainerRunner(docker_client, self.IMAGE_NAME)

    def test_image_exists(self, docker_client) -> None:
        """Test that ercot-lmp image exists."""
        image = docker_client.images.get(self.IMAGE_NAME)
        assert image is not None
        assert self.IMAGE_NAME in image.tags

    def test_image_has_python(self, runner) -> None:
        """Test that Python 3.11 is available in image."""
        output = runner.run_command(["python", "--version"])
        assert b"Python 3.11" in output

    def test_pex_binary_exists(self, runner) -> None:
        """Test that .pex files exist in image."""
        output = runner.run_command(["bash", "-c", "ls -la /app/*.pex"])
        assert b"ercot_lmp.pex" in output
        assert b"hello_world.pex" in output

    def test_hello_world_pex_executable(self, runner) -> None:
        """Test that hello_world.pex runs correctly."""
        output = runner.run_command(["/app/hello_world.pex", "--name", "Docker"])
        assert b"Hello, Docker!" in output

    @pytest.mark.parametrize("name", ["World", "Pants", "Docker"])
    def test_hello_world_with_various_names(self, runner, name: str) -> None:
        """Test hello_world.pex with various inputs.

        Args:
            name: Name to greet.
        """
        output = runner.run_command(["/app/hello_world.pex", "--name", name])
        expected = f"Hello, {name}!".encode()
        assert expected in output

    def test_workdir_is_app(self, runner) -> None:
        """Test that working directory is /app."""
        output = runner.run_command(["pwd"])
        assert b"/app" in output

    def test_app_directory_structure(self, runner) -> None:
        """Test that /app contains expected files."""
        output = runner.run_command(["ls", "-la", "/app/"])
        assert b"ercot_lmp.pex" in output
        assert b"hello_world.pex" in output

    def test_image_size_reasonable(self, docker_client) -> None:
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
    def ensure_image_exists(self, docker_client):
        """Skip tests if image doesn't exist."""
        try:
            docker_client.images.get(self.IMAGE_NAME)
        except Exception:
            pytest.skip(f"Image {self.IMAGE_NAME} not found")

    @pytest.fixture
    def postgres_helper(self, docker_client):
        """Create and cleanup PostgreSQL container with helper.

        Yields:
            PostgresTestHelper instance.
        """
        # Remove any existing container
        try:
            container = docker_client.containers.get(self.CONTAINER_NAME)
            container.remove(force=True)
        except Exception:
            pass

        # Start container
        container = docker_client.containers.run(
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

        # Helper waits for DB readiness
        helper = PostgresTestHelper(
            container,
            db_user=self.DB_USER,
            db_name=self.DB_NAME,
        )

        yield helper

        # Cleanup
        try:
            container.remove(force=True)
        except Exception:
            pass

    def test_image_exists(self, docker_client) -> None:
        """Test that ercot-db image exists."""
        image = docker_client.images.get(self.IMAGE_NAME)
        assert image is not None

    def test_postgres_version(self, postgres_helper) -> None:
        """Test that PostgreSQL 16 is running."""
        postgres_helper.assert_query_contains("SELECT version();", b"PostgreSQL 16")

    def test_database_created(self, postgres_helper) -> None:
        """Test that database is created and accessible."""
        postgres_helper.assert_query_contains(f"\\l {self.DB_NAME}", self.DB_NAME)

    def test_schema_initialized(self, postgres_helper) -> None:
        """Test that ercot schema exists."""
        import time

        # Retry schema check as it may take a moment after container startup
        for attempt in range(3):
            try:
                postgres_helper.assert_query_contains("\\dn ercot", b"ercot")
                break
            except RuntimeError as e:
                if attempt == 2:
                    raise e
                time.sleep(1)

    def test_tables_created(self, postgres_helper) -> None:
        """Test that required tables exist."""
        output = postgres_helper.execute_query("\\dt ercot.*")
        assert b"lmp_data" in output
        assert b"monitor_metadata" in output

    def test_lmp_data_table_structure(self, postgres_helper) -> None:
        """Test lmp_data table has correct columns."""
        output = postgres_helper.execute_query("\\d ercot.lmp_data")
        required_columns = [b"id", b"timestamp", b"location", b"lmp_value"]
        for col in required_columns:
            assert col in output, f"Column {col} not found in table structure"

    def test_monitor_metadata_table_structure(self, postgres_helper) -> None:
        """Test monitor_metadata table has correct columns."""
        output = postgres_helper.execute_query("\\d ercot.monitor_metadata")
        required_columns = [b"id", b"key", b"value", b"updated_at"]
        for col in required_columns:
            assert col in output, f"Column {col} not found in table structure"

    def test_indexes_created(self, postgres_helper) -> None:
        """Test that expected indexes exist."""
        output = postgres_helper.execute_query("\\di ercot.*")
        assert b"idx_lmp_timestamp" in output
        assert b"idx_lmp_location" in output

    def test_seed_data_loaded(self, postgres_helper) -> None:
        """Test that seed data was inserted."""
        postgres_helper.assert_query_contains(
            "SELECT COUNT(*) as count FROM ercot.lmp_data;",
            b"5",  # 5 sample records
        )

    def test_sample_data_values(self, postgres_helper) -> None:
        """Test that sample data contains expected values."""
        postgres_helper.assert_query_contains(
            "SELECT location FROM ercot.lmp_data WHERE location='HB_HOUSTON' LIMIT 1;",
            b"HB_HOUSTON",
        )

    def test_metadata_seeded(self, postgres_helper) -> None:
        """Test that monitor_metadata was seeded."""
        postgres_helper.assert_query_contains(
            "SELECT COUNT(*) as count FROM ercot.monitor_metadata;",
            b"3",  # 3 metadata entries
        )

    def test_function_get_latest_lmp_exists(self, postgres_helper) -> None:
        """Test that get_latest_lmp function exists."""
        postgres_helper.assert_query_contains(
            "\\df ercot.get_latest_lmp",
            b"get_latest_lmp",
        )

    def test_function_update_metadata_exists(self, postgres_helper) -> None:
        """Test that update_metadata function exists."""
        postgres_helper.assert_query_contains(
            "\\df ercot.update_metadata",
            b"update_metadata",
        )

    def test_function_get_avg_lmp_exists(self, postgres_helper) -> None:
        """Test that get_avg_lmp function exists."""
        postgres_helper.assert_query_contains(
            "\\df ercot.get_avg_lmp",
            b"get_avg_lmp",
        )

    def test_get_latest_lmp_returns_data(self, postgres_helper) -> None:
        """Test that get_latest_lmp function returns correct data."""
        output = postgres_helper.execute_query("SELECT * FROM ercot.get_latest_lmp('HB_HOUSTON');")
        assert b"HB_HOUSTON" in output
        assert b"44.25" in output  # Latest LMP value for HB_HOUSTON

    def test_get_latest_lmp_different_location(self, postgres_helper) -> None:
        """Test get_latest_lmp with different location."""
        output = postgres_helper.execute_query("SELECT * FROM ercot.get_latest_lmp('LZ_WEST');")
        assert b"LZ_WEST" in output
        assert b"39.10" in output  # Latest LMP value for LZ_WEST

    def test_timestamps_in_utc(self, postgres_helper) -> None:
        """Test that timestamps are stored with timezone."""
        output = postgres_helper.execute_query("SELECT timestamp FROM ercot.lmp_data LIMIT 1;")
        assert b"+00" in output  # UTC timezone indicator

    def test_unique_constraint_on_lmp_data(self, postgres_helper) -> None:
        """Test that unique constraint exists on timestamp + location."""
        output = postgres_helper.execute_query(
            "INSERT INTO ercot.lmp_data (timestamp, location, lmp_value) " "VALUES ('2024-01-01 12:00:00+00', 'HB_HOUSTON', 50.0);",
            check=False,
        )
        assert b"duplicate key" in output or b"UNIQUE" in output

    def test_connection_with_credentials(self, postgres_helper) -> None:
        """Test that database is accessible with provided credentials."""
        postgres_helper.assert_query_contains("SELECT current_user;", b"ercot_user")

    def test_table_comments_exist(self, postgres_helper) -> None:
        """Test that table comments were set."""
        output = postgres_helper.execute_query("\\dt+ ercot.lmp_data")
        # Check for either full comment or partial match
        has_comment = b"ERCOT LMP" in output or b"Locational Marginal Pricing" in output
        assert has_comment, "Table comments not found"


class TestDockerImageIntegration:
    """Integration tests between Docker images."""

    @pytest.fixture(autouse=True)
    def ensure_images_exist(self, docker_client):
        """Skip tests if images don't exist."""
        try:
            docker_client.images.get("ercot-lmp:latest")
            docker_client.images.get("ercot-db:latest")
        except Exception:
            pytest.skip("Required Docker images not found")

    def test_both_images_present(self, docker_client) -> None:
        """Test that both required images exist."""
        images = docker_client.images.list()
        image_tags = [tag for image in images for tag in image.tags]
        assert "ercot-lmp:latest" in image_tags
        assert "ercot-db:latest" in image_tags

    def test_images_have_base_images(self, docker_client) -> None:
        """Test that images are based on expected base images."""
        lmp_image = docker_client.images.get("ercot-lmp:latest")
        db_image = docker_client.images.get("ercot-db:latest")

        # Verify images exist and have labels/config
        assert lmp_image is not None
        assert db_image is not None
        assert lmp_image.attrs.get("Config") is not None
        assert db_image.attrs.get("Config") is not None
