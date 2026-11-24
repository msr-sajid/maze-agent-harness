# maze-agent-harness

A small AI agent harness built from first principles, in about 150 lines of Python.
It sends a free language model through an online maze, one web page at a time, and
brings back the message waiting at the exit.

The point is the harness, not the model: a **tool registry**, a **tool-call loop**
and a **step log**. Swap the model and the harness stays the same.

## How it works

```
task ──> run_agent loop ──> model ──> asks for a tool? ──yes──> registry.run() ──┐
              ^                              │no                                  │
              └──────── tool result ─────────┴──> final answer                    │
              └───────────────────────────────────────────────────────────────────┘
```

| File | Responsibility |
|---|---|
| `src/maze_agent/registry.py` | Turns a plain function into a model-callable tool. The JSON description is generated from its name, docstring and signature. Tool failures become text the model can read and recover from. |
| `src/maze_agent/tools.py` | The agent's tools. One so far: `read_web_page`, which only reads maze pages. |
| `src/maze_agent/loop.py` | Calls the model, runs the tools it asks for, repeats. Stops on a text answer or after `max_steps`. Retries empty replies. Writes a JSONL log of every step. |
| `src/maze_agent/cli.py` | `maze-agent` command: loads the key, builds the client, runs the loop. |

## Run it

You need [uv](https://docs.astral.sh/uv/) and a free [OpenRouter](https://openrouter.ai) key.
Free models need both "free endpoints" switches turned on at
https://openrouter.ai/settings/privacy. Nothing you send to free models is private.

```bash
cp .env.example .env        # then paste your OPENROUTER_API_KEY
uv sync
uv run maze-agent           # add --model <name> or --max-steps 40 if you like
```

Each run writes `runs/last_run.jsonl`: which model answered each step, which tool was
called with which arguments, and how much text came back.

## Test it

```bash
uv run pytest
uv run ruff check .
```

The tests use a fake model client, so they need no key and no network.

## What I changed from the course notebook

- Moved the notebook code into a package with one responsibility per file.
- Replaced the hand-written tool JSON with a registry that builds it from the function.
- Tool errors, unknown tools and bad JSON all go back to the model as text.
- Added a JSONL step log so a run can be inspected afterwards.
- Added tests for the registry, the loop, the step limit and the empty-reply retry.

## Credit

The maze (https://maze.edwarddonner.com) and the original notebook idea come from
Ed Donner's course "AI FDE: The Forward Deployed Engineer & Agentic AI Architect".
This repo is my own rewrite of the harness, not a copy of the course material.
