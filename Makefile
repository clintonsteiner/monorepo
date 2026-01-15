.PHONY: help test lint fmt tailor update-build-files pex docker-build docker-run docker-hello db-build db-run db-stop db-shell db-clean docker clean all hooks

help:
	@echo "Available targets:"
	@echo "  help              - Show this help message"
	@echo "  test              - Run all tests"
	@echo "  lint              - Run linters (flake8, isort, black)"
	@echo "  fmt               - Auto-format code (black, isort)"
	@echo "  tailor            - Auto-generate/update BUILD files"
	@echo "  update-build-files- Update BUILD file formatting"
	@echo "  hooks             - Install pre-commit hooks"
	@echo "  pex               - Build all PEX executables"
	@echo "  docker-build      - Build Docker image (includes PEX files)"
	@echo "  docker-run        - Run Docker container (ercot_lmp)"
	@echo "  docker-hello      - Run hello_world.pex in Docker"
	@echo "  docker            - Build and run Docker container"
	@echo "  db-build          - Build PostgreSQL database image"
	@echo "  db-run            - Run PostgreSQL database container"
	@echo "  db-stop           - Stop PostgreSQL database container"
	@echo "  db-shell          - Connect to PostgreSQL database"
	@echo "  db-clean          - Remove database container and volume"
	@echo "  all               - Run tests and build all PEX files"
	@echo "  clean             - Clean all build artifacts"

test:
	@echo "Running tests..."
	pants test ::

lint:
	@echo "Running linters..."
	pants lint ::

fmt:
	@echo "Formatting code..."
	pants fmt ::

tailor:
	@echo "Running Pants tailor to update BUILD files..."
	pants tailor ::

update-build-files:
	@echo "Updating BUILD file formatting..."
	pants update-build-files ::

hooks:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "✓ Pre-commit hooks installed"

pex:
	@echo "Building PEX executables..."
	pants package ercot_lmp:pex hello_world:pex
	@echo "✓ PEX files built:"
	@echo "  - dist/ercot_lmp.pex"
	@echo "  - dist/hello_world.pex"

docker-build: pex
	@echo "Building Docker image with PEX files..."
	docker build -t ercot-lmp:latest .
	@echo "✓ Docker image built: ercot-lmp:latest"

docker-run:
	@echo "Running ercot_lmp in Docker..."
	docker run --rm ercot-lmp:latest

docker-hello:
	@echo "Running hello_world.pex in Docker..."
	docker run --rm --entrypoint /app/bin/hello_world.pex ercot-lmp:latest --name "Docker"

docker: docker-build docker-run

db-build:
	@echo "Building PostgreSQL database image..."
	docker build -f db_setup/Dockerfile.db -t ercot-db:latest db_setup/
	@echo "✓ Database image built: ercot-db:latest"

db-run:
	@echo "Starting PostgreSQL database container..."
	docker run -d \
		--name ercot-postgres \
		-p 5432:5432 \
		-e POSTGRES_USER=ercot_user \
		-e POSTGRES_PASSWORD=ercot_pass \
		-e POSTGRES_DB=ercot_db \
		-v ercot_pgdata:/var/lib/postgresql/data \
		ercot-db:latest
	@echo "✓ Database running on localhost:5432"
	@echo "  User: ercot_user"
	@echo "  Password: ercot_pass"
	@echo "  Database: ercot_db"

db-stop:
	@echo "Stopping PostgreSQL database container..."
	docker stop ercot-postgres 2>/dev/null || true
	docker rm ercot-postgres 2>/dev/null || true
	@echo "✓ Database stopped"

db-shell:
	@echo "Connecting to database..."
	docker exec -it ercot-postgres psql -U ercot_user -d ercot_db

db-clean: db-stop
	@echo "Removing database volume..."
	docker volume rm ercot_pgdata 2>/dev/null || true
	docker rmi -f ercot-db:latest 2>/dev/null || true
	@echo "✓ Database cleaned"

all: test pex

clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/
	pants clean-all
	docker rmi -f ercot-lmp:latest 2>/dev/null || true
	@echo "✓ Clean complete"
