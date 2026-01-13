# orter

Typer-based CLI tool that uses OpenRouter API.


## Installation

```bash
uvx orter
```

## Usage

### Environment Variable Setup

You can set the `OPENROUTER_API_KEY` environment variable, or use the `--api-key` option with each command.

### Models

List available models.

```bash
# Default output: human-readable table + default limit(20)
uv run orter models
uv run orter models list --limit 20

# Search
uv run orter models --search gpt-4o --limit 20

# Output in JSON format
uv run orter models --json

# Get specific model information
uv run orter models get openai/gpt-4o-mini
```

### Chat Completions

Send chat completion requests.

```bash
# Basic usage (recommended)
uv run orter chat completions -m "Hello"

# Specify model
uv run orter chat completions -m "Print Hello World in Python" --model "openai/gpt-4o"

# Enable streaming
uv run orter chat completions -m "Write a simple story" --stream

# Include system message
uv run orter chat completions -m "User message" --system "You are a helpful AI assistant."

# Output in JSON format
uv run orter chat completions -m "Hello" --json

# Using additional parameters
uv run orter chat completions -m "Write a creative story" \
  --temperature 0.9 \
  --max-tokens 500 \
  --model "openai/gpt-4o-mini"
```

### Generation

Query generation statistics.

```bash
# Get generation statistics (using id from chat completions response)
uv run orter generation get gen-xxxxxxxxxxxxxx

# Output in JSON format
uv run orter generation get gen-xxxxxxxxxxxxxx --json
```

### Raw (full API access)

```bash
uv run orter raw request GET api/v1/models
uv run orter raw request POST api/v1/chat/completions \
  --body '{"model":"openai/gpt-4o-mini","messages":[{"role":"user","content":"hi"}]}'
```

## Key Features

- Chat Completions API support
- Streaming support
- Models API support
- Generation statistics lookup
- Call any endpoint with raw (full API access)
- JSON output option
- Type safety guarantee

## Examples

### Simple Question

```bash
uv run orter chat completions -m "What are the advantages of Python?"
```

### Code Generation

```bash
uv run orter chat completions -m "Create a simple calculator function in Python" \
  --model "openai/gpt-4o-mini" \
  --temperature 0.7
```

### Streaming Response

```bash
uv run orter chat completions -m "Write a long story" --stream
```

## License

MIT


### Documentation References
- https://openrouter.ai/docs/api/api-reference/responses/create-responses.md
- https://openrouter.ai/docs/api/api-reference/o-auth/exchange-auth-code-for-api-key.md
- https://openrouter.ai/docs/api/api-reference/o-auth/create-auth-keys-code.md
- https://openrouter.ai/docs/api/api-reference/analytics/get-user-activity.md
- https://openrouter.ai/docs/api/api-reference/credits/get-credits.md
- https://openrouter.ai/docs/api/api-reference/credits/create-coinbase-charge.md
- https://openrouter.ai/docs/api/api-reference/embeddings/create-embeddings.md
- https://openrouter.ai/docs/api/api-reference/embeddings/list-embeddings-models.md
- https://openrouter.ai/docs/api/api-reference/generations/get-generation.md
- https://openrouter.ai/docs/api/api-reference/models/list-models-count.md
- https://openrouter.ai/docs/api/api-reference/models/get-models.md
- https://openrouter.ai/docs/api/api-reference/models/list-models-user.md
- https://openrouter.ai/docs/api/api-reference/endpoints/list-endpoints.md
- https://openrouter.ai/docs/api/api-reference/endpoints/list-endpoints-zdr.md
- https://openrouter.ai/docs/api/api-reference/parameters/get-parameters.md
- https://openrouter.ai/docs/api/api-reference/providers/list-providers.md
- https://openrouter.ai/docs/api/api-reference/api-keys/list.md
- https://openrouter.ai/docs/api/api-reference/api-keys/create-keys.md
- https://openrouter.ai/docs/api/api-reference/api-keys/get-key.md
- https://openrouter.ai/docs/api/api-reference/api-keys/delete-keys.md
- https://openrouter.ai/docs/api/api-reference/api-keys/update-keys.md
- https://openrouter.ai/docs/api/api-reference/api-keys/get-current-key.md
- https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request.md
- https://openrouter.ai/docs/api/api-reference/completions/create-completions.md