.PHONY: help test pex pex-all docker-build docker-run docker-hello clean all

help:
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  test         - Run all tests"
	@echo "  pex          - Build all PEX executables"
	@echo "  docker-build - Build Docker image (includes PEX files)"
	@echo "  docker-run   - Run Docker container (ercot_lmp)"
	@echo "  docker-hello - Run hello_world.pex in Docker"
	@echo "  docker       - Build and run Docker container"
	@echo "  all          - Run tests and build all PEX files"
	@echo "  clean        - Clean all build artifacts"

test:
	@echo "Running tests..."
	pants test ::

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

all: test pex

clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/
	pants clean-all
	docker rmi -f ercot-lmp:latest 2>/dev/null || true
	@echo "✓ Clean complete"
