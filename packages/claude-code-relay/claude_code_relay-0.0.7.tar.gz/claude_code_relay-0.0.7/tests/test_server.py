"""Tests for the HTTP server."""

import json
import threading
import time
import urllib.request
import urllib.error
from unittest.mock import patch, MagicMock

import pytest

from claude_code_relay.server import create_server


@pytest.fixture
def server():
    """Create test server with mocked CLI."""
    with patch("claude_code_relay.server.ClaudeCLI") as mock_cli_class:
        mock_cli = MagicMock()
        mock_cli.complete = MagicMock(return_value="Hello, world!")
        mock_cli.stream = MagicMock(return_value=iter(["Hello", ", ", "world", "!"]))
        mock_cli_class.return_value = mock_cli

        server = create_server(host="127.0.0.1", port=0)  # port 0 = random available
        port = server.server_address[1]

        # Start server in background thread
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

        # Wait for server to be ready
        time.sleep(0.1)

        yield f"http://127.0.0.1:{port}"

        server.shutdown()


def _get(url: str) -> dict:
    """Make GET request and return JSON."""
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode())


def _post(url: str, data: dict) -> dict:
    """Make POST request and return JSON."""
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def test_health_check(server):
    data = _get(f"{server}/health")
    assert data["status"] == "ok"
    assert data["cli_available"] is True


def test_list_models(server):
    data = _get(f"{server}/v1/models")
    assert data["object"] == "list"
    assert len(data["data"]) > 0
    assert any(m["id"] == "sonnet" for m in data["data"])


def test_chat_completion(server):
    data = _post(
        f"{server}/v1/chat/completions",
        {"model": "sonnet", "messages": [{"role": "user", "content": "Hello"}]},
    )
    assert data["object"] == "chat.completion"
    assert data["model"] == "sonnet"
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["content"] == "Hello, world!"
