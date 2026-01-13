# Deadpipe Python SDK

**LLM observability that answers one question: "Is this prompt behaving the same as when it was last safe?"**

[![PyPI](https://img.shields.io/pypi/v/deadpipe)](https://pypi.org/project/deadpipe/)
[![Python](https://img.shields.io/pypi/pyversions/deadpipe)](https://pypi.org/project/deadpipe/)

## Installation

```bash
pip install deadpipe
```

## Quick Start

```python
from deadpipe import track
from openai import OpenAI

client = OpenAI()

with track(prompt_id="checkout_agent") as t:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Process refund for order 1938"}]
    )
    t.record(response)  # Captures 40+ metrics, builds baseline
```

That's it. Every call builds a rolling baseline. When behavior drifts, you get alerted.

## Features

- 📊 **Automatic Baselines** - Rolling p50/p95/p99 latency, token distributions, pass rates
- ✅ **Schema Validation** - Pydantic models validate every response
- 🔍 **Hallucination Proxies** - JSON failures, enum violations, empty outputs
- 🔗 **Change Tracking** - Hash prompts, tools, and system messages
- ⚡ **One Line Integration** - Context manager captures everything
- 🛡️ **Fail-Safe** - SDK errors never break your LLM calls
- 💰 **Cost Tracking** - Automatic cost estimation for GPT-4, Claude, etc.

## Usage Patterns

### Basic Tracking

```python
from deadpipe import track
from openai import OpenAI

client = OpenAI()

with track(prompt_id="my_agent") as t:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    t.record(response)
```

### With Schema Validation (Pydantic)

```python
from deadpipe import track
from pydantic import BaseModel
from typing import Literal

class OrderResponse(BaseModel):
    order_id: str
    amount: float
    status: Literal["pending", "complete", "cancelled"]

with track(prompt_id="order_agent", schema=OrderResponse) as t:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Get order 12345"}],
        response_format={"type": "json_object"}
    )
    result = t.record(response)  # Returns validated OrderResponse or None
    
    if result:
        print(f"Order {result.order_id}: {result.status}")
    else:
        print("Schema validation failed - check Deadpipe for details")
```

### With Enum and Numeric Bounds

```python
with track(
    prompt_id="pricing_agent",
    enum_fields={
        "currency": ["USD", "EUR", "GBP"],
        "tier": ["free", "pro", "enterprise"]
    },
    numeric_bounds={
        "price": (0, 10000),
        "quantity": (1, 100)
    }
) as t:
    response = client.chat.completions.create(...)
    t.record(response)
    # Automatically flags enum_out_of_range and numeric_out_of_bounds
```

### With Change Context

Know exactly what changed when behavior drifts:

```python
system_prompt = "You are a helpful assistant."
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input}
]
tools = [{"type": "function", "function": {...}}]

with track(
    prompt_id="tool_agent",
    messages=messages,           # → prompt_hash
    tools=tools,                 # → tool_schema_hash
    system_prompt=system_prompt  # → system_prompt_hash
) as t:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools
    )
    t.record(response)
```

### Streaming Support

```python
with track(prompt_id="streaming_agent") as t:
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Write a story"}],
        stream=True
    )
    
    chunks = []
    for chunk in stream:
        if chunk.choices[0].delta.content:
            t.mark_first_token()  # Call once when first content arrives
            chunks.append(chunk.choices[0].delta.content)
            print(chunk.choices[0].delta.content, end="")
    
    # Record with the stream object - we'll use the timing
    t.record(stream)
```

### Anthropic Support

```python
from deadpipe import track
import anthropic

client = anthropic.Anthropic()

with track(prompt_id="claude_agent", provider="anthropic") as t:
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello, Claude!"}]
    )
    t.record(response)
```

### Auto-Wrapping (Zero Changes)

Wrap the client once, all calls are tracked:

```python
from deadpipe import wrap_openai
from openai import OpenAI

client = wrap_openai(OpenAI(), prompt_id="my_app")

# Every call is now automatically tracked
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Retry Tracking

```python
with track(prompt_id="retrying_agent") as t:
    for attempt in range(3):
        try:
            t.mark_retry()  # Call before each retry
            response = client.chat.completions.create(...)
            t.record(response)
            break
        except openai.RateLimitError:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
```

## What We Capture

Every `t.record(response)` captures:

| Category | Fields |
|----------|--------|
| **Identity** | prompt_id, model, provider, app_id, environment, version |
| **Timing** | total_latency, first_token_time, request_start, end_time |
| **Volume** | input_tokens, output_tokens, total_tokens, estimated_cost_usd |
| **Reliability** | http_status, timeout, retry_count, provider_error_code |
| **Integrity** | json_parse_success, schema_validation_pass, empty_output, truncated |
| **Behavior** | output_hash, refusal_flag, tool_call_flag, tool_calls_count |
| **Safety** | enum_out_of_range, numeric_out_of_bounds |
| **Change** | prompt_hash, tool_schema_hash, system_prompt_hash |

## Automatic Baselines

After ~10 calls per prompt_id, we establish:

- **Latency**: mean, p50, p95, p99
- **Tokens**: input/output mean and stddev
- **Rates**: success, schema_pass, empty_output, refusal, error
- **Cost**: average cost per call

## Automatic Anomaly Detection

Anomalies fire when:

| Condition | Type |
|-----------|------|
| latency > p95 × 1.5 | `latency_spike` |
| tokens > mean + 3σ | `token_anomaly` |
| schema_pass < 99% | `schema_violation_spike` |
| empty_output > 5% | `empty_output_spike` |
| refusal > 10% | `refusal_spike` |

## Configuration

### Environment Variables

```bash
export DEADPIPE_API_KEY="dp_your_api_key"
export DEADPIPE_APP_ID="my-app"
export DEADPIPE_ENVIRONMENT="production"
export DEADPIPE_VERSION="v1.2.3"  # or GIT_COMMIT
```

### Constructor Options

```python
with track(
    prompt_id="my_agent",
    api_key="dp_xxx",                    # Or use DEADPIPE_API_KEY env var
    base_url="https://www.deadpipe.com/api/v1",
    app_id="my-app",
    environment="production",
    version="v1.2.3",
    provider="openai",                   # or "anthropic"
    schema=MyPydanticModel,              # Optional Pydantic model
    enum_fields={"status": ["a", "b"]},  # Optional enum validation
    numeric_bounds={"amount": (0, 100)}, # Optional range validation
    messages=messages,                   # For prompt_hash
    tools=tools,                         # For tool_schema_hash
    system_prompt=system_prompt,         # For system_prompt_hash
) as t:
    ...
```

## Cost Estimation

Built-in cost estimation for:

| Provider | Models |
|----------|--------|
| OpenAI | gpt-4, gpt-4-turbo, gpt-4o, gpt-4o-mini, gpt-3.5-turbo, o1-preview, o1-mini |
| Anthropic | claude-3-opus, claude-3-sonnet, claude-3-haiku, claude-3.5-sonnet |

## Fail-Safe Design

The SDK is designed to never break your application:

- All HTTP errors are caught and silently ignored
- Timeouts don't block your LLM calls
- If Deadpipe is down, your code continues normally
- No exceptions bubble up from `t.record()`

```python
# This will NEVER throw due to Deadpipe
with track(prompt_id="my_agent") as t:
    response = client.chat.completions.create(...)
    t.record(response)  # If Deadpipe is unreachable, this silently succeeds
```

## API

### `track()` Context Manager

```python
with track(prompt_id: str, **options) as tracker:
    response = client.chat.completions.create(...)
    result = tracker.record(response)
```

### `tracker.record(response)`

Records the LLM response and returns:
- If `schema` provided and valid: parsed Pydantic object
- If `schema` provided and invalid: `None`
- Otherwise: the original response

### `tracker.mark_first_token()`

Call when the first token arrives during streaming. Captures time-to-first-token (TTFT).

### `tracker.mark_retry()`

Call before each retry attempt. Increments retry_count.

### `wrap_openai(client, prompt_id, **options)`

Returns a wrapped OpenAI client that auto-tracks all completions.

## Links

- [Documentation](https://www.deadpipe.com/docs)
- [Dashboard](https://www.deadpipe.com/dashboard)
- [GitHub](https://github.com/deadpipe/deadpipe)

## License

MIT
