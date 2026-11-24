"""Tool registry: turn plain Python functions into model-callable tools.

The model never sees our code, only a JSON description. Here that description is
generated from the function's name, docstring and signature, so a tool is defined
once instead of twice.
"""

import inspect
import json
from collections.abc import Callable
from typing import Any


class ToolRegistry:
    """Holds tools, describes them to the model and runs them on request."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., str]] = {}

    def register(self, func: Callable[..., str]) -> Callable[..., str]:
        """Decorator: add a function whose arguments are all strings and which returns a string."""
        self._tools[func.__name__] = func
        return func

    @property
    def names(self) -> list[str]:
        return list(self._tools)

    def schemas(self) -> list[dict[str, Any]]:
        """The JSON tool descriptions to send to the model."""
        return [self._schema(func) for func in self._tools.values()]

    def run(self, name: str, raw_arguments: str) -> str:
        """Run a tool. Any failure becomes text, so the model can read it and recover."""
        func = self._tools.get(name)
        if func is None:
            return f"Unknown tool '{name}'. Available tools: {', '.join(self._tools)}"
        try:
            return func(**json.loads(raw_arguments or "{}"))
        except Exception as error:  # noqa: BLE001 - the model should see every failure
            return f"The tool call failed: {error}"

    @staticmethod
    def _schema(func: Callable[..., str]) -> dict[str, Any]:
        params = inspect.signature(func).parameters
        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": inspect.getdoc(func) or func.__name__,
                "parameters": {
                    "type": "object",
                    "properties": {name: {"type": "string"} for name in params},
                    "required": [n for n, p in params.items() if p.default is p.empty],
                },
            },
        }
