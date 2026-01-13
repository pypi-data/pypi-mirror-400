"""
Deadpipe - LLM observability that answers one question:
"Is this prompt behaving the same as when it was last safe?"

Recommended: Wrap your client (zero code changes)
    from deadpipe import wrap_openai
    from openai import OpenAI

    client = wrap_openai(OpenAI(), prompt_id="checkout_agent")
    # All calls automatically tracked with full context
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Process refund for order 1938"}]
    )

With decorator (alternative):
    from deadpipe import track
    from openai import OpenAI

    @track(prompt_id="checkout_agent")
    def my_function():
        client = OpenAI()
        return client.chat.completions.create(...)

Advanced: Manual tracking (for streaming, custom logic, etc.)
    from deadpipe import track
    from openai import OpenAI

    client = OpenAI()
    params = {"model": "gpt-4", "messages": [...]}

    with track(prompt_id="checkout_agent") as t:
        response = client.chat.completions.create(**params)
        t.record(response, input=params)  # Pass params to capture input
"""

import os
import time
import json
import hashlib
from contextlib import contextmanager
from typing import Optional, Literal, Any, TypeVar, Type, Dict, List
from dataclasses import dataclass, asdict
import urllib.request
import urllib.error

__version__ = "2.0.2"

T = TypeVar("T")
StatusType = Literal["success", "error", "timeout", "empty", "schema_violation", "refusal"]

# ==================== COST ESTIMATION ====================

# Approximate costs per 1K tokens (2026, updated)
MODEL_COSTS: dict[str, dict[str, float]] = {
    # OpenAI
    "gpt-4": {"input": 0.03, "output": 0.06},  # legacy
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},  # legacy
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4.1": {"input": 0.002, "output": 0.008},
    "gpt-5": {"input": 0.00175, "output": 0.014},
    "gpt-5-mini": {"input": 0.00025, "output": 0.002},
    "gpt-5.2-pro": {"input": 0.021, "output": 0.168},

    # Anthropic
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
    "claude-opus-4": {"input": 0.015, "output": 0.075},
    "claude-sonnet-4": {"input": 0.003, "output": 0.015},
    "claude-haiku-4": {"input": 0.00025, "output": 0.00125},
}

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    """Estimate cost in USD for a completion."""
    # Normalize model name
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
            # Skip None, empty strings, empty lists, and False booleans (but keep True)
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

