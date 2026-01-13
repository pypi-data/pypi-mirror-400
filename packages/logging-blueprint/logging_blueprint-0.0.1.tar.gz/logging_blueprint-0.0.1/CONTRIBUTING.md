# Contributing

## Local setup

- Use `make install` to sync dependencies with uv.
- Before sending changes, run `make lint` and `make test` to keep formatting, typing, and tests clean.

## Testing strategy

- Keep fast unit tests in-process for pure logic with explicit state.
- For realistic flows, spawn isolated subprocesses that execute temporary scripts copied from `tests/resources/examples`; avoid relying on installed entry points for tests.
- Use pytest’s built-in tempdir factories (`tmp_path`/`tmp_path_factory`) to create per-test working dirs, copy fixtures into them, and run `uv run` against those scripts so the repo stays untouched and state is process-local.
- Assert on exit codes, stdout, and stderr together; prefer deterministic fixtures over heavy mocking for config/logging behaviors.
- When performance matters, group related assertions into a single subprocess run rather than spawning many short-lived processes.
- Avoid pytest’s `monkeypatch`; prefer `unittest.mock` imported as `from unittest import mock`, and use context managers instead of decorators to keep patch scope tight.
