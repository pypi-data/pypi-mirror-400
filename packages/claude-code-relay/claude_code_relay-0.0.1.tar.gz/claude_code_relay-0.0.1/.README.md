# claude-code-relay

Local proxy that exposes Claude CLI as an OpenAI-compatible API server.

Use your existing Claude CLI installation with any OpenAI-compatible client (LiteLLM, Vercel AI SDK, LangChain, etc).

## Why?

- You already have Claude CLI working with your subscription
- You want to use tools that expect OpenAI API format
- No separate API key needed - uses your local Claude CLI

## Installation

### Python

```bash
pip install claude-code-relay
# or
uv pip install claude-code-relay
# or
poetry add claude-code-relay
```

### Node.js / Bun

```bash
npx claude-code-relay serve
# or
bunx claude-code-relay serve
# or install globally
npm install -g claude-code-relay
```

## Usage

### Start the server

```bash
# Python
claude-code-relay serve --port 52014

# Node
npx claude-code-relay serve --port 52014
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

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDE_RELAY_PORT` | `52014` | Server port |
| `CLAUDE_CLI_PATH` | `claude` | Path to Claude CLI binary |
| `CLAUDE_RELAY_TIMEOUT` | `300` | Request timeout in seconds |

### CLI Options

```bash
claude-code-relay serve [options]

Options:
  --port, -p <port>      Server port (default: 52014)
  --host, -h <host>      Host to bind (default: 127.0.0.1)
  --claude-path <path>   Path to Claude CLI
  --timeout <seconds>    Request timeout (default: 300)
  --verbose, -v          Enable verbose logging
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chat/completions` | POST | Chat completions (streaming supported) |
| `/v1/models` | GET | List available models |
| `/health` | GET | Health check |

## Supported Features

- [x] Chat completions
- [x] Streaming (SSE)
- [x] Model selection (sonnet, opus, haiku)
- [x] System prompts
- [ ] Function calling / tools (planned)
- [ ] Vision / images (planned)

## Requirements

- Claude CLI installed and authenticated
- Python 3.10+ or Node.js 18+ / Bun

## License

MIT License - see [LICENSE](LICENSE)

**DISCLAIMER**: This is an unofficial community project. Users are responsible for their own compliance with Anthropic's Terms of Service.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
