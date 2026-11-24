# CONVENTIONS - maze-agent-harness

- Pure Python 3.12+ project managed with `uv`. Source in `src/maze_agent/`, tests in `tests/`.
- One responsibility per module; keep modules under 200 lines and functions under 50.
- Tools are plain functions with string arguments, a docstring and a string return,
  registered with `@registry.register`. Tools must never raise past the registry.
- Env vars are `SCREAMING_SNAKE_CASE` (`OPENROUTER_API_KEY`, `MAZE_MODEL`). Never commit `.env`.
- Tests use a fake client; no network and no key in `pytest`.
- Finish line: `uv run pytest` and `uv run ruff check .` both clean.
