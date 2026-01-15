# Development Setup Guide

Complete setup guide for the ERCOT LMP Monorepo.

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- [Pants](https://www.pantsbuild.org/docs/installation) 2.30.0
- `pre-commit` for git hooks

## Initial Setup

### 1. Install Dependencies

```bash
# Install pre-commit
pip install pre-commit

# Install pre-commit hooks
make hooks

# Verify Pants installation
pants --version
```

### 2. Run Initial Checks

```bash
# Generate/update BUILD files
make tailor

# Format all code
make fmt

# Run all tests
make test

# Run linters
make lint
```

### 3. Build Artifacts

```bash
# Build all PEX executables
make pex

# Build Docker images
make docker-build
make db-build
```

## Development Workflow

### Daily Development

1. **Pull latest changes**
   ```bash
   git pull origin main
   make tailor  # Update BUILD files for new code
   ```

2. **Make code changes**
   - Write your code
   - Add tests
   - Run `make fmt` to format

3. **Before committing**
   ```bash
   make fmt          # Auto-format code
   make lint         # Check for issues
   make test         # Run all tests
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Your message"
   # Pre-commit hooks run automatically
   git push
   ```

### Working with Pants

#### Tailor - Auto-generate BUILD files
```bash
# Check what Tailor would do
pants tailor --check ::

# Apply Tailor suggestions
pants tailor ::
# or
make tailor
```

Tailor automatically:
- Creates BUILD files for new packages
- Adds missing targets (python_sources, python_tests, etc.)
- Discovers new dependencies

#### Update BUILD Files - Format existing BUILD files
```bash
# Format BUILD files
pants update-build-files ::
# or
make update-build-files
```

This ensures BUILD files follow consistent formatting.

#### Code Formatting
```bash
# Format all Python code
make fmt

# Format specific files
pants fmt path/to/file.py

# Check formatting without changes
pants fmt --check ::
```

#### Linting
```bash
# Run all linters
make lint

# Run specific linter
pants lint --only=flake8 ::
pants lint --only=black ::
pants lint --only=isort ::

# Lint specific files
pants lint path/to/file.py
```

### Pre-commit Hooks

Hooks run automatically on `git commit`. To run manually:

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run pants-tailor --all-files

# Skip hooks for a commit (not recommended)
git commit --no-verify -m "message"
```

Installed hooks:
- **pants-tailor**: Checks BUILD files are up to date
- **pants-update-build-files**: Ensures BUILD files are formatted
- **pants-fmt**: Formats Python code
- **pants-lint**: Runs linters
- **black**: Python formatting
- **isort**: Import sorting
- **flake8**: Python linting
- **bandit**: Security checks
- **prettier**: YAML/JSON/Markdown formatting
- **hadolint**: Dockerfile linting
- **sqlfluff**: SQL formatting
- General checks (trailing whitespace, file endings, etc.)

## Common Commands

### Testing
```bash
# Run all tests
make test

# Run tests for specific package
pants test hello_world::
pants test lib_ercot::

# Run specific test file
pants test lib_ercot/test_main.py
```

### Building PEX Files
```bash
# Build all PEX executables
make pex

# Build specific PEX
pants package ercot_lmp:pex
pants package hello_world:pex

# Run PEX locally
./dist/hello_world.pex --help
./dist/ercot_lmp.pex
```

### Docker Operations
```bash
# Application containers
make docker-build      # Build app image
make docker-run        # Run app
make docker-hello      # Run hello_world.pex
make docker           # Build and run

# Database container
make db-build         # Build database image
make db-run          # Start database
make db-shell        # Connect to database
make db-stop         # Stop database
make db-clean        # Remove database + volume
```

### Discovery and Inspection
```bash
# List all targets
pants list ::

# List targets in a package
pants list ercot_lmp::
pants list hello_world::

# Show dependencies
pants dependencies lib_ercot::

# Show dependees (what depends on this)
pants dependees lib_ercot::

# Validate BUILD files
pants validate ::
```

## Adding New Code

### Adding a New Package

1. **Create directory structure**
   ```bash
   mkdir -p my_package
   touch my_package/__init__.py
   touch my_package/main.py
   ```

2. **Run Tailor to generate BUILD file**
   ```bash
   make tailor
   ```

3. **Verify the BUILD file**
   ```bash
   cat my_package/BUILD
   ```

4. **Add tests**
   ```bash
   touch my_package/test_main.py
   make tailor  # Updates BUILD with test target
   ```

### Adding a New PEX Binary

Edit the package's BUILD file:
```python
pex_binary(
    name="mybinary",
    entry_point="main.py",
    output_path="mybinary.pex",
)
```

Or let Tailor detect it if you have an entry point.

### Adding Dependencies

1. **Add to pyproject.toml**
   ```toml
   dependencies = [
     "requests>=2.31.0",
     "your-package>=1.0.0",
   ]
   ```

2. **No need to run anything!** Pants automatically detects changes.

## Troubleshooting

### BUILD files out of date
```bash
make tailor              # Fix it
pants tailor --check ::  # Check what's wrong
```

### Import errors
```bash
# Check dependencies
pants dependencies path/to/file.py

# Add explicit dependency in BUILD if needed
python_sources(
    dependencies=["//path/to:package"],
)
```

### Formatting issues
```bash
# Auto-fix most issues
make fmt

# Check what would change
pants fmt --check ::
```

### Cache issues
```bash
# Clean Pants cache
pants clean-all

# Clean everything
make clean
```

### Pre-commit hook failures
```bash
# Fix formatting
make fmt

# Update BUILD files
make tailor
make update-build-files

# Re-run tests
make test

# If all else fails, check specific failure
pre-commit run --all-files
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pantsbuild/actions/init-pants@main
      - run: |
          pants tailor --check ::
          pants update-build-files --check ::
          pants fmt --check ::
          pants lint ::
          pants test ::
          pants package ::
```

## Best Practices

### DO:
- ✅ Run `make tailor` after adding new files
- ✅ Run `make fmt` before committing
- ✅ Run `make test` locally before pushing
- ✅ Let pre-commit hooks run (don't skip)
- ✅ Use Pants for all Python operations
- ✅ Keep BUILD files simple and let Tailor manage them

### DON'T:
- ❌ Manually edit BUILD files unless necessary
- ❌ Skip pre-commit hooks
- ❌ Commit without running tests
- ❌ Use `pip install` (use pyproject.toml)
- ❌ Ignore lint warnings

## Quick Reference

```bash
# Setup
make hooks              # Install pre-commit hooks

# Development
make fmt               # Format code
make lint              # Run linters
make test              # Run tests
make tailor            # Update BUILD files

# Building
make pex               # Build PEX executables
make docker-build      # Build Docker image
make db-build          # Build database image

# Running
./dist/hello_world.pex --help
make docker-run
make db-run

# Database
make db-shell          # Connect to DB
make db-stop           # Stop DB

# Cleanup
make clean             # Clean build artifacts
make db-clean          # Clean database
pants clean-all        # Clean Pants cache
```

## Additional Resources

- [Pants Documentation](https://www.pantsbuild.org/docs)
- [Pants Goals](https://www.pantsbuild.org/docs/goals)
- [Pre-commit Hooks](https://pre-commit.com/)
- [PEX Documentation](https://pex.readthedocs.io/)
