"""
Deadpipe - LLM observability that answers one question:
"Is this prompt still behaving safely?"

Supports: OpenAI, Anthropic, Google AI (Gemini), Mistral, Cohere

Recommended: Universal wrapper (auto-detects provider)
    from deadpipe import wrap
    from openai import OpenAI
    from anthropic import Anthropic

    # Wrap once with app context
    openai = wrap(OpenAI(), app="my_app")
    anthropic = wrap(Anthropic(), app="my_app")

    # Pass prompt_id per call
    openai.chat.completions.create(prompt_id="checkout_agent", model="gpt-4", messages=[...])
    anthropic.messages.create(prompt_id="support_agent", model="claude-3-opus", messages=[...])

Provider-specific wrappers:
    from deadpipe import wrap_openai, wrap_anthropic

    openai = wrap_openai(OpenAI(), app="my_app")
    anthropic = wrap_anthropic(Anthropic(), app="my_app")

Advanced: Manual tracking (for streaming, custom logic, etc.)
    from deadpipe import track
    from openai import OpenAI

    client = OpenAI()
    params = {"model": "gpt-4", "messages": [...]}

    with track(prompt_id="checkout_agent") as t:
        response = client.chat.completions.create(**params)
        t.record(response, input=params)
"""

import os
import time
import json
import hashlib
from contextlib import contextmanager
from typing import Optional, Literal, Any, TypeVar, Type, Dict, List, Union
from dataclasses import dataclass, asdict
import urllib.request
import urllib.error

__version__ = "4.0.0"

T = TypeVar("T")
StatusType = Literal["success", "error", "timeout", "empty", "schema_violation", "refusal"]
ProviderType = Literal["openai", "anthropic", "google", "mistral", "cohere", "unknown"]

# ==================== COST ESTIMATION ====================

