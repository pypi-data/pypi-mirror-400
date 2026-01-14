# Orbit SDK for Python

Track, monitor, and optimize your AI spend across OpenAI, Anthropic, and other LLM providers.

## Installation

```bash
pip install withorbit-sdk

# With OpenAI support
pip install withorbit-sdk[openai]

# With Anthropic support
pip install withorbit-sdk[anthropic]

# With all providers
pip install withorbit-sdk[all]
```

## Quick Start

### 1. Get your API key

Sign up at [Orbit](https://app.withorbit.io) and create an API key.

### 2. Initialize the SDK

```python
from withorbit_sdk import Orbit

orbit = Orbit(
    api_key="orb_live_xxxxxxxxxxxxxxxxxxxxxxxx",
    default_feature="my-app",  # Optional: default feature for all events
)
```

### 3. Track your LLM calls

#### Option A: Automatic tracking (Recommended)

Wrap your OpenAI or Anthropic client for automatic tracking:

```python
from openai import OpenAI
from withorbit_sdk import Orbit, WrapperOptions

orbit = Orbit(api_key="orb_live_xxx")
openai = orbit.wrap_openai(OpenAI(), WrapperOptions(feature="chat-assistant"))

# All API calls are now automatically tracked!
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello, world!"}],
)
```

Works with Anthropic too:

```python
from anthropic import Anthropic
from withorbit_sdk import Orbit, WrapperOptions

orbit = Orbit(api_key="orb_live_xxx")
anthropic = orbit.wrap_anthropic(Anthropic(), WrapperOptions(feature="document-analysis"))

message = anthropic.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Analyze this document..."}],
)
```

#### Option B: Manual tracking

For other providers or custom implementations:

```python
from withorbit_sdk import Orbit

orbit = Orbit(api_key="orb_live_xxx")

# Track a successful request
orbit.track(
    model="gpt-4o",
    input_tokens=150,
    output_tokens=50,
    latency_ms=1234,
    feature="summarization",
    environment="production",
)

# Track an error
orbit.track_error(
    model="gpt-4o",
    error_type="rate_limit_exceeded",
    error_message="Rate limit exceeded",
    feature="chat-assistant",
    input_tokens=150,
)
```

## Configuration

```python
from withorbit_sdk import Orbit, OrbitConfig

orbit = Orbit(config=OrbitConfig(
    # Required
    api_key="orb_live_xxx",

    # Optional
    base_url="https://app.withorbit.io/api/v1",  # Custom API endpoint
    default_feature="my-app",                    # Default feature name
    default_environment="production",            # 'production' | 'staging' | 'development'
    debug=False,                                 # Enable debug logging

    # Batching (for high-volume applications)
    batch_events=True,       # Batch events before sending
    batch_size=10,           # Max events per batch
    batch_interval=5.0,      # Max seconds before sending batch

    # Reliability
    retry=True,              # Retry failed requests
    max_retries=3,           # Max retry attempts
))
```

## Feature Attribution

Features are Orbit's key differentiator - they let you see exactly which parts of your application are consuming AI resources:

```python
# Track different features
orbit.track(
    model="gpt-4o",
    input_tokens=100,
    output_tokens=50,
    feature="chat-assistant",  # Attribute to chat feature
)

orbit.track(
    model="gpt-4o",
    input_tokens=500,
    output_tokens=200,
    feature="document-analysis",  # Attribute to doc analysis
)
```

Then in the Orbit dashboard, you'll see:
- Cost breakdown by feature
- Request volume by feature
- Error rates by feature
- And more!

## Context Manager Support

```python
from withorbit_sdk import Orbit

with Orbit(api_key="orb_live_xxx") as orbit:
    orbit.track(model="gpt-4o", input_tokens=100, output_tokens=50)
# Automatically flushes on exit
```

## Graceful Shutdown

For long-running processes, flush events before exit:

```python
# Before your process exits
orbit.shutdown()
```

## Event Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `model` | str | Yes | Model name (e.g., 'gpt-4o', 'claude-3-opus') |
| `input_tokens` | int | Yes | Number of input tokens |
| `output_tokens` | int | Yes | Number of output tokens |
| `provider` | str | No | Provider name (auto-detected if not provided) |
| `latency_ms` | int | No | Request latency in milliseconds |
| `feature` | str | No | Feature name for attribution |
| `environment` | str | No | Environment ('production', 'staging', 'development') |
| `status` | str | No | Request status ('success', 'error', 'timeout') |
| `error_type` | str | No | Error type if status is 'error' |
| `error_message` | str | No | Error message if status is 'error' |
| `user_id` | str | No | Your application's user ID |
| `session_id` | str | No | Session ID for grouping requests |
| `request_id` | str | No | Unique request ID for tracing |
| `metadata` | dict | No | Additional key-value metadata |

## License

MIT
