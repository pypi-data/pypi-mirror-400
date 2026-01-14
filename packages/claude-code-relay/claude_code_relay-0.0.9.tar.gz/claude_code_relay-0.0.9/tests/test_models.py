"""Tests for OpenAI-compatible models."""

from claude_code_relay.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    Choice,
    Usage,
)


def test_chat_message():
    msg = ChatMessage(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"


def test_chat_completion_request_from_dict():
    data = {
        "model": "sonnet",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True,
    }
    request = ChatCompletionRequest.from_dict(data)
    assert request.model == "sonnet"
    assert request.stream is True
    assert len(request.messages) == 1
    assert request.messages[0].content == "Hello"


def test_chat_completion_request_defaults():
    data = {
        "messages": [{"role": "user", "content": "Hello"}],
    }
    request = ChatCompletionRequest.from_dict(data)
    assert request.model == "sonnet"  # default
    assert request.stream is False  # default


def test_chat_completion_response():
    response = ChatCompletionResponse(
        model="sonnet",
        choices=[
            Choice(
                message=ChatMessage(role="assistant", content="Hi there!"),
            )
        ],
        usage=Usage(),
    )
    assert response.model == "sonnet"
    assert response.object == "chat.completion"
    assert response.choices[0].message.content == "Hi there!"
    assert response.id.startswith("chatcmpl-")
    assert response.usage.total_tokens == 0
