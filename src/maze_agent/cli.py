"""Command line entry point: `uv run maze-agent`."""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from maze_agent.loop import run_agent
from maze_agent.tools import MAZE_URL, registry

BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openrouter/free"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Send an agent through the maze.")
    parser.add_argument("--model", default=os.getenv("MAZE_MODEL", DEFAULT_MODEL))
    parser.add_argument("--max-steps", type=int, default=25)
    parser.add_argument("--log", type=Path, default=Path("runs/last_run.jsonl"))
    args = parser.parse_args(argv)

    load_dotenv(override=True)
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your key.")
        return 1

    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text("", encoding="utf-8")
    client = OpenAI(base_url=BASE_URL, api_key=api_key, timeout=120, max_retries=5)

    task = f"Have a look at {MAZE_URL} and do what it says."
    result = run_agent(task, client, args.model, registry, args.max_steps, args.log)

    print(result.answer or "The agent ran out of steps.")
    print(f"\nSteps: {result.steps}  Pages read: {len(result.tool_calls)}  Log: {args.log}")
    return 0 if result.finished else 2


if __name__ == "__main__":
    sys.exit(main())
