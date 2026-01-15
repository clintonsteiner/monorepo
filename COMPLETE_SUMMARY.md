# Complete Monorepo Template Summary

Production-ready Python monorepo template with Pants build system, PEX executables, Docker support, PostgreSQL database, and comprehensive tooling.

## 📁 Project Structure

```
monorepo/
├── pants.toml                     # Pants build configuration
├── pyproject.toml                 # Python project metadata + tool configs
├── BUILD                          # Root build file (dependencies)
├── Makefile                       # Convenient build commands
├── Dockerfile                     # Main application Docker image
├── .dockerignore                  # Docker build exclusions
├── .pre-commit-config.yaml        # Pre-commit hook configuration
├── .hadolint.yaml                 # Dockerfile linting config
├── .sqlfluff                      # SQL linting config
│
├── ercot_lmp/                     # Main application package
│   ├── BUILD                      # Build targets (sources, pex)
│   └── scripts/
│       ├── __init__.py
│       └── main.py                # Application entry point
│
├── hello_world/                   # Example CLI tool package
│   ├── BUILD                      # Build targets (sources, tests, pex)
│   ├── __init__.py
│   ├── main.py                    # CLI entry point
│   └── test_main.py              # Tests
│
├── lib_ercot/                     # Shared library package
│   ├── BUILD                      # Build targets (sources, tests)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── core.py
│   └── test_main.py              # Tests
│
├── db_setup/                      # Database setup
│   ├── BUILD                      # SQL file targets
│   ├── Dockerfile.db              # PostgreSQL image
│   ├── README.md                  # Database documentation
│   └── sql/
│       ├── 01_schema.sql         # Table definitions
│       ├── 02_seed_data.sql      # Sample data
│       └── 03_functions.sql      # Stored procedures
│
├── README.md                      # Project documentation
├── SETUP.md                       # Development setup guide
└── TEMPLATE.md                    # Template file reference
```

## 🎯 Features

### Build System
- **Pants 2.30.0** - Fast, reliable builds with caching
- **Tailor** - Auto-generates and maintains BUILD files
- **Multi-language support** - Python, SQL, Docker, etc.

### Python Tooling
- **Black** - Code formatting (88 char line length)
- **isort** - Import sorting
- **flake8** - Code linting
- **bandit** - Security scanning
- **pytest** - Testing framework

### Packaging & Distribution
- **PEX Files** - Standalone executable Python files
  - `dist/ercot_lmp.pex` (19.6 MB)
  - `dist/hello_world.pex` (922 KB)
- **Docker Images**
  - Application: `ercot-lmp:latest` (324 MB)
  - Database: `ercot-db:latest` (PostgreSQL 16)

### Database
- **PostgreSQL 16-alpine** - Lightweight database image
- **SQL Migrations** - Numbered SQL files (01_, 02_, 03_)
- **Sample Data** - Pre-populated test data
- **Stored Functions** - Database procedures
- **Persistent Volume** - Data survives container restarts

### Quality Assurance
- **Pre-commit Hooks** - 15+ automated checks
- **Linting** - Code quality enforcement
- **Testing** - Automated test execution
- **Formatting** - Consistent code style
- **SQL Validation** - SQL linting with sqlfluff
- **Dockerfile Linting** - hadolint integration

## 🚀 Quick Start

### Initial Setup
```bash
# 1. Install pre-commit hooks
make hooks

# 2. Format and validate code
make fmt
make tailor
make test

# 3. Build everything
make pex
make docker-build
make db-build
```

### Daily Development
```bash
# Format code
make fmt

# Run tests
make test

# Update BUILD files
make tailor

# Build PEX files
make pex
```

### Running Services
```bash
# Run application
./dist/hello_world.pex --name "World"
./dist/ercot_lmp.pex

# Run in Docker
make docker-run
make docker-hello

# Start database
make db-run
make db-shell    # Connect to DB
```

## 📋 Available Make Commands

### Development
| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make test` | Run all tests |
| `make lint` | Run linters (flake8, isort, black) |
| `make fmt` | Auto-format code (black, isort) |
| `make tailor` | Auto-generate/update BUILD files |
| `make update-build-files` | Update BUILD file formatting |
| `make hooks` | Install pre-commit hooks |

### Building
| Command | Description |
|---------|-------------|
| `make pex` | Build all PEX executables |
| `make docker-build` | Build Docker application image |
| `make db-build` | Build PostgreSQL database image |

### Running
| Command | Description |
|---------|-------------|
| `make docker-run` | Run ercot_lmp in Docker |
| `make docker-hello` | Run hello_world.pex in Docker |
| `make docker` | Build and run Docker container |
| `make db-run` | Start PostgreSQL database |
| `make db-shell` | Connect to database shell |

### Cleanup
| Command | Description |
|---------|-------------|
| `make clean` | Clean build artifacts |
| `make db-stop` | Stop database container |
| `make db-clean` | Remove database container + volume |

## 🔧 Pants Commands

### Tailor (BUILD File Management)
```bash
# Check what BUILD files need updating
pants tailor --check ::