MODEL_COSTS: dict[str, dict[str, float]] = {
    # OpenAI
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4.1": {"input": 0.002, "output": 0.008},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "gpt-5": {"input": 0.00175, "output": 0.014},
    "gpt-5-mini": {"input": 0.00025, "output": 0.002},
    "gpt-5.2-pro": {"input": 0.021, "output": 0.168},
    "o1": {"input": 0.015, "output": 0.06},
    "o1-mini": {"input": 0.003, "output": 0.012},
    "o1-pro": {"input": 0.15, "output": 0.6},

    # Anthropic
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3.5-haiku": {"input": 0.0008, "output": 0.004},
    "claude-opus-4": {"input": 0.015, "output": 0.075},
    "claude-sonnet-4": {"input": 0.003, "output": 0.015},
    "claude-haiku-4": {"input": 0.00025, "output": 0.00125},

    # Google AI / Gemini
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
    "gemini-2.0-pro": {"input": 0.00125, "output": 0.005},
    "gemini-pro": {"input": 0.0005, "output": 0.0015},

    # Mistral
    "mistral-large": {"input": 0.004, "output": 0.012},
    "mistral-medium": {"input": 0.0027, "output": 0.0081},
    "mistral-small": {"input": 0.001, "output": 0.003},
    "mistral-nemo": {"input": 0.0003, "output": 0.0003},
    "codestral": {"input": 0.001, "output": 0.003},
    "pixtral": {"input": 0.002, "output": 0.006},
    "ministral": {"input": 0.0001, "output": 0.0001},

    # Cohere
    "command-r-plus": {"input": 0.003, "output": 0.015},
    "command-r": {"input": 0.0005, "output": 0.0015},
    "command": {"input": 0.001, "output": 0.002},
    "command-light": {"input": 0.0003, "output": 0.0006},
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    """Estimate cost in USD for a completion."""
    model_lower = model.lower()
    for known_model, costs in MODEL_COSTS.items():
        if known_model in model_lower:
            input_cost = (input_tokens / 1000) * costs["input"]
            output_cost = (output_tokens / 1000) * costs["output"]
            return round(input_cost + output_cost, 6)
    return None


# ==================== HASHING ====================

def hash_content(content: str) -> str:
    """SHA-256 hash of content, truncated to 16 chars."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def hash_messages(messages: List[Dict[str, Any]]) -> str:
    """Hash message list for change detection."""
    serialized = json.dumps(messages, sort_keys=True, default=str)
    return hash_content(serialized)


def hash_tools(tools: Optional[List[Dict[str, Any]]]) -> Optional[str]:
    """Hash tool schemas for change detection."""
    if not tools:
        return None
    serialized = json.dumps(tools, sort_keys=True, default=str)
    return hash_content(serialized)


# ==================== TELEMETRY EVENT ====================

@dataclass
class PromptTelemetry:
    """Complete telemetry for a single prompt execution."""

    # Identity
    prompt_id: str
    model: str = ""
    provider: str = "openai"
    app_id: Optional[str] = None
    environment: Optional[str] = None
    version: Optional[str] = None

    # Timing
    request_start: str = ""
    first_token_time: Optional[int] = None
    end_time: str = ""
    total_latency: int = 0

    # Volume
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    estimated_cost_usd: Optional[float] = None

    # Reliability
    http_status: Optional[int] = None
    timeout: bool = False
    retry_count: int = 0
    provider_error_code: Optional[str] = None
    error_message: Optional[str] = None

    # Output integrity
    output_length: Optional[int] = None
    empty_output: bool = False
    truncated: bool = False
    json_parse_success: Optional[bool] = None
    schema_validation_pass: Optional[bool] = None
    missing_required_fields: Optional[str] = None

    # Behavioral fingerprint
    output_hash: Optional[str] = None
    output_embedding: Optional[str] = None
    top_logprob_mean: Optional[float] = None
    refusal_flag: bool = False
    tool_call_flag: bool = False
    tool_calls_count: int = 0

    # Safety proxies
    enum_out_of_range: bool = False
    numeric_out_of_bounds: bool = False
    hallucination_flags: Optional[str] = None

    # Change context
    prompt_hash: Optional[str] = None
    tool_schema_hash: Optional[str] = None
    system_prompt_hash: Optional[str] = None

    # Previews (for debugging/inspection in dashboard)
    input_preview: Optional[str] = None
    output_preview: Optional[str] = None
    system_prompt_preview: Optional[str] = None

    # Status
    status: StatusType = "success"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for API submission, removing None and empty values."""
        result = {}
        for k, v in asdict(self).items():
            if v is None:
                continue
            if isinstance(v, str) and not v:
                continue
            if isinstance(v, (list, dict)) and not v:
                continue
            if isinstance(v, bool) and not v:
                continue
            result[k] = v
        return result


# ==================== REFUSAL DETECTION ====================

REFUSAL_PATTERNS = [
    "i can't help with",
    "i cannot help with",
    "i'm not able to",
    "i am not able to",
    "i won't be able to",
    "i'm unable to",
    "i cannot provide",
    "i can't provide",
    "i must decline",
    "i cannot assist with",
    "i can't assist with",
    "as an ai",
    "as a language model",
    "i don't have the ability",
    "i cannot comply",
    "i'm designed to",
    "my purpose is to",
    "violates my guidelines",
    "against my guidelines",
    "ethical guidelines",
    "i apologize, but i cannot",
    "i'm sorry, but i can't",
]


def detect_refusal(text: str) -> bool:
    """Detect if response is a refusal/decline."""
    text_lower = text.lower()
    return any(pattern in text_lower for pattern in REFUSAL_PATTERNS)


# ==================== SCHEMA VALIDATION ====================

def validate_with_pydantic(data: Any, schema: Type[T]) -> tuple[bool, Optional[T], Optional[List[str]]]:
    """
    Validate data against a Pydantic model.
    Returns (is_valid, parsed_object, missing_fields)
    """
    try:
        from pydantic import ValidationError
        parsed = schema.model_validate(data)
        return True, parsed, None
    except ValidationError as e:
        missing = []
        for error in e.errors():
            if error["type"] == "missing":
                missing.append(".".join(str(loc) for loc in error["loc"]))
        return False, None, missing if missing else None
    except Exception:
        return False, None, None


def validate_enum_bounds(data: Any, enum_fields: Optional[Dict[str, List[Any]]] = None) -> bool:
    """Check if enum fields contain valid values."""
    if not enum_fields or not isinstance(data, dict):
        return True

    for field_name, valid_values in enum_fields.items():
        if field_name in data and data[field_name] not in valid_values:
            return False
    return True


def validate_numeric_bounds(
    data: Any,
    numeric_bounds: Optional[Dict[str, tuple[Optional[float], Optional[float]]]] = None
) -> bool:
    """Check if numeric fields are within expected bounds."""
    if not numeric_bounds or not isinstance(data, dict):
        return True

    for field_name, (min_val, max_val) in numeric_bounds.items():
        if field_name in data:
            value = data[field_name]
            if isinstance(value, (int, float)):
                if min_val is not None and value < min_val:
                    return False
                if max_val is not None and value > max_val:
                    return False
    return True


# ==================== PROVIDER DETECTION ====================

def detect_provider(response: Any) -> ProviderType:
    """Auto-detect provider from response object."""
    if not response:
        return "unknown"

    # Anthropic: content array + stop_reason
    if hasattr(response, "content") and isinstance(response.content, list):
        if hasattr(response, "stop_reason"):
            return "anthropic"

    # Google AI: candidates array
    if hasattr(response, "candidates") or hasattr(response, "prompt_feedback"):
        return "google"

    # Cohere: text field + generation_id or generations
    if (hasattr(response, "text") and hasattr(response, "generation_id")) or hasattr(response, "generations"):
        return "cohere"

    # OpenAI/Mistral: choices array
    if hasattr(response, "choices") or hasattr(response, "output"):
        model = str(getattr(response, "model", "")).lower()
        if "mistral" in model or "codestral" in model or "pixtral" in model or "ministral" in model:
            return "mistral"
        return "openai"

    # Check model name patterns
    if hasattr(response, "model"):
        model_lower = str(response.model).lower()
        if "claude" in model_lower:
            return "anthropic"
        if "gemini" in model_lower:
            return "google"
        if "mistral" in model_lower or "codestral" in model_lower:
            return "mistral"
        if "command" in model_lower:
            return "cohere"
        if "gpt" in model_lower or "o1" in model_lower:
            return "openai"

    return "unknown"


def detect_client_provider(client: Any) -> ProviderType:
    """Auto-detect provider from client object."""
    if not client:
        return "unknown"

    # OpenAI: has chat.completions or responses
    if hasattr(client, "chat") and hasattr(client.chat, "completions"):
        # Check if it's actually Mistral
        base_url = getattr(client, "base_url", "") or getattr(getattr(client, "_client", None), "base_url", "")
        if "mistral" in str(base_url).lower():
            return "mistral"
        return "openai"

    # Anthropic: has messages.create
    if hasattr(client, "messages") and hasattr(client.messages, "create"):
        return "anthropic"

    # Google AI: GenerativeModel or has generate_content
    client_type = type(client).__name__.lower()
    if "generativemodel" in client_type or hasattr(client, "generate_content"):
        return "google"

    # Mistral: has chat method with complete
    if hasattr(client, "chat") and hasattr(client.chat, "complete"):
        return "mistral"

    # Cohere: has chat or generate methods as callable
    if hasattr(client, "chat") and callable(client.chat):
        return "cohere"
    if hasattr(client, "generate") and callable(client.generate):
        return "cohere"

    return "unknown"


# ==================== RESPONSE PARSING ====================

def extract_openai_response(response: Any) -> Dict[str, Any]:
    """Extract relevant fields from OpenAI response object."""
    result = {
        "model": "",
        "content": "",
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "finish_reason": None,
        "tool_calls": [],
        "logprobs": None,
    }

    if hasattr(response, "model"):
        result["model"] = response.model

    # Chat completion
    if hasattr(response, "choices") and response.choices:
        choice = response.choices[0]
        if hasattr(choice, "message"):
            msg = choice.message
            result["content"] = getattr(msg, "content", "") or ""
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                result["tool_calls"] = [
                    {"name": tc.function.name, "arguments": tc.function.arguments}
                    for tc in msg.tool_calls
                ]
        if hasattr(choice, "finish_reason"):
            result["finish_reason"] = choice.finish_reason
        if hasattr(choice, "logprobs") and choice.logprobs:
            result["logprobs"] = choice.logprobs

    # New responses API
    if hasattr(response, "output"):
        result["content"] = response.output or ""

    # Usage
    if hasattr(response, "usage") and response.usage:
        usage = response.usage
        result["input_tokens"] = getattr(usage, "prompt_tokens", None)
        result["output_tokens"] = getattr(usage, "completion_tokens", None)
        result["total_tokens"] = getattr(usage, "total_tokens", None)

    return result


def extract_anthropic_response(response: Any) -> Dict[str, Any]:
    """Extract relevant fields from Anthropic response object."""
    result = {
        "model": "",
        "content": "",
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "finish_reason": None,
        "tool_calls": [],
    }

    if hasattr(response, "model"):
        result["model"] = response.model

    if hasattr(response, "content") and response.content:
        text_blocks = [block.text for block in response.content if hasattr(block, "text")]
        result["content"] = "".join(text_blocks)

        tool_blocks = [block for block in response.content if hasattr(block, "type") and block.type == "tool_use"]
        result["tool_calls"] = [
            {"name": block.name, "arguments": json.dumps(block.input)}
            for block in tool_blocks
        ]

    if hasattr(response, "stop_reason"):
        result["finish_reason"] = response.stop_reason

    if hasattr(response, "usage") and response.usage:
        result["input_tokens"] = getattr(response.usage, "input_tokens", None)
        result["output_tokens"] = getattr(response.usage, "output_tokens", None)
        if result["input_tokens"] and result["output_tokens"]:
            result["total_tokens"] = result["input_tokens"] + result["output_tokens"]

    return result


def extract_google_ai_response(response: Any) -> Dict[str, Any]:
    """Extract relevant fields from Google AI response object."""
    result = {
        "model": "",
        "content": "",
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "finish_reason": None,
        "tool_calls": [],
    }

    # Handle GenerateContentResponse
    if hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]

        if hasattr(candidate, "content") and candidate.content:
            parts = getattr(candidate.content, "parts", [])
            text_parts = [p.text for p in parts if hasattr(p, "text")]
            result["content"] = "".join(text_parts)

            # Function calls
            func_calls = [p.function_call for p in parts if hasattr(p, "function_call") and p.function_call]
            result["tool_calls"] = [
                {"name": fc.name, "arguments": json.dumps(dict(fc.args))}
                for fc in func_calls
            ]

        if hasattr(candidate, "finish_reason"):
            result["finish_reason"] = str(candidate.finish_reason)

    # Usage metadata
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        result["input_tokens"] = getattr(response.usage_metadata, "prompt_token_count", None)
        result["output_tokens"] = getattr(response.usage_metadata, "candidates_token_count", None)
        result["total_tokens"] = getattr(response.usage_metadata, "total_token_count", None)

    return result


