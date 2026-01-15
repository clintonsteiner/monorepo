.PHONY: help test pex docker-build docker-run docker clean

help:
	@echo "Available targets:"
	@echo "  test         - Run tests"
	@echo "  pex          - Build PEX executable"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  docker       - Build and run Docker container"
	@echo "  clean        - Clean build artifacts"

test:
	pants test ::

pex:
	pants package ercot_lmp:pex
	@echo "PEX file built: dist/ercot_lmp.pex"

docker-build:
	docker build -t ercot-lmp:latest .

docker-run:
	docker run --rm ercot-lmp:latest

docker: docker-build docker-run

clean:
	rm -rf dist/
	pants clean-all
	docker rmi -f ercot-lmp:latest 2>/dev/null || true
