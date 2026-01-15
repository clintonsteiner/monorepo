# Pants Monorepo Template - File Reference

This document provides the complete file structure for the template.

## Core Configuration Files

### pants.toml
```toml
[GLOBAL]
pants_version = "2.30.0"
backend_packages = [
    "pants.backend.python",
]

[source]
root_patterns = ["/"]

[python]
interpreter_constraints = ["CPython>=3.11,<3.13"]

[python-infer]
use_rust_parser = true

[anonymous-telemetry]
enabled = false
```

### pyproject.toml
```toml
[project]
name = "your-project-name"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "requests>=2.31.0",
  "pandas>=2.0.0",
  # Add your dependencies here
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### Root BUILD
```python
python_requirements(
    name="reqs",
    source="pyproject.toml",
)
```

## Package Structure

### Application Package (ercot_lmp/BUILD)
```python
python_sources(
    sources=["**/*.py"],
)

pex_binary(
    name="pex",
    entry_point="scripts/main.py",
    output_path="ercot_lmp.pex",
)
```

### Library Package (lib_ercot/BUILD)
```python
python_sources(
    sources=["**/*.py", "!*_test.py", "!test_*.py"],
)

python_tests(
    name="tests",
    sources=["*_test.py", "test_*.py"],
)
```

## Docker Configuration

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    requests>=2.31.0 \
    pandas>=2.0.0 \
    # Add your dependencies here

# Copy source code
COPY ercot_lmp/ /app/ercot_lmp/
COPY lib_ercot/ /app/lib_ercot/

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "/app/ercot_lmp/scripts/main.py"]
```

### .dockerignore
```
# Git
.git/
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# Pants
.pants.d/
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test and build artifacts
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
```

## Build Automation

### Makefile
```makefile
.PHONY: help test pex docker-build docker-run docker clean all

help:
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  test         - Run all tests"
	@echo "  pex          - Build standalone PEX executable"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  docker       - Build and run Docker container"
	@echo "  all          - Run tests and build PEX"
	@echo "  clean        - Clean all build artifacts"

test:
	@echo "Running tests..."
	pants test ::

pex:
	@echo "Building PEX executable..."
	pants package ercot_lmp:pex
	@echo "✓ PEX file built: dist/ercot_lmp.pex"

docker-build:
	@echo "Building Docker image..."
	docker build -t ercot-lmp:latest .
	@echo "✓ Docker image built: ercot-lmp:latest"

docker-run:
	@echo "Running Docker container..."
	docker run --rm ercot-lmp:latest

docker: docker-build docker-run

all: test pex

clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/
	pants clean-all
	docker rmi -f ercot-lmp:latest 2>/dev/null || true
	@echo "✓ Clean complete"
```

## Key Design Principles

### 1. Simplicity
- Minimal configuration files
- Only essential dependencies
- Clear, self-documenting structure

### 2. Separation of Concerns
- Application code separate from libraries
- Tests separate from sources
- Build configuration separate from source code

### 3. Reproducibility
- Pinned tool versions (Pants)
- Explicit interpreter constraints
- Docker for consistent environments

### 4. Developer Experience
- Makefile for common operations
- Clear help messages
- Fast feedback (cached builds)

### 5. Production Ready
- PEX for deployment
- Docker for containerization
- Comprehensive testing support

## Extending the Template

### Adding a New Service
1. Create `my_service/` directory
2. Add `my_service/BUILD`:
   ```python
   python_sources(sources=["**/*.py"])

   pex_binary(
       name="pex",
       entry_point="main.py",
       output_path="my_service.pex",
   )
   ```
3. Update Dockerfile if needed
4. Update Makefile with new targets

### Adding Backend Features
Common backends to add to `pants.toml`:
```toml
backend_packages = [
    "pants.backend.python",
    "pants.backend.python.lint.black",      # Code formatting
    "pants.backend.python.lint.isort",      # Import sorting
    "pants.backend.python.typecheck.mypy",  # Type checking
    "pants.backend.shell",                  # Shell scripts
]
```

### Multi-Environment Dockerfiles
Create `Dockerfile.dev`, `Dockerfile.prod`, etc. and update Makefile:
```makefile
docker-build-dev:
	docker build -f Dockerfile.dev -t myapp:dev .
```

## Validation Checklist

After setting up from this template:

- [ ] `pants list ::` shows all targets
- [ ] `pants test ::` runs all tests
- [ ] `pants package ercot_lmp:pex` builds executable
- [ ] `./dist/ercot_lmp.pex` runs without errors
- [ ] `docker build -t test .` succeeds
- [ ] `docker run --rm test` works
- [ ] `make help` shows all targets
- [ ] `make test` runs successfully
- [ ] `make pex` creates PEX file
- [ ] `make docker` builds and runs

## Common Patterns

### Entry Point Script
```python
# scripts/main.py
import argparse

def main():
    parser = argparse.ArgumentParser(description="Your app")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    # Your application logic here
    print(f"Running with config: {args.config}")

if __name__ == "__main__":
    main()
```

### Library Module
```python
# lib_ercot/utils/core.py
"""Core utilities."""

def my_function():
    """Do something useful."""
    pass
```

### Test File
```python
# lib_ercot/test_main.py
import pytest
from lib_ercot.utils.core import my_function

def test_my_function():
    """Test the function."""
    result = my_function()
    assert result is not None
```

## Template Checklist

When using this as a template:

1. **Rename** packages (`ercot_lmp` → `your_app`)
2. **Update** `pyproject.toml` with your metadata
3. **Modify** dependencies in `pyproject.toml`
4. **Update** Dockerfile COPY paths
5. **Adjust** Makefile target names
6. **Customize** README.md for your project
7. **Remove** this TEMPLATE.md file
8. **Test** everything works with your changes

---

**Created**: 2026-01-15
**Pants Version**: 2.30.0
**Python**: 3.11+