def extract_mistral_response(response: Any) -> Dict[str, Any]:
    """Extract relevant fields from Mistral response object."""
    # Mistral uses OpenAI-compatible format
    result = extract_openai_response(response)

    # Handle Mistral SDK v1.x specific fields if needed
    if hasattr(response, "model"):
        result["model"] = response.model

    return result


def extract_cohere_response(response: Any) -> Dict[str, Any]:
    """Extract relevant fields from Cohere response object."""
    result = {
        "model": "",
        "content": "",
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "finish_reason": None,
        "tool_calls": [],
    }

    # Chat API response
    if hasattr(response, "text"):
        result["content"] = response.text or ""

    # Generate API response (legacy)
    if hasattr(response, "generations") and response.generations:
        result["content"] = response.generations[0].text or ""

    # Model
    if hasattr(response, "model"):
        result["model"] = response.model

    # Finish reason
    if hasattr(response, "finish_reason"):
        result["finish_reason"] = response.finish_reason

    # Tool calls
    if hasattr(response, "tool_calls") and response.tool_calls:
        result["tool_calls"] = [
            {"name": tc.name, "arguments": json.dumps(tc.parameters)}
            for tc in response.tool_calls
        ]

    # Token usage
    if hasattr(response, "meta") and response.meta:
        if hasattr(response.meta, "tokens"):
            result["input_tokens"] = getattr(response.meta.tokens, "input_tokens", None)
            result["output_tokens"] = getattr(response.meta.tokens, "output_tokens", None)
        if hasattr(response.meta, "billed_units"):
            result["input_tokens"] = getattr(response.meta.billed_units, "input_tokens", None)
            result["output_tokens"] = getattr(response.meta.billed_units, "output_tokens", None)

        if result["input_tokens"] and result["output_tokens"]:
            result["total_tokens"] = result["input_tokens"] + result["output_tokens"]

    return result


def extract_response(response: Any, provider: Optional[ProviderType] = None) -> Dict[str, Any]:
    """Extract response data based on detected or specified provider."""
    detected_provider = provider or detect_provider(response)

    if detected_provider == "anthropic":
        return extract_anthropic_response(response)
    elif detected_provider == "google":
        return extract_google_ai_response(response)
    elif detected_provider == "mistral":
        return extract_mistral_response(response)
    elif detected_provider == "cohere":
        return extract_cohere_response(response)
    else:
        return extract_openai_response(response)


def calculate_logprob_mean(logprobs: Any) -> Optional[float]:
    """Calculate mean log probability from OpenAI logprobs."""
    if not logprobs:
        return None

    try:
        if hasattr(logprobs, "content") and logprobs.content:
            probs = [token.logprob for token in logprobs.content if hasattr(token, "logprob")]
            if probs:
                return sum(probs) / len(probs)
    except Exception:
        pass
    return None


# ==================== TRACKER ====================