def detect_provider(response: Any) -> str:
    """Auto-detect provider from response object."""
    if not response:
        return "unknown"
    
    # Anthropic has content array and stop_reason
    if hasattr(response, "content") and isinstance(response.content, list):
        return "anthropic"
    if hasattr(response, "stop_reason"):
        return "anthropic"
    
    # OpenAI has choices array or output field
    if hasattr(response, "choices"):
        return "openai"
    if hasattr(response, "output"):
        return "openai"
    
    # Check model name patterns
    if hasattr(response, "model"):
        model_lower = str(response.model).lower()
        if "claude" in model_lower:
            return "anthropic"
        if "gpt" in model_lower or "o1" in model_lower:
            return "openai"
    
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
    
    # Handle different response types
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
    
    # New responses API (gpt-4.1 style)
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
        # Anthropic returns list of content blocks
        text_blocks = [block.text for block in response.content if hasattr(block, "text")]
        result["content"] = "".join(text_blocks)
        
        # Tool use blocks
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
    "Is this prompt behaving the same as when it was last safe?"
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
        
        # Context hashes (auto-extracted from response or set by wrapper)
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
                
                # Try to extract provider error code
                if hasattr(exc_val, "status_code"):
                    self._telemetry.http_status = exc_val.status_code
                if hasattr(exc_val, "code"):
                    self._telemetry.provider_error_code = str(exc_val.code)
                    
                # Detect timeout
                if "timeout" in str(exc_val).lower():
                    self._telemetry.status = "timeout"
                    self._telemetry.timeout = True
            
            # Send even on error
            if not self._recorded:
                self._send()
        
        # Send if not already recorded
        elif not self._recorded:
            self._send()
        
        return False  # Don't suppress exceptions
    
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
        
        Returns:
            - If schema provided and validation passes: parsed/validated object
            - If schema provided and validation fails: None (check telemetry.schema_validation_pass)
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
        if detected_provider == "anthropic":
            extracted = extract_anthropic_response(response)
        else:
            extracted = extract_openai_response(response)
        
        # Extract input context from input params if provided
        if input:
            messages = input.get("messages", []) if isinstance(input, dict) else getattr(input, "messages", [])
            tools = input.get("tools") if isinstance(input, dict) else getattr(input, "tools", None)
            system_prompt = None
            
            for msg in messages:
                if msg.get("role") == "system" if isinstance(msg, dict) else getattr(msg, "role", None) == "system":
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
        
        # Update context hashes if they were set (by wrap_openai, input params, or manually)
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
        self._telemetry.http_status = 200  # Successful response
        
        content = extracted["content"]
        self._telemetry.output_length = len(content) if content else 0
        self._telemetry.empty_output = not content or len(content.strip()) == 0
        self._telemetry.truncated = extracted.get("finish_reason") == "length"
        
        # Tool calls
        tool_calls = extracted.get("tool_calls", [])
        self._telemetry.tool_call_flag = len(tool_calls) > 0
        self._telemetry.tool_calls_count = len(tool_calls)
        
        # Output hash
        if content:
            self._telemetry.output_hash = hash_content(content)
        
        # Capture previews for dashboard inspection (truncate to reasonable size)
        MAX_PREVIEW_LENGTH = 2000
        
        # Output preview
        if content:
            self._telemetry.output_preview = (
                content[:MAX_PREVIEW_LENGTH] + "..." 
                if len(content) > MAX_PREVIEW_LENGTH 
                else content
            )
        
        # Input preview - extract last user message
        if self._messages:
            user_messages = [m for m in self._messages if m.get("role") == "user"]
            if user_messages:
                last_user_msg = user_messages[-1].get("content", "")
                self._telemetry.input_preview = (
                    last_user_msg[:MAX_PREVIEW_LENGTH] + "..."
                    if len(last_user_msg) > MAX_PREVIEW_LENGTH
                    else last_user_msg
                )
        
        # System prompt preview
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
                # Try to find and parse JSON in content
                content_stripped = content.strip()
                if content_stripped.startswith("{") or content_stripped.startswith("["):
                    parsed_data = json.loads(content_stripped)
                    self._telemetry.json_parse_success = True
                elif "```json" in content_stripped:
                    # Extract from markdown code block
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
            # Only warn in development to avoid noise in production
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
            
            # Send asynchronously without blocking - fire and forget
            # Use a thread to avoid blocking the main execution
            import threading
            def send_async():
                try:
                    with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                        pass  # We don't need the response
                except Exception:
                    # Fail silently - never break user's LLM calls
                    pass
            
            thread = threading.Thread(target=send_async, daemon=True)
            thread.start()
                
        except Exception:
            # Fail silently - never break user's LLM calls
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


# ==================== CLIENT WRAPPER ====================

