"""OpenAI-compatible request/response models using dataclasses."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class ChatMessage:
    """A chat message."""

    role: Literal["system", "user", "assistant"]
    content: str


@dataclass
class ChatCompletionRequest:
    """OpenAI-compatible chat completion request."""

    model: str
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    stop: str | list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatCompletionRequest:
        """Create from dictionary."""
        messages = [
            ChatMessage(role=m["role"], content=m["content"])
            for m in data.get("messages", [])
        ]
        return cls(
            model=data.get("model", "sonnet"),
            messages=messages,
            stream=data.get("stream", False),
            temperature=data.get("temperature"),
            max_tokens=data.get("max_tokens"),
            top_p=data.get("top_p"),
            stop=data.get("stop"),
        )


@dataclass
class Choice:
    """A completion choice."""

    message: ChatMessage
    index: int = 0
    finish_reason: Literal["stop", "length", "tool_calls"] | None = "stop"


@dataclass
class Usage:
    """Token usage statistics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


def _default_id() -> str:
    return f"chatcmpl-{uuid.uuid4().hex[:12]}"


def _default_time() -> int:
    return int(time.time())


@dataclass
class ChatCompletionResponse:
    """OpenAI-compatible chat completion response."""

    model: str
    choices: list[Choice]
    id: str = field(default_factory=_default_id)
    object: Literal["chat.completion"] = "chat.completion"
    created: int = field(default_factory=_default_time)
    usage: Usage = field(default_factory=Usage)


@dataclass
class ModelInfo:
    """Model information."""

    id: str
    object: Literal["model"] = "model"
    created: int = field(default_factory=_default_time)
    owned_by: str = "anthropic"


@dataclass
class ModelList:
    """List of available models."""

    data: list[ModelInfo]
    object: Literal["list"] = "list"
