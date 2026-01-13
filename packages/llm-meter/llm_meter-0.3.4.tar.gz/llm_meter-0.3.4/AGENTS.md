# AGENTS.md

## Dev environment tips
- Use `uv sync` to install all dependencies and create the virtual environment.
- Run the CLI directly using `uv run llm-meter --help` to verify your changes.
- Use `uv run python examples/fastapi_app.py` to test the middleware integration with a live server.
- The project documentation is managed in the `docs/` folder; ensure any new architecture changes are reflected there.
- Database migrations are not currently handled (direct SQLAlchemy `create_all`); if schema changes, delete `llm_usage.db` for a fresh start during development.

## Testing & Quality Control
- **Full Suite**: Run `uv run pytest --cov=llm_meter` to execute tests and verify 100% coverage.
- **Type Checking**: Run `uv run pyright` to ensure strict type safety. We use `TYPE_CHECKING` blocks to keep the core library lightweight.
- **Linting**: Run `uv run ruff check . --fix` to catch and correct most stylistic and logical issues.
- **Formatting**: Run `uv run ruff format .` before committing to ensure consistent code style.
- **Pre-commit**: It is highly recommended to run `uv run pre-commit run --all-files` manually if you want to verify everything before the git hook triggers.
- **Mocking**: When adding tests for new providers, use `unittest.mock.AsyncMock` to avoid making actual API calls.

## PR instructions
- **Strict Quality**: Every PR must pass `ruff`, `pyright`, and `pytest` with 100% coverage.
- **SOLID Consistency**: Ensure new components follow the existing Protocol-based architecture (e.g., `StorageEngine` and `ProviderInstrumenter`).
- **Title format**: `[llm-meter] <Title>` (e.g., `[llm-meter] Add Anthropic support`).
- **Dependencies**: Do not add new hard dependencies to `pyproject.toml` unless discussed; prefer the "Extra" pattern for optional provider SDKs.
