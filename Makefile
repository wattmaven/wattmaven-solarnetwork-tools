.PHONY: lint-check lint-fix format-check format-fix fix test pre-commit-tasks ci-smoke-test clean

VENV = .venv
RUFF = uv run ruff
PYTEST = uv run pytest

all: install  ## Install dependencies and set up project

install: ## Create venv and install dependencies
	uv venv
	uv sync --all-packages

lint-check: ## Check code with ruff
	$(RUFF) check .

lint-fix: ## Fix linting issues with ruff
	$(RUFF) check --fix .

format-check: ## Check code formatting
	$(RUFF) format --check .

format-fix: ## Fix code formatting
	$(RUFF) format .

fix: ## Run all linting and formatting checks
	make lint-fix format-fix

test: ## Run tests
	$(PYTEST)

pre-commit-tasks: ## Run pre-commit tasks
	make lint-check format-check test

ci-smoke-test: ## Run tests in CI
	make lint-check format-check test

clean: ## Clean up temporary files and virtual environment
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf $(VENV)