class PromptTracker:
    """
    Context manager for tracking a single prompt execution.
    Captures comprehensive telemetry to answer:
    "Is this prompt still behaving safely?"
    """

    def __init__(
        self,
        prompt_id: str,
        api_key: Optional[str] = None,
        base_url: str = "https://www.deadpipe.com/api/v1",
        timeout: int = 10,
        # Identity
        app_id: Optional[str] = None,
        environment: Optional[str] = None,
        version: Optional[str] = None,
        # Validation
        schema: Optional[Type] = None,
        enum_fields: Optional[Dict[str, List[Any]]] = None,
        numeric_bounds: Optional[Dict[str, tuple[Optional[float], Optional[float]]]] = None,
    ):
        self.prompt_id = prompt_id
        self.api_key = api_key or os.environ.get("DEADPIPE_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout

        # Identity
        self.app_id = app_id or os.environ.get("DEADPIPE_APP_ID")
        self.environment = environment or os.environ.get("DEADPIPE_ENVIRONMENT")
        self.version = version or os.environ.get("DEADPIPE_VERSION") or os.environ.get("GIT_COMMIT")

        # Validation schemas
        self.schema = schema
        self.enum_fields = enum_fields
        self.numeric_bounds = numeric_bounds

        # Context hashes
        self.prompt_hash: Optional[str] = None
        self.tool_schema_hash: Optional[str] = None
        self.system_prompt_hash: Optional[str] = None

        # Store messages and system prompt for preview generation
        self._messages: Optional[List[Dict[str, Any]]] = None
        self._system_prompt: Optional[str] = None

        # Timing
        self._start_time: Optional[float] = None
        self._first_token_time: Optional[float] = None
        self._end_time: Optional[float] = None

        # State
        self._telemetry: Optional[PromptTelemetry] = None
        self._recorded = False
        self._error: Optional[Exception] = None
        self._retry_count = 0

    def __enter__(self) -> "PromptTracker":
        self._start_time = time.time()
        self._telemetry = PromptTelemetry(
            prompt_id=self.prompt_id,
            app_id=self.app_id,
            environment=self.environment,
            version=self.version,
            request_start=time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(self._start_time)),
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = time.time()

        if self._telemetry:
            self._telemetry.end_time = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(self._end_time))
            self._telemetry.total_latency = int((self._end_time - (self._start_time or self._end_time)) * 1000)

        # Handle exceptions
        if exc_type is not None:
            if self._telemetry:
                self._telemetry.status = "error"
                self._telemetry.error_message = str(exc_val)

                if hasattr(exc_val, "status_code"):
                    self._telemetry.http_status = exc_val.status_code
                if hasattr(exc_val, "code"):
                    self._telemetry.provider_error_code = str(exc_val.code)

                if "timeout" in str(exc_val).lower():
                    self._telemetry.status = "timeout"
                    self._telemetry.timeout = True

            if not self._recorded:
                self._send()

        elif not self._recorded:
            self._send()

        return False

    def mark_first_token(self):
        """Call this when the first token is received (for streaming)."""
        if self._first_token_time is None and self._start_time:
            self._first_token_time = time.time()
            if self._telemetry:
                self._telemetry.first_token_time = int((self._first_token_time - self._start_time) * 1000)

    def mark_retry(self):
        """Call this before each retry attempt."""
        self._retry_count += 1
        if self._telemetry:
            self._telemetry.retry_count = self._retry_count

    def record(
        self,
        response: Any,
        *,
        parsed_output: Any = None,
        input: Any = None,
    ) -> Any:
        """
        Record the LLM response and extract telemetry.

        Args:
            response: The raw response from the LLM provider
            parsed_output: Optional pre-parsed output (if you already parsed JSON)
            input: The input parameters passed to the LLM call

        Returns:
            - If schema provided and validation passes: parsed/validated object
            - If schema provided and validation fails: None
            - Otherwise: the raw response
        """
        if not self._telemetry:
            return response

        self._end_time = time.time()
        self._telemetry.end_time = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(self._end_time))
        self._telemetry.total_latency = int((self._end_time - (self._start_time or self._end_time)) * 1000)

        # Auto-detect provider from response
        detected_provider = detect_provider(response)
        self._telemetry.provider = detected_provider if detected_provider != "unknown" else "openai"

        # Extract response data based on detected provider
        extracted = extract_response(response, detected_provider)

        # Extract input context from input params if provided
        if input:
            messages = input.get("messages", []) if isinstance(input, dict) else getattr(input, "messages", [])
            tools = input.get("tools") if isinstance(input, dict) else getattr(input, "tools", None)
            system_prompt = None

            # Handle Anthropic's system parameter (separate from messages)
            if isinstance(input, dict) and "system" in input:
                system_prompt = input["system"] if isinstance(input["system"], str) else json.dumps(input["system"])

            # Also check messages for system prompt (OpenAI style)
            if not system_prompt:
                for msg in messages:
                    role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
                    if role == "system":
                        system_prompt = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")
                        break

            if messages:
                self.prompt_hash = hash_messages(messages)
                self._messages = messages
            if tools:
                self.tool_schema_hash = hash_tools(tools)
            if system_prompt:
                self.system_prompt_hash = hash_content(system_prompt)
                self._system_prompt = system_prompt

        # Update context hashes
        if self.prompt_hash:
            self._telemetry.prompt_hash = self.prompt_hash
        if self.tool_schema_hash:
            self._telemetry.tool_schema_hash = self.tool_schema_hash
        if self.system_prompt_hash:
            self._telemetry.system_prompt_hash = self.system_prompt_hash

        # Fill telemetry
        self._telemetry.model = extracted["model"]
        self._telemetry.input_tokens = extracted["input_tokens"]
        self._telemetry.output_tokens = extracted["output_tokens"]
        self._telemetry.total_tokens = extracted["total_tokens"]
        self._telemetry.http_status = 200

        content = extracted["content"]
        self._telemetry.output_length = len(content) if content else 0
        self._telemetry.empty_output = not content or len(content.strip()) == 0
        self._telemetry.truncated = extracted.get("finish_reason") in ("length", "MAX_TOKENS")

        # Tool calls
        tool_calls = extracted.get("tool_calls", [])
        self._telemetry.tool_call_flag = len(tool_calls) > 0
        self._telemetry.tool_calls_count = len(tool_calls)

        # Output hash
        if content:
            self._telemetry.output_hash = hash_content(content)

        # Capture previews
        MAX_PREVIEW_LENGTH = 2000

        if content:
            self._telemetry.output_preview = (
                content[:MAX_PREVIEW_LENGTH] + "..."
                if len(content) > MAX_PREVIEW_LENGTH
                else content
            )

        if self._messages:
            user_messages = [m for m in self._messages if m.get("role") == "user"]
            if user_messages:
                last_user_msg = user_messages[-1].get("content", "")
                self._telemetry.input_preview = (
                    last_user_msg[:MAX_PREVIEW_LENGTH] + "..."
                    if len(last_user_msg) > MAX_PREVIEW_LENGTH
                    else last_user_msg
                )

        if self._system_prompt:
            self._telemetry.system_prompt_preview = (
                self._system_prompt[:MAX_PREVIEW_LENGTH] + "..."
                if len(self._system_prompt) > MAX_PREVIEW_LENGTH
                else self._system_prompt
            )

        # Logprob mean
        if extracted.get("logprobs"):
            self._telemetry.top_logprob_mean = calculate_logprob_mean(extracted["logprobs"])

        # Cost estimation
        if self._telemetry.input_tokens and self._telemetry.output_tokens:
            self._telemetry.estimated_cost_usd = estimate_cost(
                self._telemetry.model,
                self._telemetry.input_tokens,
                self._telemetry.output_tokens
            )

        # Refusal detection
        if content:
            self._telemetry.refusal_flag = detect_refusal(content)
            if self._telemetry.refusal_flag:
                self._telemetry.status = "refusal"

        # Determine status
        if self._telemetry.empty_output:
            self._telemetry.status = "empty"

        # JSON parsing attempt
        parsed_data = parsed_output
        if parsed_data is None and content:
            try:
                content_stripped = content.strip()
                if content_stripped.startswith("{") or content_stripped.startswith("["):
                    parsed_data = json.loads(content_stripped)
                    self._telemetry.json_parse_success = True
                elif "```json" in content_stripped:
                    start = content_stripped.find("```json") + 7
                    end = content_stripped.find("```", start)
                    if end > start:
                        parsed_data = json.loads(content_stripped[start:end].strip())
                        self._telemetry.json_parse_success = True
            except json.JSONDecodeError:
                self._telemetry.json_parse_success = False

        # Schema validation
        validated_result = None
        if self.schema and parsed_data is not None:
            is_valid, validated, missing = validate_with_pydantic(parsed_data, self.schema)
            self._telemetry.schema_validation_pass = is_valid
            if not is_valid:
                self._telemetry.status = "schema_violation"
                if missing:
                    self._telemetry.missing_required_fields = json.dumps(missing)
            validated_result = validated

        # Enum bounds check
        if self.enum_fields and parsed_data is not None:
            if not validate_enum_bounds(parsed_data, self.enum_fields):
                self._telemetry.enum_out_of_range = True
                self._telemetry.status = "schema_violation"

        # Numeric bounds check
        if self.numeric_bounds and parsed_data is not None:
            if not validate_numeric_bounds(parsed_data, self.numeric_bounds):
                self._telemetry.numeric_out_of_bounds = True
                self._telemetry.status = "schema_violation"

        # Send telemetry
        self._send()
        self._recorded = True

        # Return appropriate result
        if self.schema:
            return validated_result
        return response

    def _send(self):
        """Send telemetry to Deadpipe API."""
        if not self.api_key or not self._telemetry:
            if os.environ.get("DEADPIPE_DEBUG") == "1":
                import sys
                print("[Deadpipe] DEADPIPE_API_KEY not set. Telemetry will not be sent.", file=sys.stderr)
            return

        try:
            payload = self._telemetry.to_dict()
            data = json.dumps(payload).encode("utf-8")

            req = urllib.request.Request(
                f"{self.base_url}/prompt",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                },
                method="POST",
            )

            import threading

            def send_async():
                try:
                    with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                        pass
                except Exception:
                    pass

            thread = threading.Thread(target=send_async, daemon=True)
            thread.start()

        except Exception:
            pass