class TrackedOpenAI:
    """
    Wrapper around OpenAI client that auto-tracks all completions.
    
    Usage:
        from deadpipe import wrap_openai
        from openai import OpenAI
        
        client = wrap_openai(OpenAI(), prompt_id="my_agent")
        response = client.chat.completions.create(...)  # Automatically tracked
    """
    
    def __init__(
        self,
        client: Any,
        prompt_id: str,
        api_key: Optional[str] = None,
        base_url: str = "https://www.deadpipe.com/api/v1",
        app_id: Optional[str] = None,
        environment: Optional[str] = None,
        version: Optional[str] = None,
        schema: Optional[Type] = None,
    ):
        self._client = client
        self._prompt_id = prompt_id
        self._api_key = api_key
        self._base_url = base_url
        self._app_id = app_id
        self._environment = environment
        self._version = version
        self._schema = schema
        
        # Wrap chat.completions
        if hasattr(client, "chat") and hasattr(client.chat, "completions"):
            self.chat = _TrackedChat(
                client.chat,
                prompt_id=prompt_id,
                api_key=api_key,
                base_url=base_url,
                app_id=app_id,
                environment=environment,
                version=version,
                schema=schema,
            )
        
        # Wrap responses (new API)
        if hasattr(client, "responses"):
            self.responses = _TrackedResponses(
                client.responses,
                prompt_id=prompt_id,
                api_key=api_key,
                base_url=base_url,
                app_id=app_id,
                environment=environment,
                version=version,
                schema=schema,
            )
    
    def __getattr__(self, name):
        # Proxy all other attributes to the wrapped client
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
        # Auto-extract context from params for hashing
        messages = api_kwargs.get("messages", [])
        tools = api_kwargs.get("tools")
        system_prompt = None
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content", "")
                break
        
        with track(**self._kwargs) as t:
            response = self._completions.create(**api_kwargs)
            # Pass input params to record() so it can extract context
            t.record(response, input=api_kwargs)
            return response


class _TrackedResponses:
    """Wrapper for OpenAI's new responses API."""
    
    def __init__(self, responses, **kwargs):
        self._responses = responses
        self._kwargs = kwargs
    
    def create(self, **api_kwargs):
        input_content = api_kwargs.get("input", "")
        messages = [{"role": "user", "content": input_content}] if isinstance(input_content, str) else input_content
        
        with track(**self._kwargs) as t:
            response = self._responses.create(**api_kwargs)
            # Pass input params to record() so it can extract context
            t.record(response, input=api_kwargs)
            return response


def wrap_openai(
    client: Any,
    prompt_id: str,
    *,
    api_key: Optional[str] = None,
    base_url: str = "https://www.deadpipe.com/api/v1",
    app_id: Optional[str] = None,
    environment: Optional[str] = None,
    version: Optional[str] = None,
    schema: Optional[Type] = None,
) -> TrackedOpenAI:
    """
    Wrap an OpenAI client to automatically track all completions.
    
    Example:
        from deadpipe import wrap_openai
        from openai import OpenAI
        
        client = wrap_openai(OpenAI(), prompt_id="checkout_agent")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
        # Automatically tracked!
    """
    return TrackedOpenAI(
        client,
        prompt_id=prompt_id,
        api_key=api_key,
        base_url=base_url,
        app_id=app_id,
        environment=environment,
        version=version,
        schema=schema,
    )


# Decorator support for Python
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
    
    Note: For best results, use wrap_openai() instead. This decorator is for
    cases where you can't modify the client initialization.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # If result looks like an LLM response, track it
            if hasattr(result, 'choices') or (hasattr(result, 'content') and hasattr(result, 'model')):
                with track(prompt_id=prompt_id, **options) as t:
                    # Try to extract input from function args/kwargs
                    input_params = kwargs if 'messages' in kwargs or 'model' in kwargs else None
                    t.record(result, input=input_params)
            return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            # If result looks like an LLM response, track it
            if hasattr(result, 'choices') or (hasattr(result, 'content') and hasattr(result, 'model')):
                with track(prompt_id=prompt_id, **options) as t:
                    # Try to extract input from function args/kwargs
                    input_params = kwargs if 'messages' in kwargs or 'model' in kwargs else None
                    t.record(result, input=input_params)
            return result
        
        # Return appropriate wrapper based on whether function is async
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


__all__ = [
    "wrap_openai",  # Primary recommended method
    "track",  # Advanced manual tracking
    "track_decorator",  # Decorator alternative
    "PromptTracker",
    "PromptTelemetry",
    "TrackedOpenAI",
    # Utilities
    "estimate_cost",
    "detect_refusal",
    "extract_openai_response",
    "extract_anthropic_response",
    "validate_with_pydantic",
    "validate_enum_bounds",
    "validate_numeric_bounds",
]
