# claude-code-relay

Local proxy that exposes Claude CLI as an OpenAI-compatible API server.

Use your existing Claude CLI installation with any OpenAI-compatible client.

## Why?

- You already have Claude CLI working with your subscription
- You want to use tools that expect OpenAI API format
- No separate API key needed - uses your local Claude CLI

## Installation

### Node.js / Bun

```bash
npx claude-code-relay serve
# or
bunx claude-code-relay serve
# or install globally
npm install -g claude-code-relay
```

### Python

```bash
pip install claude-code-relay
```

## Usage

### Start the server

```bash
# Node
npx claude-code-relay serve --port 52014

# Python
claude-code-relay serve --port 52014
```

### Use with OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:52014/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="sonnet",  # or "opus", "haiku"
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "http://localhost:52014/v1",
  apiKey: "not-needed",
});

const response = await client.chat.completions.create({
  model: "sonnet",
  messages: [{ role: "user", content: "Hello!" }],
});
```

### Use with LiteLLM

```python
from litellm import completion

response = completion(
    model="openai/sonnet",
    api_base="http://localhost:52014/v1",
    api_key="not-needed",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Use with Vercel AI SDK

```typescript
import { createOpenAICompatible } from "@ai-sdk/openai-compatible";
import { generateText } from "ai";

const claude = createOpenAICompatible({
  name: "claude-code-relay",
  baseURL: "http://localhost:52014/v1",
  apiKey: "not-needed",
});

const { text } = await generateText({
  model: claude.chatModel("sonnet"),
  prompt: "Hello!",
});
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chat/completions` | POST | Chat completions (streaming supported) |
| `/v1/models` | GET | List available models |
| `/health` | GET | Health check |

## OpenAI API Compatibility

### Supported Features

| Feature | Status | Notes |
|---------|--------|-------|
| `model` | Supported | `sonnet`, `opus`, `haiku` (+ aliases below) |
| `messages` | Supported | `system`, `user`, `assistant` roles |
| `stream` | Supported | SSE streaming |
| System prompts | Supported | Via `system` role in messages |

### Model Aliases

These model names are normalized to Claude CLI format:

| Input | Maps to |
|-------|---------|
| `sonnet` | `sonnet` |
| `opus` | `opus` |
| `haiku` | `haiku` |
| `claude-3-sonnet` | `sonnet` |
| `claude-3-opus` | `opus` |
| `claude-3-haiku` | `haiku` |
| `claude-sonnet-4` | `sonnet` |
| `claude-opus-4` | `opus` |

### Not Supported

These parameters are accepted but **ignored** (not passed to Claude CLI):

| Parameter | Status |
|-----------|--------|
| `temperature` | Ignored |
| `max_tokens` | Ignored |
| `top_p` | Ignored |
| `stop` | Ignored |
| `n` | Not supported |
| `presence_penalty` | Not supported |
| `frequency_penalty` | Not supported |
| `logit_bias` | Not supported |
| `response_format` | Not supported |
| `tools` / `functions` | Not supported |
| `tool_choice` | Not supported |
| `seed` | Not supported |
| `logprobs` | Not supported |
| `user` | Not supported |

### Response Limitations

- `usage` tokens are always `0` (not tracked by Claude CLI)
- `finish_reason` is always `"stop"` (no length/tool_calls detection)

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDE_CODE_RELAY_PORT` | `52014` | Server port (Python only) |
| `CLAUDE_CODE_RELAY_HOST` | `127.0.0.1` | Host to bind (Python only) |
| `CLAUDE_CLI_PATH` | `claude` | Path to Claude CLI binary |
| `CLAUDE_CODE_RELAY_TIMEOUT` | `300` | Request timeout in seconds |
| `CLAUDE_CODE_RELAY_VERBOSE` | `false` | Enable verbose logging (`1` or `true`) |

### CLI Options

```
claude-code-relay serve [options]

Options:
  --port, -p <port>      Server port (default: 52014)
  --host <host>          Host to bind (default: 127.0.0.1)
  --claude-path <path>   Path to Claude CLI
  --timeout <seconds>    Request timeout (default: 300)
  --verbose, -v          Enable verbose logging
```

## Requirements

- Claude CLI installed and authenticated
- Python 3.10+ or Node.js 18+

## License

MIT - see [LICENSE](LICENSE)

**Disclaimer**: Unofficial community project. Users are responsible for compliance with Anthropic's Terms of Service.
