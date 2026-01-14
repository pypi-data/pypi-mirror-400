# Repository Guidelines

## Project Structure & Module Organization
The core library lives in `pysolidarity/`, with API clients, resources, and helpers in
modules like `client.py`, `resources/`, and `http.py`. Packaging metadata is in
`pyproject.toml`, and build artifacts land in `dist/`. There is currently no `tests/`
directory; add tests alongside a new `tests/` package if you expand coverage.

## Build, Test, and Development Commands
- `pip install -e .[dev]`: install editable package plus dev tooling (pytest, ruff, mypy).
- `python -m pytest`: run tests (when present).
- `ruff check .`: run linting with the configured rule set and line length.
- `mypy pysolidarity`: run strict type checks for the package.
- `python -m build`: build sdist and wheel into `dist/`.

## Coding Style & Naming Conventions
- Python, 4-space indentation; keep lines to 100 chars (see `tool.ruff`).
- Use `snake_case` for functions/variables and `PascalCase` for classes.
- Keep modules small and focused; new API endpoints should go under
  `pysolidarity/resources/`.

## Testing Guidelines
- Use `pytest` with descriptive test names like `test_users_create_or_update`.
- Prefer request/response mocking via `responses` when hitting HTTP logic.
- No coverage thresholds are enforced yet; add tests for new behavior.

## Commit & Pull Request Guidelines
- Commit messages follow a short, imperative style (e.g., `Add rate limit support`).
- PRs should describe the change, link relevant issues, and include usage examples
  or test results when behavior changes.

## Configuration Tips
- Required environment variable: `SOLIDARITY_API_KEY` for authenticated API calls.
