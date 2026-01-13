# Deadpipe Python SDK

**LLM observability that answers one question: "Is this prompt still behaving safely?"**

**Supports:** OpenAI, Anthropic, Google AI (Gemini), Mistral, Cohere

[![PyPI](https://img.shields.io/pypi/v/deadpipe)](https://pypi.org/project/deadpipe/)
[![Python](https://img.shields.io/pypi/pyversions/deadpipe)](https://pypi.org/project/deadpipe/)

## Installation

```bash
pip install deadpipe
```

## Quick Start

### Universal Wrapper (Recommended)

The `wrap()` function auto-detects your provider and wraps appropriately:

```python
from deadpipe import wrap
from openai import OpenAI
from anthropic import Anthropic

# Wrap once with optional app context
openai = wrap(OpenAI(), app="my_app")
anthropic = wrap(Anthropic(), app="my_app")

# Pass prompt_id per call - identifies which prompt/agent this is
response = openai.chat.completions.create(
    prompt_id="checkout_agent",  # Required for tracking
    model="gpt-4",
    messages=[{"role": "user", "content": "Process refund for order 1938"}]
)

# Use different prompt_ids for different prompts
response = anthropic.messages.create(
    prompt_id="support_agent",
    model="claude-3-opus",
    messages=[{"role": "user", "content": "Help me with my order"}]
)
```

That's it. Every call builds a rolling baseline. When behavior drifts, you get alerted.

### Provider-Specific Wrappers

For explicit control, use provider-specific wrappers:

```python
from deadpipe import wrap_openai, wrap_anthropic, wrap_google_ai, wrap_mistral, wrap_cohere

openai = wrap_openai(OpenAI(), app="my_app")
anthropic = wrap_anthropic(Anthropic(), app="my_app")
```

### Manual Tracking

For streaming, custom logic, or unsupported clients:

```python
from deadpipe import track
from openai import OpenAI

client = OpenAI()
params = {
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Process refund for order 1938"}]
}

with track(prompt_id="checkout_agent") as t:
    response = client.chat.completions.create(**params)
    t.record(response, input=params)  # Pass params to capture input
```

## Provider Examples

### OpenAI

```python
from deadpipe import wrap
from openai import OpenAI

client = wrap(OpenAI(), app="my_app")

response = client.chat.completions.create(
    prompt_id="openai_agent",
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Anthropic

```python
from deadpipe import wrap
from anthropic import Anthropic

client = wrap(Anthropic(), app="my_app")

response = client.messages.create(
    prompt_id="claude_agent",
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude!"}]
)
```

### Google AI (Gemini)

```python
from deadpipe import wrap_google_ai
import google.generativeai as genai

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-pro")

# Wrap the model directly
tracked_model = wrap_google_ai(model, app="my_app")

response = tracked_model.generate_content("Hello, Gemini!", prompt_id="gemini_agent")
```

### Mistral

```python
from deadpipe import wrap
from mistralai import Mistral

client = wrap(Mistral(api_key=os.environ["MISTRAL_API_KEY"]), app="my_app")

response = client.chat.complete(
    prompt_id="mistral_agent",
    model="mistral-large-latest",
    messages=[{"role": "user", "content": "Hello, Mistral!"}]
)
```

### Cohere

```python
from deadpipe import wrap
import cohere

client = wrap(cohere.Client(os.environ["COHERE_API_KEY"]), app="my_app")

response = client.chat(
    prompt_id="cohere_agent",
    model="command-r-plus",
    message="Hello, Cohere!"
)
```

## Features

- 📊 **Automatic Baselines** - Rolling p50/p95/p99 latency, token distributions, pass rates
- ✅ **Schema Validation** - Pydantic models validate every response
- 🔍 **Hallucination Proxies** - JSON failures, enum violations, empty outputs
- 🔗 **Change Tracking** - Hash prompts, tools, and system messages
- ⚡ **One Line Integration** - Wrapper captures everything
- 🛡️ **Fail-Safe** - SDK errors never break your LLM calls
- 💰 **Cost Tracking** - Automatic cost estimation for all providers

## What We Capture

Every prompt execution captures:

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

## Advanced Usage

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

### Schema Validation with Universal Wrapper

Each prompt can have its own schema when using the universal wrapper:

```python
from deadpipe import wrap
from pydantic import BaseModel, Field
from typing import Literal
from openai import OpenAI

class OrderResponse(BaseModel):
    product_id: str
    confidence: float = Field(ge=0, le=1)
    category: Literal["electronics", "clothing", "food"]

class RefundResponse(BaseModel):
    refund_id: str
    amount: float
    status: Literal["pending", "approved", "rejected"]

# Wrap once
client = wrap(OpenAI(), app="my_ecommerce")

# Different schemas for different prompts
order = client.chat.completions.create(
    prompt_id="recommender",
    schema=OrderResponse,  # Auto-validates, tracks pass rates
    model="gpt-4",
    messages=[{"role": "user", "content": "Recommend a product"}]
)

refund = client.chat.completions.create(
    prompt_id="refund_agent",
    schema=RefundResponse,  # Different schema for this prompt
    model="gpt-4",
    messages=[{"role": "user", "content": "Process refund for order 123"}]
)
```

### With Enum and Numeric Bounds

```python
# Using track() context manager
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

# Or with universal wrapper (per-call)
client = wrap(OpenAI(), app="my_app")
response = client.chat.completions.create(
    prompt_id="pricing_agent",
    enum_fields={"currency": ["USD", "EUR", "GBP"]},
    numeric_bounds={"price": {"min": 0, "max": 10000}},
    model="gpt-4",
    messages=[...]
)
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
    
    t.record(stream)
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

### Decorator

```python
from deadpipe import track_decorator
from openai import OpenAI

@track_decorator(prompt_id="checkout_agent")
def process_refund():
    client = OpenAI()
    return client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Process refund for order 1938"}]
    )
```

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
client = wrap(
    OpenAI(),
    app="my-app",                        # Optional app identifier
    api_key="dp_xxx",                    # Or use DEADPIPE_API_KEY env var
    base_url="https://www.deadpipe.com/api/v1",
    environment="production",
    version="v1.2.3",
)

# Then pass prompt_id per call (with optional schema per call)
response = client.chat.completions.create(
    prompt_id="checkout_agent",
    schema=CheckoutResponse,  # Optional: per-call schema validation
    model="gpt-4",
    messages=[...]
)
```

## Supported Models & Pricing

| Provider | Models |
|----------|--------|
| **OpenAI** | gpt-4, gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo, o1, o1-mini, o1-pro |
| **Anthropic** | claude-3-opus, claude-3-sonnet, claude-3-haiku, claude-3.5-sonnet, claude-sonnet-4, claude-opus-4 |
| **Google AI** | gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash, gemini-2.0-pro |
| **Mistral** | mistral-large, mistral-medium, mistral-small, mistral-nemo, codestral, pixtral |
| **Cohere** | command-r-plus, command-r, command, command-light |

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

## Fail-Safe Design

The SDK is designed to never break your application:

- All HTTP errors are caught and silently ignored
- Timeouts don't block your LLM calls
- If Deadpipe is down, your code continues normally
- No exceptions bubble up from `t.record()`

```python
# This will NEVER throw due to Deadpipe
client = wrap(OpenAI(), app="my_app")
response = client.chat.completions.create(prompt_id="my_agent", ...)  # Always works
```

## API Reference

### `wrap(client, app=None, **options)`

Universal wrapper that auto-detects provider.

- `client`: Any supported LLM client
- `app`: Optional app identifier (can also use DEADPIPE_APP_ID env var)

Returns: Wrapped client with identical API. Each call must include `prompt_id`.

### Provider-Specific Wrappers

- `wrap_openai(client, app=None, **options)` - OpenAI client
- `wrap_anthropic(client, app=None, **options)` - Anthropic client
- `wrap_google_ai(model, app=None, **options)` - Google AI GenerativeModel
- `wrap_mistral(client, app=None, **options)` - Mistral client
- `wrap_cohere(client, app=None, **options)` - Cohere client

All wrappers accept optional `app` and require `prompt_id` per call.

### `track()` Context Manager

```python
with track(prompt_id: str, **options) as tracker:
    response = client.chat.completions.create(...)
    result = tracker.record(response)
```

### `tracker.record(response, parsed_output=None, input=None)`

Records the LLM response and returns:
- If `schema` provided and valid: parsed Pydantic object
- If `schema` provided and invalid: `None`
- Otherwise: the original response

### Utility Functions

- `estimate_cost(model, input_tokens, output_tokens)` - Estimate USD cost
- `detect_refusal(text)` - Detect if response is a refusal
- `detect_provider(response)` - Detect provider from response
- `detect_client_provider(client)` - Detect provider from client

## Links

- [Documentation](https://www.deadpipe.com/docs)
- [Dashboard](https://www.deadpipe.com/dashboard)
- [GitHub](https://github.com/deadpipe/deadpipe)

## License

MIT
