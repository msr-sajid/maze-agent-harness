"""The agent's tools. Right now there is one: read a page in the maze."""

import requests
from bs4 import BeautifulSoup

from maze_agent.registry import ToolRegistry

MAZE_URL = "https://maze.edwarddonner.com"

registry = ToolRegistry()


def page_text(html: str) -> str:
    """Strip a page down to its visible text."""
    body = BeautifulSoup(html, "html.parser").body
    return body.get_text(separator="\n", strip=True) if body else ""


@registry.register
def read_web_page(url: str) -> str:
    """Read a web page in the maze and return its text without the HTML."""
    if not url.startswith(MAZE_URL):
        return f"This tool only reads maze pages. Ask for a URL that starts with {MAZE_URL}"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return page_text(response.text)