# ==================== CONVENIENCE FUNCTIONS ====================

@contextmanager
def track(
    prompt_id: str,
    *,
    api_key: Optional[str] = None,
    base_url: str = "https://www.deadpipe.com/api/v1",
    app_id: Optional[str] = None,
    environment: Optional[str] = None,
    version: Optional[str] = None,
    schema: Optional[Type] = None,
    enum_fields: Optional[Dict[str, List[Any]]] = None,
    numeric_bounds: Optional[Dict[str, tuple[Optional[float], Optional[float]]]] = None,
):
    """
    Context manager for tracking a prompt execution.

    Example:
        with track(prompt_id="checkout_agent") as t:
            response = client.chat.completions.create(...)
            t.record(response)

    With schema validation:
        with track(prompt_id="checkout_agent", schema=MySchema) as t:
            response = client.chat.completions.create(...)
            result = t.record(response)  # Returns validated MySchema or None
    """
    tracker = PromptTracker(
        prompt_id=prompt_id,
        api_key=api_key,
        base_url=base_url,
        app_id=app_id,
        environment=environment,
        version=version,
        schema=schema,
        enum_fields=enum_fields,
        numeric_bounds=numeric_bounds,
    )
    with tracker:
        yield tracker


# ==================== CLIENT WRAPPERS ====================

class TrackedOpenAI:
    """Wrapper around OpenAI client that auto-tracks all completions."""

    def __init__(
        self,
        client: Any,
        app: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://www.deadpipe.com/api/v1",
        environment: Optional[str] = None,
        version: Optional[str] = None,
        schema: Optional[Type] = None,
    ):
        self._client = client
        self._api_key = api_key
        self._base_url = base_url
        self._app_id = app
        self._environment = environment
        self._version = version
        self._schema = schema

        if hasattr(client, "chat") and hasattr(client.chat, "completions"):
            self.chat = _TrackedChat(
                client.chat,
                api_key=api_key,
                base_url=base_url,
                app_id=app,
                environment=environment,
                version=version,
                schema=schema,
            )

        if hasattr(client, "responses"):
            self.responses = _TrackedResponses(
                client.responses,
                api_key=api_key,
                base_url=base_url,
                app_id=app,
                environment=environment,
                version=version,
                schema=schema,
            )

    def __getattr__(self, name):
        return getattr(self._client, name)


class _TrackedChat:
    def __init__(self, chat, **kwargs):
        self._chat = chat
        self._kwargs = kwargs
        self.completions = _TrackedCompletions(chat.completions, **kwargs)


class _TrackedCompletions:
    def __init__(self, completions, **kwargs):
        self._completions = completions
        self._kwargs = kwargs

    def create(self, **api_kwargs):
        # Extract deadpipe-specific params (prompt_id required, others optional per-call)
        prompt_id = api_kwargs.pop("prompt_id", None)
        schema = api_kwargs.pop("schema", None)
        enum_fields = api_kwargs.pop("enum_fields", None)
        numeric_bounds = api_kwargs.pop("numeric_bounds", None)
        
        if not prompt_id:
            import sys
            print("[Deadpipe] prompt_id is required for tracking. Call will not be tracked.", file=sys.stderr)
            return self._completions.create(**api_kwargs)
        
        # Merge per-call options with defaults (per-call wins)
        track_kwargs = {**self._kwargs}
        if schema is not None:
            track_kwargs["schema"] = schema
        if enum_fields is not None:
            track_kwargs["enum_fields"] = enum_fields
        if numeric_bounds is not None:
            track_kwargs["numeric_bounds"] = numeric_bounds
        
        with track(prompt_id=prompt_id, **track_kwargs) as t:
            response = self._completions.create(**api_kwargs)
            t.record(response, input=api_kwargs)
            return response


class _TrackedResponses:
    def __init__(self, responses, **kwargs):
        self._responses = responses
        self._kwargs = kwargs

    def create(self, **api_kwargs):
        # Extract deadpipe-specific params (prompt_id required, others optional per-call)
        prompt_id = api_kwargs.pop("prompt_id", None)
        schema = api_kwargs.pop("schema", None)
        enum_fields = api_kwargs.pop("enum_fields", None)
        numeric_bounds = api_kwargs.pop("numeric_bounds", None)

        if not prompt_id:
            import sys
            print("[Deadpipe] prompt_id is required for tracking. Call will not be tracked.", file=sys.stderr)
            return self._responses.create(**api_kwargs)

        # Merge per-call options with defaults (per-call wins)
        track_kwargs = {**self._kwargs}
        if schema is not None:
            track_kwargs["schema"] = schema
        if enum_fields is not None:
            track_kwargs["enum_fields"] = enum_fields
        if numeric_bounds is not None:
            track_kwargs["numeric_bounds"] = numeric_bounds

        with track(prompt_id=prompt_id, **track_kwargs) as t:
            response = self._responses.create(**api_kwargs)
            t.record(response, input=api_kwargs)
            return response


