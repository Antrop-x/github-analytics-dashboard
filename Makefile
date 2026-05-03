.PHONY: help install install-dev test test-verbose test-coverage run clean lint format check type-check build

help:
	@echo "GitHub Analytics Dashboard - Makefile Commands"
	@echo ""
	@echo "Commands:"
	@echo "  make install          Install dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make test             Run tests"
	@echo "  make test-verbose     Run tests with verbose output"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo "  make run              Run the Streamlit app"
	@echo "  make lint             Run linting checks"
	@echo "  make format           Format code with black"
	@echo "  make type-check       Run type checking with mypy"
	@echo "  make check            Run all checks (lint + test + type)"
	@echo "  make build            Build package"
	@echo "  make clean            Clean up cache and build files"
	@echo ""

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install ruff mypy pytest-cov

test:
	python -m pytest tests/

test-verbose:
	python -m pytest tests/ -v -s

test-coverage:
	python -m pytest tests/ --cov=. --cov-report=html --cov-report=term

run:
	streamlit run app.py

lint:
	python -m pylint core/ services/ infrastructure/ config/ --fail-under=7.0 2>/dev/null || true

format:
	python -m black core/ services/ infrastructure/ config/ tests/

type-check:
	python -m mypy core/ services/ infrastructure/ config/ --ignore-missing-imports

check: lint test type-check
	@echo "All checks passed!"

build:
	python -m build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .coverage -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
