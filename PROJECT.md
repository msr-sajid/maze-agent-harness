---
project_id: d57a8180-d7c1-461e-972e-f4778432eba3
status: live              # building | live | paused | archived
goal: "A small agent harness (tool registry, loop, step log) that walks a model through a maze"
domain: ai-agents
audience: Me, and anyone learning how agent harnesses work
---

# maze-agent-harness

> A first-principles agent harness that sends a free LLM through an online maze.

## Current state

_2026-11-24_ - Working. `uv run maze-agent` solved the maze in 12 steps on `openrouter/free`. 7 tests and ruff pass. Published to GitHub as a public repo.

## Goals

- Rewrite the course notebook as a clean, tested package that is my own.
- Document how the harness works for someone new to agents.

## Stack

Python 3.12, uv, OpenAI SDK pointed at OpenRouter, requests, BeautifulSoup, pytest, ruff.

## Stack Deviation

`dak init` scaffolds React/FastAPI/Postgres. This project is a command-line agent with no UI, database or server, so I removed the web scaffold and kept the DAK identity, PROJECT.md and CONVENTIONS.md. Alternative considered: wrapping the agent in a FastAPI + React app; rejected as unnecessary for a learning repo.

## Log

### Phase 1 - Refactor and publish (2026-11-24)

Turned `setup.ipynb` from the Udemy course into a package: registry, tools, loop, CLI, step log, tests.

**Lessons**
- Generating the tool JSON from the function signature removes the duplicate definition.
- Free models sometimes return empty replies; the loop retries instead of stopping.
