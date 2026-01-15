# SQL initialization scripts
files(
    name="sql",
    sources=["sql/*.sql"],
)

# Docker image: ercot-db:latest
# PostgreSQL with initialization scripts
docker_image(
    name="docker",
    source="Dockerfile.db",
    dependencies=[":sql"],
    image_tags=["latest"],
    repository="ercot-db",
)
