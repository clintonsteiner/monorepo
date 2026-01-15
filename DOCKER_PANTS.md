# Docker Integration with Pants

Complete guide for using Docker as Pants targets in the monorepo.

## Overview

Docker images are now built as first-class Pants targets, providing:

- ✅ Dependency tracking
- ✅ Parallel builds
- ✅ Caching
- ✅ Consistent with other build artifacts

## Docker Targets

### Application Image: `ercot_lmp:docker`

**Location**: `ercot_lmp/BUILD`

```python
docker_image(
    name="docker",
    source="Dockerfile",
    dependencies=[
        ":pex",                    # ercot_lmp.pex
        "//hello_world:pex",       # hello_world.pex
        ":ercot_lmp",              # Python sources
        "//lib_ercot:lib_ercot",   # Library sources
        "//hello_world:hello_world", # hello_world sources
    ],
    image_tags=["latest"],
)
```

**Features**:

- Based on python:3.11-slim
- Includes all Python dependencies
- Contains PEX binaries in `/app`
- Multiple Python packages (ercot_lmp, lib_ercot, hello_world)

### Database Image: `db_setup:docker`

**Location**: `db_setup/BUILD`

```python
docker_image(
    name="docker",
    source="Dockerfile.db",
    dependencies=[":sql"],
    image_tags=["latest"],
    repository="ercot-db",
)
```

**Features**:

- Based on postgres:16-alpine
- Includes SQL initialization files
- Auto-runs SQL scripts on first start
- Lightweight (272 MB)

## Building with Pants

### Build Single Image

```bash
# Build application image
pants package ercot_lmp:docker

# Build database image
pants package db_setup:docker
```

### Build All Images

```bash
# Build both Docker images
pants package ercot_lmp:docker db_setup:docker

# Or use Makefile
make docker-build
```

### Pants Benefits

1. **Dependency Tracking**
   - Pants automatically builds PEX files first
   - Changes to Python code trigger image rebuild
   - SQL file changes trigger database image rebuild

2. **Caching**
   - Pants caches Docker layers
   - Only rebuilds when dependencies change
   - Much faster than standalone Docker builds

3. **Parallel Builds**
   - Multiple images build simultaneously
   - Better CI/CD performance

## Using Built Images

### Application Image

```bash
# Run with default entrypoint
docker run --rm ercot-lmp:latest

# Run hello_world.pex
docker run --rm --entrypoint /app/hello_world.pex \
    ercot-lmp:latest --name "Pants"

# Interactive shell
docker run --rm -it --entrypoint /bin/bash ercot-lmp:latest
```

### Database Image

```bash
# Start database
docker run -d --name ercot-postgres \
    -p 5432:5432 \
    -e POSTGRES_USER=ercot_user \
    -e POSTGRES_PASSWORD=ercot_pass \
    -e POSTGRES_DB=ercot_db \
    ercot-db:latest

# Connect to database
docker exec -it ercot-postgres psql -U ercot_user -d ercot_db

# Stop database
docker stop ercot-postgres
docker rm ercot-postgres
```

## Makefile Integration

All Docker operations available via Makefile:

```bash
# Build images with Pants
make docker-build        # Build both images

# Run containers
make docker-run          # Run application
make docker-hello        # Run hello_world.pex
make docker              # Build and run

# Database operations
make db-build            # Build database image
make db-run              # Start database container
make db-stop             # Stop database container
make db-shell            # Connect to database
make db-clean            # Remove database + volume
```

## Dockerfile Structure

### Application Dockerfile (`ercot_lmp/Dockerfile`)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    requests>=2.31.0 \
    pandas>=2.0.0 \
    beautifulsoup4>=4.12.0 \
    lxml>=5.0.0 \
    html5lib>=1.1

# Copy everything from Pants build context
COPY . /app

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "/app/ercot_lmp/scripts/main.py"]
```

### Database Dockerfile (`db_setup/Dockerfile.db`)

```dockerfile
FROM postgres:16-alpine

ENV POSTGRES_USER=ercot_user
ENV POSTGRES_PASSWORD=ercot_pass
ENV POSTGRES_DB=ercot_db