# Auto-generate/update BUILD files
pants tailor ::
make tailor
```

### Formatting
```bash
# Format all code
pants fmt ::
make fmt

# Format specific files
pants fmt path/to/file.py

# Check formatting (no changes)
pants fmt --check ::
```

### Linting
```bash
# Run all linters
pants lint ::
make lint

# Run specific linter
pants lint --only=flake8 ::
pants lint --only=black ::
pants lint --only=isort ::
```

### Testing
```bash
# Run all tests
pants test ::
make test

# Run package tests
pants test hello_world::
pants test lib_ercot::

# Run specific test file
pants test hello_world/test_main.py
```

### Building
```bash
# Build all packages
pants package ::

# Build specific PEX
pants package hello_world:pex
pants package ercot_lmp:pex
```

### Discovery
```bash
# List all targets
pants list ::

# List package targets
pants list hello_world::

# Show dependencies
pants dependencies lib_ercot::

# Show what depends on this
pants dependees lib_ercot::
```

## 🪝 Pre-commit Hooks

Hooks run automatically on `git commit`:

### Pants Hooks
- `pants-tailor` - Ensures BUILD files are up to date
- `pants-update-build-files` - Formats BUILD files
- `pants-fmt` - Formats Python code
- `pants-lint` - Runs linters

### Python Hooks
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Code linting
- `bandit` - Security checks

### Other Hooks
- `prettier` - YAML/JSON/Markdown formatting
- `hadolint` - Dockerfile linting
- `sqlfluff` - SQL linting and formatting
- File checks (trailing whitespace, EOF, merge conflicts, etc.)

### Manual Hook Execution
```bash
# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run pants-tailor --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

## 🐳 Docker Images

### Application Image (ercot-lmp:latest)
- **Base**: python:3.11-slim
- **Size**: ~324 MB
- **Contents**:
  - Python source code (ercot_lmp, lib_ercot, hello_world)
  - PEX executables in `/app/bin/`
  - All Python dependencies
- **Entry Point**: ercot_lmp application
- **Alternate Entry Points**:
  - `/app/bin/hello_world.pex` - Hello world CLI
  - `/app/bin/ercot_lmp.pex` - Main application

### Database Image (ercot-db:latest)
- **Base**: postgres:16-alpine
- **Size**: ~230 MB
- **Features**:
  - Auto-executes SQL files in order (01_, 02_, 03_)
  - Pre-populated with sample data
  - Stored functions and procedures
  - Persistent volume support
- **Default Credentials**:
  - User: `ercot_user`
  - Password: `ercot_pass`
  - Database: `ercot_db`
  - Port: `5432`

## 🗄️ Database Schema

### Tables

#### `ercot.lmp_data`
Stores ERCOT LMP (Locational Marginal Pricing) data.

```sql
CREATE TABLE ercot.lmp_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    location VARCHAR(100) NOT NULL,
    lmp_value DECIMAL(10, 2),
    energy_value DECIMAL(10, 2),
    congestion_value DECIMAL(10, 2),
    loss_value DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp, location)
);
```

#### `ercot.monitor_metadata`
Stores monitoring job metadata and status.

```sql
CREATE TABLE ercot.monitor_metadata (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### Functions

- `ercot.get_latest_lmp(location)` - Get most recent LMP reading
- `ercot.update_metadata(key, value)` - Update metadata
- `ercot.get_avg_lmp(location, start, end)` - Calculate average LMP

### Sample Queries

```sql
-- Get latest data for Houston
SELECT * FROM ercot.get_latest_lmp('HB_HOUSTON');

-- View all metadata
SELECT * FROM ercot.monitor_metadata;

-- Calculate average LMP
SELECT ercot.get_avg_lmp(
    'HB_HOUSTON',
    '2024-01-01 00:00:00+00',
    '2024-01-01 23:59:59+00'
);
```

## 📦 PEX Executables

### What is PEX?
PEX (Python EXecutable) files are self-contained Python applications that:
- Include all dependencies
- Work without virtual environments
- Are a single executable file
- Can be shipped and run anywhere

### Available PEX Files

#### hello_world.pex (922 KB)
Simple CLI tool demonstrating PEX packaging.

```bash
# Run locally
./dist/hello_world.pex --help
./dist/hello_world.pex --name "World" --repeat 3

# Run in Docker
docker run --rm --entrypoint /app/bin/hello_world.pex \
    ercot-lmp:latest --name "Docker"
```

#### ercot_lmp.pex (19.6 MB)
Main application with all dependencies (pandas, requests, etc.).

```bash
# Run locally
./dist/ercot_lmp.pex

