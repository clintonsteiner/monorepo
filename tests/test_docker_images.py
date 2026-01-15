"""Docker image tests."""

import time

import docker
import pytest

pytestmark = pytest.mark.docker


@pytest.fixture(scope="session")
def docker_client():
    return docker.from_env()


def run_in_container(client, image, cmd):
    """Run command in container, return output bytes."""
    out = client.containers.run(image, cmd, remove=True, stdout=True, stderr=True, entrypoint="")
    return out if isinstance(out, bytes) else out.encode()


class TestErcotLmpImage:
    IMAGE = "ercot-lmp:latest"

    @pytest.fixture(autouse=True)
    def skip_if_missing(self, docker_client):
        try:
            docker_client.images.get(self.IMAGE)
        except Exception:
            pytest.skip(f"{self.IMAGE} not found")

    def test_image_exists(self, docker_client):
        assert self.IMAGE in docker_client.images.get(self.IMAGE).tags

    def test_has_python(self, docker_client):
        assert b"Python 3.11" in run_in_container(docker_client, self.IMAGE, ["python", "--version"])

    def test_pex_files_exist(self, docker_client):
        out = run_in_container(docker_client, self.IMAGE, ["ls", "/app/"])
        assert b"ercot_lmp.pex" in out and b"hello_world.pex" in out

    def test_hello_world_runs(self, docker_client):
        out = run_in_container(docker_client, self.IMAGE, ["/app/hello_world.pex", "--name", "Docker"])
        assert b"Hello, Docker!" in out


class TestErcotDbImage:
    IMAGE = "ercot-db:latest"
    CREDS = {"user": "ercot_user", "password": "ercot_pass", "db": "ercot_db"}

    @pytest.fixture(autouse=True)
    def skip_if_missing(self, docker_client):
        try:
            docker_client.images.get(self.IMAGE)
        except Exception:
            pytest.skip(f"{self.IMAGE} not found")

    @pytest.fixture
    def pg(self, docker_client):
        name = "test-ercot-db"
        try:
            docker_client.containers.get(name).remove(force=True)
        except Exception:
            pass

        c = docker_client.containers.run(
            self.IMAGE,
            environment={"POSTGRES_USER": self.CREDS["user"], "POSTGRES_PASSWORD": self.CREDS["password"], "POSTGRES_DB": self.CREDS["db"]},
            name=name,
            detach=True,
        )
        # Wait for ready
        for _ in range(15):
            if c.exec_run(["pg_isready", "-U", self.CREDS["user"]]).exit_code == 0:
                time.sleep(1)  # Extra wait for init scripts
                break
            time.sleep(1)
        try:
            yield c
        finally:
            c.remove(force=True)

    def _query(self, pg, sql):
        cmd = ["psql", "-U", self.CREDS["user"], "-d", self.CREDS["db"], "-c", sql]
        return pg.exec_run(cmd, environment={"PGPASSWORD": self.CREDS["password"]}).output

    def test_postgres_version(self, pg):
        assert b"PostgreSQL 16" in self._query(pg, "SELECT version();")

    def test_schema_exists(self, pg):
        assert b"ercot" in self._query(pg, "\\dn ercot")

    def test_tables_exist(self, pg):
        out = self._query(pg, "\\dt ercot.*")
        assert b"lmp_data" in out and b"monitor_metadata" in out

    def test_seed_data(self, pg):
        assert b"5" in self._query(pg, "SELECT COUNT(*) FROM ercot.lmp_data;")

    def test_functions_exist(self, pg):
        out = self._query(pg, "\\df ercot.*")
        assert b"get_latest_lmp" in out and b"update_metadata" in out