# Pants provides paths relative to repo root
COPY db_setup/sql/*.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
```

## Dependencies

### How Pants Handles Dependencies

When you declare dependencies in `docker_image`:

```python
docker_image(
    name="docker",
    dependencies=[
        ":pex",                    # Builds ercot_lmp.pex first
        "//hello_world:pex",       # Builds hello_world.pex first
        ":ercot_lmp",              # Includes Python sources
        "//lib_ercot:lib_ercot",   # Includes library sources
    ],
)
```

Pants:

1. Resolves all transitive dependencies
2. Builds PEX files if needed
3. Collects all files into build context
4. Runs Docker build with collected files

### Build Order

```
Request: pants package ercot_lmp:docker
    ↓
1. Build ercot_lmp:pex (if not cached)
    ↓
2. Build hello_world:pex (if not cached)
    ↓
3. Collect Python sources (ercot_lmp, lib_ercot, hello_world)
    ↓
4. Create Docker build context
    ↓
5. Run Docker build
    ↓
6. Tag image as ercot-lmp:latest
```

## CI/CD Integration

### GitHub Actions

The workflows already use Pants for Docker builds:

```yaml
# .github/workflows/ci.yml
- name: Build Docker images
  run: pants package ercot_lmp:docker db_setup:docker
```

### Publishing Images

To publish to Docker Hub or GHCR:

```bash
# Build with Pants
pants package ercot_lmp:docker

# Tag for registry
docker tag ercot-lmp:latest username/ercot-lmp:v1.0.0

# Push
docker push username/ercot-lmp:v1.0.0
```

## Configuration

### pants.toml

```toml
[docker]
default_repository = "ercot-lmp"
build_args = []
build_target_stage = ""
```

### Custom Tags

To add custom tags:

```python
docker_image(
    name="docker",
    image_tags=["latest", "v1.0.0", "dev"],
)
```

### Build Arguments

Pass Docker build arguments:

```python
docker_image(
    name="docker",
    extra_build_args=["VERSION=1.0.0", "ENV=production"],
)
```

## Troubleshooting

### Image Not Found After Build

**Issue**: Docker image not appearing in `docker images`

**Solution**:

```bash
# Check Pants output
pants package ercot_lmp:docker

# Look for: "Built docker image: ercot-lmp:latest"
# If not there, check BUILD file syntax
```

### Dependency Not Included

**Issue**: Files missing in Docker image

**Solution**:

```python
# Add missing dependency to BUILD file
docker_image(
    dependencies=[
        ":missing-target",  # Add this
    ],
)
```

### COPY Command Fails

**Issue**: Dockerfile COPY can't find files

**Solution**:

- Pants creates build context with specific structure
- Use `COPY . /app` to copy everything
- Or use Pants-relative paths: `COPY package/file /dest`

### Cache Not Working

**Issue**: Pants rebuilds Docker image every time

**Solution**:

```bash
# Clear Pants cache
rm -rf .pants.d

# Rebuild
pants package ercot_lmp:docker
```

## Best Practices

### DO ✅

- Use Pants to build Docker images (not standalone docker build)
- Declare all dependencies in BUILD files
- Use simple COPY commands in Dockerfiles
- Let Pants handle build ordering
- Use Makefile for convenience
- Cache Docker layers appropriately

### DON'T ❌

- Don't use standalone `docker build` for Pants-managed images
- Don't hard-code paths in Dockerfiles
- Don't skip Pants dependency declarations
- Don't mix Pants and non-Pants Docker workflows
- Don't use complex COPY logic (let Pants handle it)

## Migration from Standalone Docker

Before (standalone Docker):

```bash
docker build -t ercot-lmp:latest .
docker build -f db_setup/Dockerfile.db -t ercot-db:latest db_setup/
```

After (Pants):

```bash
pants package ercot_lmp:docker db_setup:docker
# Or: make docker-build
```

Benefits:

- ✅ Automatic dependency building
- ✅ Parallel builds
- ✅ Better caching
- ✅ Integrated with test/lint workflow
- ✅ Consistent with other artifacts

## Advanced Usage

### Multi-Stage Builds

```dockerfile
# Stage 1: Builder
FROM python:3.11 AS builder
WORKDIR /build
COPY . .
RUN pip wheel --no-deps -w /wheels .

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /wheels /wheels
RUN pip install /wheels/*.whl
```

### Platform-Specific Builds

```python
docker_image(
    name="docker-arm64",
    extra_build_args=["--platform=linux/arm64"],
)
```

### Custom Registries

```python
docker_image(
    name="docker",
    registries=["gcr.io/my-project"],
    repository="my-app",
)
```

## Resources

- [Pants Docker Backend Docs](https://www.pantsbuild.org/docs/docker)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- Project Dockerfiles:
  - `ercot_lmp/Dockerfile`
  - `db_setup/Dockerfile.db`
