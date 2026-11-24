"""The agent loop: call the model, run the tools it asks for, repeat until it answers."""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from maze_agent.registry import ToolRegistry

SYSTEM_PROMPT = (
    "You are an agent that completes tasks by using your tools, one step at a time. "
    "Reply in Markdown. Put any map or diagram in a code block. Do not use emojis."
)


@dataclass
class AgentResult:
    answer: str
    steps: int
    tool_calls: list[tuple[str, str]] = field(default_factory=list)
    finished: bool = True


def _log(log_path: Path | None, event: dict[str, Any]) -> None:
    """Append one JSON line per event, so a run can be replayed and inspected."""
    if log_path:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"ts": time.time(), **event}) + "\n")


def run_agent(
    task: str,
    client: Any,
    model: str,
    registry: ToolRegistry,
    max_steps: int = 25,
    log_path: Path | None = None,
) -> AgentResult:
    """Run the loop. Stops on a text answer with no tool call, or after max_steps."""
    messages: list[Any] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]
    result = AgentResult(answer="", steps=0, finished=False)
    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=model, messages=messages, tools=registry.schemas()
        )
        message = response.choices[0].message
        text = (message.content or "").strip()
        result.steps = step
        _log(log_path, {"step": step, "model": response.model, "text": text})

        if message.tool_calls:
            messages.append(message)
            for call in message.tool_calls:
                output = registry.run(call.function.name, call.function.arguments)
                result.tool_calls.append((call.function.name, call.function.arguments))
                _log(log_path, {"step": step, "tool": call.function.name,
                                "args": call.function.arguments, "chars": len(output)})
                messages.append({"role": "tool", "tool_call_id": call.id, "content": output})
        elif text:
            result.answer, result.finished = text, True
            return result
        # an empty reply with no tool call: a free model glitch, so just ask again
    return result
