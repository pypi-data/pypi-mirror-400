# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

PYTHON_EXE := $(shell uv run python -c "import sys; print(sys.executable)")
PYO3_ENV   := PYO3_PYTHON=$(PYTHON_EXE)

PY_SRC  := .
PY_TEST := tests

# ---------------------------------------------------------------------
# Meta targets
# ---------------------------------------------------------------------

.PHONY: all check check_py check_rs pipeline dev

all: check
check: check_py check_rs

check_py: lint_py test_py
check_rs: lint_rs test_rs

# Developer-friendly full pipeline
pipeline:
	$(MAKE) lint_rs
	$(MAKE) test_rs
	$(MAKE) develop
	$(MAKE) lint_py
	$(MAKE) test_py

dev: develop

# ---------------------------------------------------------------------
# Python
# ---------------------------------------------------------------------

.PHONY: lint_py test_py

lint_py:
	uv run ruff check $(PY_SRC) --fix
	uv run ruff format $(PY_SRC)

test_py:
	uv run pytest $(PY_TEST)

# ---------------------------------------------------------------------
# Rust
# ---------------------------------------------------------------------

.PHONY: lint_rs test_rs

lint_rs:
	cargo fmt

test_rs:
	$(PYO3_ENV) cargo test

# ---------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------

.PHONY: develop

develop:
	maturin develop
