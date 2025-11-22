.PHONY: help install install-dev install-all setup run run-dashboard run-api test clean docker-build docker-up docker-down docker-logs lint format check

# Default target
help:
	@echo "BI Platform - Build and Run Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install base dependencies"
	@echo "  make install-dev      - Install development dependencies"
	@echo "  make install-all      - Install all dependencies (base + api + bi + dev)"
	@echo "  make setup            - Full setup (install + sample data)"
	@echo ""
	@echo "Running:"
	@echo "  make run              - Run BI Dashboard"
	@echo "  make run-dashboard    - Run BI Dashboard only"
	@echo "  make run-api          - Run API Engine only"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-logs      - View Docker logs"
	@echo ""
	@echo "Development:"
	@echo "  make lint             - Run linter"
	@echo "  make format           - Format code"
	@echo "  make check            - Run lint and format checks"
	@echo "  make clean            - Clean build artifacts"
	@echo ""

# Installation
install:
	pip install --upgrade pip
	pip install -r requirements/base.txt

install-dev:
	pip install -r requirements/dev.txt

install-all:
	pip install --upgrade pip
	pip install -r requirements/base.txt || echo "Warning: Some base dependencies failed (may need build tools)"
	pip install -r requirements/api.txt
	pip install -r requirements/bi.txt
	pip install -r requirements/dev.txt
	@echo ""
	@echo "Note: Database drivers are optional. Install with:"
	@echo "  pip install -r requirements/database.txt"
	@echo "  (or use: make install-db)"

install-db:
	@echo "Installing optional database drivers..."
	pip install -r requirements/database.txt || echo "Warning: Database drivers installation failed (optional)"

setup: install-all
	@echo "Creating directories..."
	@mkdir -p logs data
	@echo "Creating sample data..."
	@python scripts/create_sample_data.py || echo "Warning: Sample data creation failed (optional)"
	@echo "Setup complete!"

# Running
run:
	python run_app.py

run-dashboard:
	python run_app.py

run-api:
	python run_api.py

# Testing
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Development
lint:
	@echo "Running linter..."
	@if command -v flake8 > /dev/null; then \
		flake8 . --exclude=venv,env,.venv --max-line-length=120; \
	else \
		echo "flake8 not installed. Install with: pip install flake8"; \
	fi

format:
	@echo "Formatting code..."
	@if command -v black > /dev/null; then \
		black . --exclude=venv,env,.venv; \
	else \
		echo "black not installed. Install with: pip install black"; \
	fi

check: lint
	@echo "All checks passed!"

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	rm -rf build/ dist/ .eggs/

