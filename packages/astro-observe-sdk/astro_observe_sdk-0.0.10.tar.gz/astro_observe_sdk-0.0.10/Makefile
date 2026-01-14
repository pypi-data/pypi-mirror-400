.PHONY: check
check:
	@echo "Checking version match in different files..."
	@python scripts/check_version_match.py
	@echo "Running pre-commits..."
	@uv run prek run -a
	@echo "Checking code with mypy..."
	@uv run mypy


.PHONY: test
test:
	@echo "Running tests..."
	@uv run -m pytest -s


.PHONY: build
build:
	@echo "Building..."
	@rm -rf dist/*
	@uv build
