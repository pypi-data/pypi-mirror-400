"""HTTP server with OpenAI-compatible endpoints using stdlib only."""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING, Any

from .cli_wrapper import ClaudeCLI, CLIConfig
from .models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    Choice,
    ModelInfo,
    ModelList,
    Usage,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Global CLI instance (set by create_server)
_cli: ClaudeCLI | None = None
_verbose: bool = False


def _log(msg: str) -> None:
    """Log if verbose mode is enabled."""
    if _verbose:
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        ms = int((time.time() % 1) * 1000)
        print(f"[{timestamp}.{ms:03d}] {msg}")


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OpenAI-compatible API."""

    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        """Log using logging module instead of stderr."""
        logger.info("%s - %s", self.address_string(), format % args)

    def _send_json(self, data: dict[str, Any], status: int = 200) -> None:
        """Send JSON response."""
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message: str, status: int = 500) -> None:
        """Send error response."""
        self._send_json({"error": {"message": message, "type": "server_error"}}, status)

    def _send_sse_chunk(self, data: str) -> None:
        """Send SSE chunk."""
        chunk = f"data: {data}\n\n".encode()
        self.wfile.write(chunk)
        self.wfile.flush()

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/health":
            self._send_json({"status": "ok" if _cli else "degraded", "cli_available": _cli is not None})
        elif self.path == "/v1/models":
            now = int(time.time())
            models = ModelList(data=[
                ModelInfo(id="sonnet", created=now),
                ModelInfo(id="opus", created=now),
                ModelInfo(id="haiku", created=now),
            ])
            self._send_json(asdict(models))
        else:
            self._send_error("Not found", 404)

    def do_POST(self) -> None:
        """Handle POST requests."""
        if self.path != "/v1/chat/completions":
            self._send_error("Not found", 404)
            return

        if _cli is None:
            self._send_error("Claude CLI not available", 503)
            return

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            request = ChatCompletionRequest.from_dict(data)
        except (json.JSONDecodeError, ValueError) as e:
            self._send_error(f"Invalid request: {e}", 400)
            return

        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        chat_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created = int(time.time())

        msg_count = len(request.messages)
        last_msg = request.messages[-1].content[:30] if request.messages else ""
        _log(f"→ POST /v1/chat/completions model={request.model} stream={request.stream} msgs={msg_count} \"{last_msg}{'...' if len(last_msg) >= 30 else ''}\"")

        if request.stream:
            self._handle_stream(request, messages, chat_id, created)
        else:
            self._handle_completion(request, messages, chat_id, created)

    def _handle_completion(
        self,
        request: ChatCompletionRequest,
        messages: list[dict[str, Any]],
        chat_id: str,
        created: int,
    ) -> None:
        """Handle non-streaming completion."""
        assert _cli is not None

        try:
            content = _cli.complete(messages, model=request.model)
            _log(f"← response complete, length={len(content)}")
        except Exception as e:
            _log(f"← error: {e}")
            logger.error(f"Completion failed: {e}")
            self._send_error(str(e))
            return

        response = ChatCompletionResponse(
            id=chat_id,
            created=created,
            model=request.model,
            choices=[Choice(message=ChatMessage(role="assistant", content=content))],
            usage=Usage(),
        )
        self._send_json(asdict(response))

    def _handle_stream(
        self,
        request: ChatCompletionRequest,
        messages: list[dict[str, Any]],
        chat_id: str,
        created: int,
    ) -> None:
        """Handle streaming completion."""
        assert _cli is not None

        # Send headers for SSE
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        # Initial chunk with role
        initial = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": request.model,
            "choices": [{"index": 0, "delta": {"role": "assistant", "content": ""}, "finish_reason": None}],
        }
        self._send_sse_chunk(json.dumps(initial))

        total_len = 0
        try:
            for text in _cli.stream(messages, model=request.model):
                total_len += len(text)
                chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": request.model,
                    "choices": [{"index": 0, "delta": {"content": text}, "finish_reason": None}],
                }
                self._send_sse_chunk(json.dumps(chunk))
            _log(f"← stream complete, total length={total_len}")
        except Exception as e:
            _log(f"← stream error: {e}")
            logger.error(f"Streaming failed: {e}")
            error = json.dumps({"error": {"message": str(e), "type": "server_error"}})
            self._send_sse_chunk(error)

        # Final chunk
        final = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": request.model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        self._send_sse_chunk(json.dumps(final))
        self._send_sse_chunk("[DONE]")


def create_server(
    host: str = "127.0.0.1",
    port: int = 52014,
    config: CLIConfig | None = None,
    verbose: bool = False,
) -> HTTPServer:
    """Create HTTP server instance."""
    global _cli, _verbose
    _verbose = verbose

    try:
        _cli = ClaudeCLI(config)
    except RuntimeError as e:
        logger.error(f"Failed to initialize Claude CLI: {e}")
        _cli = None

    server = HTTPServer((host, port), RequestHandler)
    return server


def run_server(
    host: str = "127.0.0.1",
    port: int = 52014,
    config: CLIConfig | None = None,
    verbose: bool = False,
) -> None:
    """Run the server."""
    server = create_server(host, port, config, verbose=verbose)
    logger.info(f"Starting server on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()