def wrap_openai(
    client: Any,
    app: Optional[str] = None,
    *,
    api_key: Optional[str] = None,
    base_url: str = "https://www.deadpipe.com/api/v1",
    environment: Optional[str] = None,
    version: Optional[str] = None,
    schema: Optional[Type] = None,
) -> TrackedOpenAI:
    """Wrap an OpenAI client to automatically track all completions.
    
    Args:
        client: The OpenAI client instance
        app: Optional app identifier (can also use DEADPIPE_APP_ID env var)
        
    Each call must include prompt_id:
        client.chat.completions.create(prompt_id="checkout", model="gpt-4", messages=[...])
    """
    return TrackedOpenAI(
        client,
        app=app,
        api_key=api_key,
        base_url=base_url,
        environment=environment,
        version=version,
        schema=schema,
    )


# ==================== ANTHROPIC WRAPPER ====================

class TrackedAnthropic:
    """Wrapper around Anthropic client that auto-tracks all messages."""

    def __init__(
        self,
        client: Any,
        app: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://www.deadpipe.com/api/v1",
        environment: Optional[str] = None,
        version: Optional[str] = None,
        schema: Optional[Type] = None,
    ):
        self._client = client
        self._kwargs = {
            "api_key": api_key,
            "base_url": base_url,
            "app_id": app,
            "environment": environment,
            "version": version,
            "schema": schema,
        }

        if hasattr(client, "messages"):
            self.messages = _TrackedAnthropicMessages(client.messages, **self._kwargs)

    def __getattr__(self, name):
        return getattr(self._client, name)


class _TrackedAnthropicMessages:
    def __init__(self, messages, **kwargs):
        self._messages = messages
        self._kwargs = kwargs

    def create(self, **api_kwargs):
        # Extract deadpipe-specific params (prompt_id required, others optional per-call)
        prompt_id = api_kwargs.pop("prompt_id", None)
        schema = api_kwargs.pop("schema", None)
        enum_fields = api_kwargs.pop("enum_fields", None)
        numeric_bounds = api_kwargs.pop("numeric_bounds", None)
        
        if not prompt_id:
            import sys
            print("[Deadpipe] prompt_id is required for tracking. Call will not be tracked.", file=sys.stderr)
            return self._messages.create(**api_kwargs)
        
        # Merge per-call options with defaults (per-call wins)
        track_kwargs = {**self._kwargs}
        if schema is not None:
            track_kwargs["schema"] = schema
        if enum_fields is not None:
            track_kwargs["enum_fields"] = enum_fields
        if numeric_bounds is not None:
            track_kwargs["numeric_bounds"] = numeric_bounds
        
        with track(prompt_id=prompt_id, **track_kwargs) as t:
            response = self._messages.create(**api_kwargs)
            t.record(response, input=api_kwargs)
            return response


def wrap_anthropic(
    client: Any,
    app: Optional[str] = None,
    *,
    api_key: Optional[str] = None,
    base_url: str = "https://www.deadpipe.com/api/v1",
    environment: Optional[str] = None,
    version: Optional[str] = None,
    schema: Optional[Type] = None,
) -> TrackedAnthropic:
    """Wrap an Anthropic client to automatically track all messages.
    
    Args:
        client: The Anthropic client instance
        app: Optional app identifier (can also use DEADPIPE_APP_ID env var)
        
    Each call must include prompt_id:
        client.messages.create(prompt_id="support", model="claude-3-opus", messages=[...])
    """
    return TrackedAnthropic(
        client,
        app=app,
        api_key=api_key,
        base_url=base_url,
        environment=environment,
        version=version,
        schema=schema,
    )


# ==================== GOOGLE AI WRAPPER ====================

class TrackedGoogleAI:
    """Wrapper around Google AI GenerativeModel that auto-tracks all generations."""

    def __init__(
        self,
        model: Any,
        app: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://www.deadpipe.com/api/v1",
        environment: Optional[str] = None,
        version: Optional[str] = None,
        schema: Optional[Type] = None,
    ):
        self._model = model
        self._kwargs = {
            "api_key": api_key,
            "base_url": base_url,
            "app_id": app,
            "environment": environment,
            "version": version,
            "schema": schema,
        }

    def generate_content(self, contents, *, prompt_id: Optional[str] = None, schema: Optional[Type] = None, enum_fields: Optional[dict] = None, numeric_bounds: Optional[dict] = None, **api_kwargs):
        if not prompt_id:
            import sys
            print("[Deadpipe] prompt_id is required for tracking. Call will not be tracked.", file=sys.stderr)
            return self._model.generate_content(contents, **api_kwargs)
        
        # Merge per-call options with defaults (per-call wins)
        track_kwargs = {**self._kwargs}
        if schema is not None:
            track_kwargs["schema"] = schema
        if enum_fields is not None:
            track_kwargs["enum_fields"] = enum_fields
        if numeric_bounds is not None:
            track_kwargs["numeric_bounds"] = numeric_bounds
        
        with track(prompt_id=prompt_id, **track_kwargs) as t:
            response = self._model.generate_content(contents, **api_kwargs)
            # Convert to messages format for context extraction
            if isinstance(contents, str):
                input_data = {"messages": [{"role": "user", "content": contents}]}
            elif isinstance(contents, list):
                input_data = {"messages": [{"role": "user", "content": str(c)} for c in contents]}
            else:
                input_data = {"messages": [{"role": "user", "content": str(contents)}]}
            t.record(response, input=input_data)
            return response

    def start_chat(self, **kwargs):
        chat = self._model.start_chat(**kwargs)
        return _TrackedGoogleAIChat(chat, **self._kwargs)

    def __getattr__(self, name):
        return getattr(self._model, name)


class _TrackedGoogleAIChat:
    def __init__(self, chat, **kwargs):
        self._chat = chat
        self._kwargs = kwargs

    def send_message(self, content, *, prompt_id: Optional[str] = None, schema: Optional[Type] = None, enum_fields: Optional[dict] = None, numeric_bounds: Optional[dict] = None, **api_kwargs):
        if not prompt_id:
            import sys
            print("[Deadpipe] prompt_id is required for tracking. Call will not be tracked.", file=sys.stderr)
            return self._chat.send_message(content, **api_kwargs)
        
        # Merge per-call options with defaults (per-call wins)
        track_kwargs = {**self._kwargs}
        if schema is not None:
            track_kwargs["schema"] = schema
        if enum_fields is not None:
            track_kwargs["enum_fields"] = enum_fields
        if numeric_bounds is not None:
            track_kwargs["numeric_bounds"] = numeric_bounds
        
        with track(prompt_id=prompt_id, **track_kwargs) as t:
            response = self._chat.send_message(content, **api_kwargs)
            input_data = {"messages": [{"role": "user", "content": str(content)}]}
            t.record(response, input=input_data)
            return response

    def __getattr__(self, name):
        return getattr(self._chat, name)