# Run in Docker
docker run --rm ercot-lmp:latest
```

## 🎨 Code Style Configuration

### Black
```toml
[tool.black]
line-length = 88
target-version = ['py311']
```

### isort
```toml
[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
```

### flake8
```toml
[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
```

## 📊 Build Targets

Total: 21 targets across 4 packages

### Root (/)
- `reqs` - Python requirements from pyproject.toml

### ercot_lmp
- `ercot_lmp` - Python sources
- `pex` - PEX executable

### hello_world
- `hello_world` - Python sources
- `tests` - Test suite
- `pex` - PEX executable

### lib_ercot
- `lib_ercot` - Python sources
- `tests` - Test suite

### db_setup
- `sql` - SQL initialization files

## 🔄 Typical Workflows

### Adding a New Feature
```bash
# 1. Create new files
mkdir -p my_feature
touch my_feature/__init__.py
touch my_feature/main.py
touch my_feature/test_main.py

# 2. Generate BUILD files
make tailor

# 3. Write code and tests
# ... edit files ...

# 4. Format and test
make fmt
make test

# 5. Commit
git add .
git commit -m "Add new feature"
# Pre-commit hooks run automatically
```

### Updating Dependencies
```bash
# 1. Edit pyproject.toml
# Add new dependency

# 2. No other steps needed!
# Pants automatically detects changes

# 3. Test it works
make test
make pex
```

### Releasing
```bash
# 1. Run all checks
make fmt
make lint
make test

# 2. Build artifacts
make pex
make docker-build
make db-build

# 3. Tag release
git tag v1.0.0
git push --tags

# 4. Distribute
# - Push Docker images to registry
# - Distribute PEX files
```

## 🧰 Troubleshooting

### BUILD files out of date
```bash
make tailor
```

### Import errors
```bash
pants dependencies path/to/file.py
# Check what Pants thinks the dependencies are
```

### Formatting issues
```bash
make fmt  # Auto-fix
```

### Cache problems
```bash
pants clean-all  # Nuclear option
```

### Pre-commit hook failures
```bash
# Fix issues first
make fmt
make tailor
make test

# Then commit
git commit
```

## 📚 Key Files Reference

### Configuration Files
- `pants.toml` - Pants build system config
- `pyproject.toml` - Python project + tool configs
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.dockerignore` - Docker build exclusions
- `.hadolint.yaml` - Dockerfile linting
- `.sqlfluff` - SQL linting

### Build Files
- `BUILD` - Defines build targets
- Generated by Tailor
- Should be committed to git
- Can be manually edited if needed

### Docker Files
- `Dockerfile` - Main application image
- `db_setup/Dockerfile.db` - Database image
- Multi-stage builds for optimization

### Documentation
- `README.md` - Project overview
- `SETUP.md` - Development setup guide
- `TEMPLATE.md` - Template file reference
- `db_setup/README.md` - Database documentation

## 🎯 Best Practices

### DO ✅
- Run `make tailor` after adding new files
- Run `make fmt` before committing
- Let pre-commit hooks run (don't skip)
- Use Pants for Python operations
- Keep BUILD files simple
- Test locally before pushing
- Use meaningful commit messages

### DON'T ❌
- Manually maintain BUILD files
- Skip pre-commit hooks
- Commit untested code
- Use `pip install` directly
- Ignore lint warnings
- Commit large binary files
- Use force push to main/master

## 📈 Performance Tips

### Pants Performance
- Pants caches everything aggressively
- First build is slow, subsequent builds are fast
- Use `--changed-since=origin/main` for targeted operations
- Pants runs tests in parallel automatically

### Docker Performance
- Use `.dockerignore` to exclude unnecessary files
- Layer caching speeds up rebuilds
- Build PEX files first, then Docker image

### Pre-commit Performance
- Hooks only run on changed files
- Use `--all-files` sparingly
- Some hooks cache results

## 🔐 Security

### Secrets Management
- Never commit secrets to git
- Use environment variables
- `.env` files are gitignored
- Bandit scans for security issues

### Database Security
- Change default passwords in production
- Use strong passwords
- Don't expose port 5432 publicly
- Use connection pooling

### Docker Security
- Base images are regularly updated
- hadolint checks Dockerfile best practices
- Don't run containers as root (not configured here)

## 🚢 Production Deployment

### Building for Production
```bash
# Build optimized images
docker build -t myapp:prod .
docker build -f db_setup/Dockerfile.db -t mydb:prod db_setup/

# Push to registry
docker tag myapp:prod registry.example.com/myapp:prod
docker push registry.example.com/myapp:prod
```

### Environment Variables
Set these in production:
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- Any app-specific env vars

### Monitoring
- Application logs to stdout/stderr
- Database logs available via `docker logs`
- Add monitoring/observability as needed

## 📝 License

[Your License Here]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make fmt && make test`
5. Commit with pre-commit hooks
6. Push and create a pull request

---

**Template Version**: 1.0.0
**Last Updated**: 2026-01-15
**Pants Version**: 2.30.0
**Python Version**: 3.11+
**PostgreSQL Version**: 16
