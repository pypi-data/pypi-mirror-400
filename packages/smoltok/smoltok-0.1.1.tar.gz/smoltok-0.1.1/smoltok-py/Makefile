.PHONY: help
help:  ## Display this help screen
	@echo -e "\033[1mAvailable commands:\033[0m"
	@grep -E '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' | sort

.PHONY: clean
clean:  ## Clean uv cache
	uv cache clean

.PHONY: install
install:  ## Install dependencies with locked uv.lock
	uv sync --dev --locked

.PHONY: lock
lock:  ## Run uv lock
	uv lock

.PHONY: format
format:  ## Format code
	uv run ruff format .
	uv run ruff check --fix .

.PHONY: lint
lint:  ## Lint code and type check
	uv run ruff check .
	uv run ruff format --check .
	uv run ty check .

.PHONY dev-lint:
dev-lint: format  ## Format code and type check
	uv run ty check .

.PHONY: dev
dev: clean install  ## Build and install the package in development mode
	uv run maturin develop

.PHONY: build-release
build-release: clean install  ## Build the package for release
	uv run maturin build --release

.PHONY: example
example: dev  ## Run example test verbosely
	uv run pytest -v -s tests/test_example.py

.PHONY: test
test: dev  ## Run tests
	uv run pytest

.PHONY: bench-random-data
bench-random-data: build-release  ## Run benchmark on the random data (Python vs Rust)
	uv run python -m py_impl.bench.random_data --size 10_000 --vocab-size 512 --runs 5 --plot

.PHONY: bench-download
bench-download:  ## Run download dataset script
	uv run python -m py_impl.bench.download

.PHONY: bench-wikitext
bench-wikitext: build-release  ## Run training benchmark script (wikitext test set)
	uv run python -m py_impl.bench.wikitext --vocab-size 512 --train-python
	uv run python -m py_impl.bench.wikitext --vocab-size 1024 --train-python
	uv run python -m py_impl.bench.wikitext --vocab-size 2048 --train-python

.PHONY: publish
publish: build-release  ## Publish smoltok to pip
	uv run maturin publish