def wrap_google_ai(
    model: Any,
    app: Optional[str] = None,
    *,
    api_key: Optional[str] = None,
    base_url: str = "https://www.deadpipe.com/api/v1",
    environment: Optional[str] = None,
    version: Optional[str] = None,
    schema: Optional[Type] = None,
) -> TrackedGoogleAI:
    """Wrap a Google AI GenerativeModel to automatically track all generations.
    
    Args:
        model: The Google AI GenerativeModel instance
        app: Optional app identifier (can also use DEADPIPE_APP_ID env var)
        
    Each call must include prompt_id:
        model.generate_content("Hello", prompt_id="chat_agent")
    """
    return TrackedGoogleAI(
        model,
        app=app,
        api_key=api_key,
        base_url=base_url,
        environment=environment,
        version=version,
        schema=schema,
    )


# ==================== MISTRAL WRAPPER ====================

class TrackedMistral:
    """Wrapper around Mistral client that auto-tracks all completions."""

    def __init__(
        self,
        client: Any,
        app: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://www.deadpipe.com/api/v1",
        environment: Optional[str] = None,
        version: Optional[str] = None,
        schema: Optional[Type] = None,
    ):
        self._client = client
        self._kwargs = {
            "api_key": api_key,
            "base_url": base_url,
            "app_id": app,
            "environment": environment,
            "version": version,
            "schema": schema,
        }

        if hasattr(client, "chat"):
            self.chat = _TrackedMistralChat(client.chat, **self._kwargs)

    def __getattr__(self, name):
        return getattr(self._client, name)


class _TrackedMistralChat:
    def __init__(self, chat, **kwargs):
        self._chat = chat
        self._kwargs = kwargs

        # v1.x style
        if hasattr(chat, "complete"):
            self.complete = self._tracked_complete

        # v0.x style (OpenAI-compatible)
        if hasattr(chat, "completions"):
            self.completions = _TrackedMistralCompletions(chat.completions, **kwargs)

    def _tracked_complete(self, **api_kwargs):
        # Extract deadpipe-specific params (prompt_id required, others optional per-call)
        prompt_id = api_kwargs.pop("prompt_id", None)
        schema = api_kwargs.pop("schema", None)
        enum_fields = api_kwargs.pop("enum_fields", None)
        numeric_bounds = api_kwargs.pop("numeric_bounds", None)
        
        if not prompt_id:
            import sys
            print("[Deadpipe] prompt_id is required for tracking. Call will not be tracked.", file=sys.stderr)
            return self._chat.complete(**api_kwargs)
        
        # Merge per-call options with defaults (per-call wins)
        track_kwargs = {**self._kwargs}
        if schema is not None:
            track_kwargs["schema"] = schema
        if enum_fields is not None:
            track_kwargs["enum_fields"] = enum_fields
        if numeric_bounds is not None:
            track_kwargs["numeric_bounds"] = numeric_bounds
        
        with track(prompt_id=prompt_id, **track_kwargs) as t:
            response = self._chat.complete(**api_kwargs)
            t.record(response, input=api_kwargs)
            return response

    def __getattr__(self, name):
        return getattr(self._chat, name)


class _TrackedMistralCompletions:
    def __init__(self, completions, **kwargs):
        self._completions = completions
        self._kwargs = kwargs

    def create(self, **api_kwargs):
        # Extract deadpipe-specific params (prompt_id required, others optional per-call)
        prompt_id = api_kwargs.pop("prompt_id", None)
        schema = api_kwargs.pop("schema", None)
        enum_fields = api_kwargs.pop("enum_fields", None)
        numeric_bounds = api_kwargs.pop("numeric_bounds", None)
        
        if not prompt_id:
            import sys
            print("[Deadpipe] prompt_id is required for tracking. Call will not be tracked.", file=sys.stderr)
            return self._completions.create(**api_kwargs)
        
        # Merge per-call options with defaults (per-call wins)
        track_kwargs = {**self._kwargs}
        if schema is not None:
            track_kwargs["schema"] = schema
        if enum_fields is not None:
            track_kwargs["enum_fields"] = enum_fields
        if numeric_bounds is not None:
            track_kwargs["numeric_bounds"] = numeric_bounds
        
        with track(prompt_id=prompt_id, **track_kwargs) as t:
            response = self._completions.create(**api_kwargs)
            t.record(response, input=api_kwargs)
            return response


def wrap_mistral(
    client: Any,
    app: Optional[str] = None,
    *,
    api_key: Optional[str] = None,
    base_url: str = "https://www.deadpipe.com/api/v1",
    environment: Optional[str] = None,
    version: Optional[str] = None,
    schema: Optional[Type] = None,
) -> TrackedMistral:
    """Wrap a Mistral client to automatically track all completions.
    
    Args:
        client: The Mistral client instance
        app: Optional app identifier (can also use DEADPIPE_APP_ID env var)
        
    Each call must include prompt_id:
        client.chat.complete(prompt_id="code_gen", model="mistral-large", messages=[...])
    """
    return TrackedMistral(
        client,
        app=app,
        api_key=api_key,
        base_url=base_url,
        environment=environment,
        version=version,
        schema=schema,
    )


# ==================== COHERE WRAPPER ====================

