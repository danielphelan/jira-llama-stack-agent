# Model Provider Configuration Guide

This document explains how to configure and use different model providers with the Jira-Llama Stack Agent.

## Supported Providers

The agent supports three model providers through a unified abstraction layer:

1. **Ollama** - Run models locally (recommended for development)
2. **Llama Stack** - Meta's official framework
3. **OpenAI** - GPT-4, GPT-3.5, and compatible APIs

## Quick Start

### 1. Choose Your Provider

Edit `config/agent_config.yaml` and set the `provider` field:

```yaml
model_provider:
  provider: "ollama"  # Options: ollama, llama_stack, openai
```

### 2. Configure Provider Settings

Each provider has its own configuration section in the same file.

## Ollama Configuration

### Setup

1. Install Ollama: https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama3.3:70b
   # Or for a smaller model:
   ollama pull llama3.1:8b
   ```
3. Start Ollama server:
   ```bash
   ollama serve
   ```

### Configuration

```yaml
model_provider:
  provider: "ollama"

  ollama:
    model_name: "llama3.3:70b"
    base_url: "http://localhost:11434"  # Ollama's default port
    temperature: 0.7
    max_tokens: 4096
    top_p: 0.9
```

### Available Models

Popular Ollama models:
- `llama3.3:70b` - Latest Llama 3.3 (requires ~40GB RAM)
- `llama3.1:8b` - Smaller, faster (requires ~8GB RAM)
- `mixtral:8x7b` - High quality, efficient
- `phi3:mini` - Very small, fast (3.8B parameters)
- `codellama:13b` - Optimized for code

### Advantages

- ✅ Completely local - no API keys needed
- ✅ No usage costs
- ✅ Fast model switching
- ✅ Privacy - data never leaves your machine
- ✅ Built-in model management

### Requirements

- RAM: 8GB minimum, 16GB+ recommended
- Disk: 4-40GB per model
- Network: Only for initial model download

## Llama Stack Configuration

### Setup

1. Install Llama Stack:
   ```bash
   pip install llama-stack llama-stack-client
   ```
2. Start Llama Stack server:
   ```bash
   llama-stack-server --port 5000
   ```

### Configuration

```yaml
model_provider:
  provider: "llama_stack"

  llama_stack:
    model_name: "meta-llama/Llama-3.3-70B-Instruct"
    base_url: "http://localhost:5000"
    temperature: 0.7
    max_tokens: 4096
    top_p: 0.9
```

### Advantages

- ✅ Meta's official framework
- ✅ Advanced features (safety layers, memory)
- ✅ Production-ready
- ✅ Integrated guardrails

## OpenAI Configuration

### Setup

1. Get an API key from https://platform.openai.com/api-keys
2. Set environment variable:
   ```bash
   export OPENAI_API_KEY=sk-your-api-key-here
   ```

### Configuration

```yaml
model_provider:
  provider: "openai"

  openai:
    model_name: "gpt-4"  # Or: gpt-4-turbo, gpt-3.5-turbo
    api_key: "${OPENAI_API_KEY}"  # Reads from environment
    temperature: 0.7
    max_tokens: 4096
```

### Available Models

- `gpt-4` - Highest quality
- `gpt-4-turbo` - Faster, cheaper
- `gpt-3.5-turbo` - Fast and economical

### OpenAI-Compatible APIs

You can also use OpenAI-compatible APIs (Together AI, Azure OpenAI, etc.):

```yaml
openai:
  model_name: "meta-llama/Llama-3-70b-chat-hf"
  api_key: "${API_KEY}"
  base_url: "https://api.together.xyz/v1"  # Example: Together AI
```

### Advantages

- ✅ Highest quality responses
- ✅ No local setup required
- ✅ Consistent availability
- ✅ Regular model updates

### Costs

- GPT-4: ~$0.03 per 1K tokens
- GPT-4-turbo: ~$0.01 per 1K tokens
- GPT-3.5-turbo: ~$0.002 per 1K tokens

Typical story analysis costs: $0.05-$0.20 per story

## Environment Variables

You can override configuration using environment variables:

```bash
# Ollama
export MODEL_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.3:70b

# Llama Stack
export MODEL_PROVIDER=llama_stack
export LLAMA_STACK_BASE_URL=http://localhost:5000
export LLAMA_STACK_MODEL=meta-llama/Llama-3.3-70B-Instruct

# OpenAI
export MODEL_PROVIDER=openai
export OPENAI_API_KEY=sk-your-key
export OPENAI_MODEL=gpt-4
```

## Switching Between Providers

### Option 1: Edit Config File

Change the `provider` field in `config/agent_config.yaml`:

```yaml
model_provider:
  provider: "ollama"  # Change this
```

### Option 2: Use Environment Variable

```bash
export MODEL_PROVIDER=ollama
```

### Option 3: Programmatic Override

```python
from src.agent.core import RequirementsAgent

agent = RequirementsAgent(
    provider_override="ollama"
)
```

## Recommendations

### For Development
**Use Ollama** with `llama3.1:8b` or `phi3:mini`
- Fast iteration
- No costs
- Good quality for testing

### For Production (Self-Hosted)
**Use Llama Stack** with `Llama-3.3-70B-Instruct`
- Production-ready
- Safety features
- Full control

### For Production (Cloud)
**Use OpenAI** with `gpt-4-turbo`
- Consistent quality
- No infrastructure
- Predictable costs

## Troubleshooting

### Ollama: "Connection refused"

Check if Ollama is running:
```bash
ollama list
```

Start the server:
```bash
ollama serve
```

### Ollama: Model not found

Pull the model:
```bash
ollama pull llama3.3:70b
```

### OpenAI: Authentication error

Verify your API key is set:
```bash
echo $OPENAI_API_KEY
```

### Llama Stack: Server not responding

Start the Llama Stack server:
```bash
llama-stack-server --port 5000
```

## Performance Comparison

| Provider | Speed | Quality | Cost | Setup |
|----------|-------|---------|------|-------|
| Ollama (8B) | ⚡⚡⚡ | ⭐⭐⭐ | Free | Easy |
| Ollama (70B) | ⚡⚡ | ⭐⭐⭐⭐ | Free | Medium |
| Llama Stack | ⚡⚡ | ⭐⭐⭐⭐ | Free | Medium |
| OpenAI GPT-4 | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | $$$ | Very Easy |

## Advanced: Custom Providers

You can add custom providers by implementing the `BaseModelProvider` interface:

```python
from src.providers import BaseModelProvider, ModelProviderFactory

class CustomProvider(BaseModelProvider):
    async def chat_completion(self, messages, **kwargs):
        # Your implementation
        pass

    # Implement other required methods...

# Register it
ModelProviderFactory.register_provider("custom", CustomProvider)
```

## Next Steps

- See `config/agent_config.yaml` for full configuration options
- Check `.env.example` for environment variable examples
- Read the main README for overall setup instructions
