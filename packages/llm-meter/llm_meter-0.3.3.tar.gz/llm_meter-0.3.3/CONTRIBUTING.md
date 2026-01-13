# Contributing to llm-meter

First off, thank you for considering contributing to `llm-meter`! It's people like you that make it a great tool.

## Code of Conduct

Maintain a positive and respectful environment for all contributors.

## How Can I Contribute?

### Reporting Bugs
- Use the [GitHub issue tracker](https://github.com/doubledare704/llm-meter/issues) to report bugs.
- Include details about your environment and steps to reproduce the issue.

### Suggesting Enhancements
- Open an issue to discuss new features or improvements.

### Pull Requests
1. Fork the repo and create your branch from `main`.
2. Ensure `pre-commit` hooks are installed and passing.
3. Add tests for any new functionality.
4. Update documentation if necessary.
5. Submit a PR!

## Development Setup

We use `uv` for dependency management.

```bash
# Clone the repo
git clone https://github.com/doubledare704/llm-meter.git
cd llm-meter

# Sync dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

## Running Tests

```bash
uv run pytest --cov=llm_meter
```

## Linting & Formatting

```bash
uv run ruff check . --fix
uv run ruff format .
```

All code must pass strict `pyright` checks:

```bash
uv run pyright
```
