"""Wrapper for Claude CLI subprocess calls."""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CLIConfig:
    """Configuration for Claude CLI."""

    cli_path: str = "claude"
    timeout: int = 300
    verbose: bool = False

    @classmethod
    def from_env(cls) -> CLIConfig:
        """Create config from environment variables."""
        return cls(
            cli_path=os.getenv("CLAUDE_CLI_PATH", "claude"),
            timeout=int(os.getenv("CLAUDE_CODE_RELAY_TIMEOUT", "300")),
            verbose=os.getenv("CLAUDE_CODE_RELAY_VERBOSE", "").lower() in ("1", "true"),
        )


class ClaudeCLI:
    """Wrapper for Claude CLI subprocess calls."""

    MODELS = {
        "sonnet": "sonnet",
        "opus": "opus",
        "haiku": "haiku",
        "claude-3-sonnet": "sonnet",
        "claude-3-opus": "opus",
        "claude-3-haiku": "haiku",
        "claude-sonnet-4": "sonnet",
        "claude-opus-4": "opus",
    }

    def __init__(self, config: CLIConfig | None = None) -> None:
        self.config = config or CLIConfig.from_env()
        self._validate_cli()

    def _validate_cli(self) -> None:
        """Check if Claude CLI is available."""
        cli_path = shutil.which(self.config.cli_path)
        if not cli_path:
            raise RuntimeError(
                f"Claude CLI not found at '{self.config.cli_path}'. "
                "Please install it or set CLAUDE_CLI_PATH."
            )
        logger.info(f"Using Claude CLI at: {cli_path}")

    def _normalize_model(self, model: str) -> str:
        """Normalize model name to Claude CLI format."""
        return self.MODELS.get(model.lower(), "sonnet")

    def _build_prompt(
        self,
        messages: list[dict[str, Any]],
        system_prompt: str | None = None,
    ) -> str:
        """Convert OpenAI messages to a single prompt string."""
        parts = []

        # Extract system prompt from messages if not provided
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
                break

        if system_prompt:
            parts.append(f"System: {system_prompt}\n")

        for msg in messages:
            if msg["role"] == "system":
                continue
            elif msg["role"] == "user":
                parts.append(f"Human: {msg['content']}\n")
            elif msg["role"] == "assistant":
                parts.append(f"Assistant: {msg['content']}\n")

        parts.append("Assistant:")
        return "\n".join(parts)

    def complete(
        self,
        messages: list[dict[str, Any]],
        model: str = "sonnet",
        system_prompt: str | None = None,
    ) -> str:
        """Run a non-streaming completion."""
        prompt = self._build_prompt(messages, system_prompt)
        normalized_model = self._normalize_model(model)

        cmd = [
            self.config.cli_path,
            "-p",
            "--model", normalized_model,
            "--output-format", "text",
        ]

        if self.config.verbose:
            logger.info(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
            )
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"Claude CLI timeout after {self.config.timeout}s") from e

        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI failed: {result.stderr}")

        return result.stdout.strip()

    def stream(
        self,
        messages: list[dict[str, Any]],
        model: str = "sonnet",
        system_prompt: str | None = None,
    ) -> Iterator[str]:
        """Run a streaming completion."""
        prompt = self._build_prompt(messages, system_prompt)
        normalized_model = self._normalize_model(model)

        cmd = [
            self.config.cli_path,
            "-p",
            "--model", normalized_model,
            "--output-format", "stream-json",
        ]

        if self.config.verbose:
            logger.info(f"Running: {' '.join(cmd)}")

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Send prompt and close stdin
        assert proc.stdin is not None
        proc.stdin.write(prompt)
        proc.stdin.close()

        # Stream output
        assert proc.stdout is not None

        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                # Extract text content from stream-json format
                if "content" in data:
                    yield data["content"]
                elif "text" in data:
                    yield data["text"]
                elif "delta" in data and "text" in data["delta"]:
                    yield data["delta"]["text"]
            except json.JSONDecodeError:
                # Not JSON, might be raw text
                if not line.startswith("{"):
                    yield line

        proc.wait()

        if proc.returncode != 0:
            assert proc.stderr is not None
            error = proc.stderr.read()
            logger.error(f"Claude CLI error: {error}")
