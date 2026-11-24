import json
from types import SimpleNamespace

from maze_agent.loop import run_agent
from maze_agent.registry import ToolRegistry
from maze_agent.tools import MAZE_URL, page_text, read_web_page


def make_registry() -> ToolRegistry:
    reg = ToolRegistry()

    @reg.register
    def echo(text: str) -> str:
        """Echo the text back."""
        return f"echo:{text}"

    return reg


def reply(text="", calls=()):
    tool_calls = [
        SimpleNamespace(id=f"c{i}", function=SimpleNamespace(name=n, arguments=json.dumps(a)))
        for i, (n, a) in enumerate(calls)
    ]
    message = SimpleNamespace(content=text, tool_calls=tool_calls or None)
    return SimpleNamespace(model="fake", choices=[SimpleNamespace(message=message)])


class FakeClient:
    def __init__(self, replies):
        self._replies = iter(replies)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **_):
        return next(self._replies)


def test_schema_is_built_from_the_function():
    schema = make_registry().schemas()[0]["function"]
    assert schema["name"] == "echo"
    assert schema["description"] == "Echo the text back."
    assert schema["parameters"]["required"] == ["text"]


def test_tool_errors_become_text_for_the_model():
    reg = make_registry()
    assert reg.run("echo", "not json").startswith("The tool call failed")
    assert reg.run("missing", "{}").startswith("Unknown tool")


def test_loop_runs_tool_then_answers():
    client = FakeClient([reply(calls=[("echo", {"text": "hi"})]), reply("all done")])
    result = run_agent("go", client, "fake", make_registry())
    assert result.finished and result.answer == "all done"
    assert result.steps == 2 and result.tool_calls[0][0] == "echo"


def test_loop_stops_at_max_steps(tmp_path):
    client = FakeClient([reply(calls=[("echo", {"text": "x"})])] * 3)
    log = tmp_path / "run.jsonl"
    result = run_agent("go", client, "fake", make_registry(), max_steps=3, log_path=log)
    assert not result.finished and result.steps == 3
    assert len(log.read_text().splitlines()) == 6  # a step line and a tool line per step


def test_empty_reply_is_retried():
    client = FakeClient([reply(""), reply("finally")])
    assert run_agent("go", client, "fake", make_registry()).answer == "finally"


def test_page_text_strips_html():
    assert page_text("<html><body><h1>Room</h1><p>Exit</p></body></html>") == "Room\nExit"


def test_tool_refuses_pages_outside_the_maze():
    assert "only reads maze pages" in read_web_page("https://example.com")
    assert MAZE_URL in read_web_page("https://example.com")
