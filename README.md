# Python Monorepo with Pants Build System

A clean, production-ready template for Python monorepos using [Pants](https://www.pantsbuild.org/) build system with PEX and Docker support.

## Project Structure

```
.
├── pants.toml              # Pants configuration
├── pyproject.toml          # Project dependencies
├── BUILD                   # Root build file (dependencies)
├── Makefile               # Convenient build commands
├── Dockerfile             # Docker image definition
├── .dockerignore          # Docker build exclusions
│
├── ercot_lmp/             # Application package
│   ├── BUILD              # Build targets (sources, pex)
│   └── scripts/
│       ├── __init__.py
│       └── main.py        # Application entry point
│
└── lib_ercot/             # Shared library package
    ├── BUILD              # Build targets (sources, tests)
    ├── utils/
    │   ├── __init__.py
    │   └── core.py
    └── test_main.py       # Tests
```

## Quick Start

### Prerequisites

- Python 3.11+
- [Pants](https://www.pantsbuild.org/docs/installation) 2.30.0
- Docker (for containerization)

### Available Commands

```bash
# Show all available targets
make help

# Run tests
make test

# Build standalone PEX executable
make pex

# Build Docker image
make docker-build

# Run Docker container
make docker-run

# Build and run Docker (combined)
make docker

# Run tests and build PEX
make all

# Clean all build artifacts
make clean
```

### Using Pants Directly

```bash
# List all targets
pants list ::

# Run tests
pants test ::

# Build PEX
pants package ercot_lmp:pex

# Run specific tests
pants test lib_ercot:tests
```

## Template Structure

### 1. Pants Configuration (`pants.toml`)

Minimal configuration with:
- Python backend
- Python 3.11-3.13 interpreter constraints
- Rust parser for better performance
- Telemetry disabled

### 2. BUILD Files

**Root BUILD** - Defines Python requirements from `pyproject.toml`

**Package BUILD files** - Define:
- `python_sources`: Source code targets
- `pex_binary`: Executable PEX files
- `python_tests`: Test targets

### 3. PEX Executable

Creates a standalone executable Python file (`.pex`) that:
- Contains all dependencies
- Works without virtual environments
- Can be shipped as a single file
- Built to `dist/ercot_lmp.pex`

### 4. Docker Image

Multi-stage Docker build that:
- Uses Python 3.11-slim base
- Installs dependencies from pyproject.toml
- Copies source code
- Sets up proper PYTHONPATH
- Defines entry point

### 5. Makefile

Provides convenient commands with:
- Clear output messages
- Proper PHONY targets
- Combined targets (docker = build + run)
- Clean target for all artifacts

## Customizing This Template

### For a New Project

1. **Update project metadata** in `pyproject.toml`:
   ```toml
   [project]
   name = "your-project-name"
   version = "0.1.0"
   dependencies = [...]
   ```

2. **Rename packages**:
   - `ercot_lmp/` → your application package
   - `lib_ercot/` → your library package

3. **Update BUILD files** with new package names

4. **Update Dockerfile** COPY commands with new paths

5. **Update Makefile** targets as needed

### Adding a New Package

1. Create directory with Python code
2. Add `BUILD` file:
   ```python
   python_sources(
       sources=["**/*.py", "!*_test.py", "!test_*.py"],
   )

   python_tests(
       name="tests",
       sources=["*_test.py", "test_*.py"],
   )
   ```

### Adding a New PEX Binary

In your package's `BUILD` file:
```python
pex_binary(
    name="mybinary",
    entry_point="module/main.py",
    output_path="mybinary.pex",
)
```

Build with: `pants package //path/to/package:mybinary`

## Best Practices

### BUILD Files
- Keep them simple and declarative
- Use glob patterns for sources (`**/*.py`)
- Separate test sources from production sources
- Explicit naming for non-default targets

### Dependencies
- Define all dependencies in `pyproject.toml`
- Pants will automatically infer import dependencies
- Use explicit `dependencies=[]` only when needed

### Testing
- Name test files `test_*.py` or `*_test.py`
- Run all tests with `pants test ::`
- Run specific tests with `pants test path/to:tests`

### Docker
- Keep Dockerfile simple and cacheable
- Order layers by change frequency
- Use `.dockerignore` to exclude unnecessary files
- Pin dependency versions for reproducibility

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: pantsbuild/actions/init-pants@main
      - run: pants test ::

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: pantsbuild/actions/init-pants@main
      - run: pants package ::
```

## Troubleshooting

### Pants cache issues
```bash
pants clean-all
```

### Docker build fails
```bash
# Check .dockerignore
# Verify source paths in Dockerfile
docker build -t test . --progress=plain
```

### PEX runtime issues
```bash
# Test PEX locally
./dist/ercot_lmp.pex --help
```

## Resources

- [Pants Documentation](https://www.pantsbuild.org/docs)
- [PEX Documentation](https://pex.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/)

## License

[Your License Here]