class TrackedCohere:
    """Wrapper around Cohere client that auto-tracks all chat/generate calls."""

    def __init__(
        self,
        client: Any,
        app: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://www.deadpipe.com/api/v1",
        environment: Optional[str] = None,
        version: Optional[str] = None,
        schema: Optional[Type] = None,
    ):
        self._client = client
        self._kwargs = {
            "api_key": api_key,
            "base_url": base_url,
            "app_id": app,
            "environment": environment,
            "version": version,
            "schema": schema,
        }

    def chat(self, *, prompt_id: Optional[str] = None, schema: Optional[Type] = None, enum_fields: Optional[dict] = None, numeric_bounds: Optional[dict] = None, **api_kwargs):
        if not prompt_id:
            import sys
            print("[Deadpipe] prompt_id is required for tracking. Call will not be tracked.", file=sys.stderr)
            return self._client.chat(**api_kwargs)
        
        # Merge per-call options with defaults (per-call wins)
        track_kwargs = {**self._kwargs}
        if schema is not None:
            track_kwargs["schema"] = schema
        if enum_fields is not None:
            track_kwargs["enum_fields"] = enum_fields
        if numeric_bounds is not None:
            track_kwargs["numeric_bounds"] = numeric_bounds
        
        with track(prompt_id=prompt_id, **track_kwargs) as t:
            response = self._client.chat(**api_kwargs)
            # Convert Cohere params to messages format
            messages = api_kwargs.get("chat_history", [])
            if api_kwargs.get("message"):
                messages = messages + [{"role": "user", "content": api_kwargs["message"]}]
            t.record(response, input={"messages": messages})
            return response

    def generate(self, *, prompt_id: Optional[str] = None, schema: Optional[Type] = None, enum_fields: Optional[dict] = None, numeric_bounds: Optional[dict] = None, **api_kwargs):
        if not prompt_id:
            import sys
            print("[Deadpipe] prompt_id is required for tracking. Call will not be tracked.", file=sys.stderr)
            return self._client.generate(**api_kwargs)
        
        # Merge per-call options with defaults (per-call wins)
        track_kwargs = {**self._kwargs}
        if schema is not None:
            track_kwargs["schema"] = schema
        if enum_fields is not None:
            track_kwargs["enum_fields"] = enum_fields
        if numeric_bounds is not None:
            track_kwargs["numeric_bounds"] = numeric_bounds
        
        with track(prompt_id=prompt_id, **track_kwargs) as t:
            response = self._client.generate(**api_kwargs)
            input_data = {"messages": [{"role": "user", "content": api_kwargs.get("prompt", "")}]}
            t.record(response, input=input_data)
            return response

    def __getattr__(self, name):
        return getattr(self._client, name)


def wrap_cohere(
    client: Any,
    app: Optional[str] = None,
    *,
    api_key: Optional[str] = None,
    base_url: str = "https://www.deadpipe.com/api/v1",
    environment: Optional[str] = None,
    version: Optional[str] = None,
    schema: Optional[Type] = None,
) -> TrackedCohere:
    """Wrap a Cohere client to automatically track all chat/generate calls.
    
    Args:
        client: The Cohere client instance
        app: Optional app identifier (can also use DEADPIPE_APP_ID env var)
        
    Each call must include prompt_id:
        client.chat(prompt_id="assistant", message="Hello")
    """
    return TrackedCohere(
        client,
        app=app,
        api_key=api_key,
        base_url=base_url,
        environment=environment,
        version=version,
        schema=schema,
    )


# ==================== UNIVERSAL WRAPPER ====================

def wrap(
    client: Any,
    app: Optional[str] = None,
    *,
    api_key: Optional[str] = None,
    base_url: str = "https://www.deadpipe.com/api/v1",
    environment: Optional[str] = None,
    version: Optional[str] = None,
    schema: Optional[Type] = None,
) -> Any:
    """
    Universal wrapper that auto-detects the provider and wraps appropriately.

    Example:
        from deadpipe import wrap
        from openai import OpenAI
        from anthropic import Anthropic

        # Wrap once with app context
        openai = wrap(OpenAI(), app="my_app")
        anthropic = wrap(Anthropic(), app="my_app")

        # Pass prompt_id per call
        openai.chat.completions.create(prompt_id="checkout", model="gpt-4", messages=[...])
        anthropic.messages.create(prompt_id="support", model="claude-3-opus", messages=[...])
    
    Args:
        client: The LLM provider client instance
        app: Optional app identifier (can also use DEADPIPE_APP_ID env var)
    """
    kwargs = {
        "api_key": api_key,
        "base_url": base_url,
        "environment": environment,
        "version": version,
        "schema": schema,
    }

    provider = detect_client_provider(client)

    if provider == "openai":
        return wrap_openai(client, app, **kwargs)
    elif provider == "anthropic":
        return wrap_anthropic(client, app, **kwargs)
    elif provider == "google":
        return wrap_google_ai(client, app, **kwargs)
    elif provider == "mistral":
        return wrap_mistral(client, app, **kwargs)
    elif provider == "cohere":
        return wrap_cohere(client, app, **kwargs)
    else:
        # Fallback: try to detect by structure
        if hasattr(client, "chat") and hasattr(client.chat, "completions"):
            return wrap_openai(client, app, **kwargs)
        if hasattr(client, "messages"):
            return wrap_anthropic(client, app, **kwargs)

        import sys
        print("[Deadpipe] Could not detect provider. Returning unwrapped client.", file=sys.stderr)
        return client


# ==================== DECORATOR SUPPORT ====================

from functools import wraps
from typing import Callable


def track_decorator(prompt_id: str, **options):
    """
    Decorator to automatically track function calls that return LLM responses.

    Usage:
        @track_decorator(prompt_id="my_agent")
        def my_llm_function():
            client = OpenAI()
            return client.chat.completions.create(...)

    Note: For best results, use wrap() instead. This decorator is for
    cases where you can't modify the client initialization.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if hasattr(result, 'choices') or (hasattr(result, 'content') and hasattr(result, 'model')):
                with track(prompt_id=prompt_id, **options) as t:
                    input_params = kwargs if 'messages' in kwargs or 'model' in kwargs else None
                    t.record(result, input=input_params)
            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if hasattr(result, 'choices') or (hasattr(result, 'content') and hasattr(result, 'model')):
                with track(prompt_id=prompt_id, **options) as t:
                    input_params = kwargs if 'messages' in kwargs or 'model' in kwargs else None
                    t.record(result, input=input_params)
            return result

        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


__all__ = [
    # Universal wrapper (recommended)
    "wrap",

    # Provider-specific wrappers
    "wrap_openai",
    "wrap_anthropic",
    "wrap_google_ai",
    "wrap_mistral",
    "wrap_cohere",

    # Manual tracking
    "track",
    "track_decorator",
    "PromptTracker",
    "PromptTelemetry",

    # Tracked client classes
    "TrackedOpenAI",
    "TrackedAnthropic",
    "TrackedGoogleAI",
    "TrackedMistral",
    "TrackedCohere",

    # Response extraction utilities
    "extract_response",
    "extract_openai_response",
    "extract_anthropic_response",
    "extract_google_ai_response",
    "extract_mistral_response",
    "extract_cohere_response",

    # Provider detection
    "detect_provider",
    "detect_client_provider",

    # Validation utilities
    "estimate_cost",
    "detect_refusal",
    "validate_with_pydantic",
    "validate_enum_bounds",
    "validate_numeric_bounds",
]
