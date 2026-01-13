import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from openai import AsyncOpenAI

try:
    from anthropic import AsyncAnthropic

    HAS_ANTHROPIC = True
except ImportError:  # pragma: no cover - optional provider
    HAS_ANTHROPIC = False
    AsyncAnthropic = None  # type: ignore

try:
    import google.generativeai as genai

    HAS_GENAI = True
except ImportError:  # pragma: no cover - optional provider
    HAS_GENAI = False
    genai = None  # type: ignore

try:
    from ollama import AsyncClient as OllamaAsyncClient

    HAS_OLLAMA = True
except ImportError:  # pragma: no cover - optional provider
    HAS_OLLAMA = False
    OllamaAsyncClient = None  # type: ignore

# Pricing table expressed in USD per 1K tokens for prompt and completion.
PRICING_USD_PER_1K = {
    "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
    "gpt-4o": {"prompt": 0.005, "completion": 0.015},
    "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
}


def _get_usage_value(usage: Any, key: str) -> int:
    if usage is None:
        return 0
    if isinstance(usage, dict):
        return int(usage.get(key, 0) or 0)
    return int(getattr(usage, key, 0) or 0)


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    pricing = PRICING_USD_PER_1K.get(model)
    if not pricing:
        for key, value in PRICING_USD_PER_1K.items():
            if model.startswith(key):
                pricing = value
                break
    if not pricing:
        return 0.0
    prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
    completion_cost = (completion_tokens / 1000) * pricing["completion"]
    return prompt_cost + completion_cost


@dataclass
class InvocationMetrics:
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency: float
    cost: float


def _normalize_tool_calls(raw: Any) -> List[Dict[str, Any]]:
    """Convert provider-specific tool call payloads into a simple shape."""
    normalized: List[Dict[str, Any]] = []
    if not raw:
        return normalized

    iterable = raw if isinstance(raw, (list, tuple)) else [raw]
    for call in iterable:
        name = None
        arguments = None

        # OpenAI style: call.function.name / arguments
        function = getattr(call, "function", None) or (call.get("function") if isinstance(call, dict) else None)
        if function:
            name = getattr(function, "name", None) or (function.get("name") if isinstance(function, dict) else None)
            arguments = getattr(function, "arguments", None) or (
                function.get("arguments") if isinstance(function, dict) else None
            )

        # Fallbacks
        name = name or getattr(call, "name", None) or (call.get("name") if isinstance(call, dict) else None)
        arguments = (
            arguments or getattr(call, "arguments", None) or (call.get("arguments") if isinstance(call, dict) else None)
        )

        normalized.append({"name": str(name or ""), "arguments": arguments})
    return normalized


@dataclass
class ProviderResponse:
    content: str
    metrics: InvocationMetrics
    tool_calls: List[Dict[str, Any]]


class BaseProvider(Protocol):
    name: str

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.0,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> ProviderResponse: ...


class OpenAIProvider:
    name = "openai"

    def __init__(self, client: Optional[AsyncOpenAI] = None, api_key: Optional[str] = None):
        if client is None:
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable must be set")
            client = AsyncOpenAI(api_key=api_key)
        self._client = client

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.0,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> ProviderResponse:
        start_time = time.perf_counter()
        response = await self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=response_format,
        )
        latency = time.perf_counter() - start_time

        usage = getattr(response, "usage", None)
        prompt_tokens = _get_usage_value(usage, "prompt_tokens")
        completion_tokens = _get_usage_value(usage, "completion_tokens")
        total_tokens = _get_usage_value(usage, "total_tokens")
        if not total_tokens:
            total_tokens = prompt_tokens + completion_tokens

        cost = estimate_cost(model, prompt_tokens, completion_tokens)
        message = response.choices[0].message
        content = message.content or ""
        tool_calls = _normalize_tool_calls(getattr(message, "tool_calls", None))
        metrics = InvocationMetrics(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency=latency,
            cost=cost,
        )
        return ProviderResponse(content=str(content), metrics=metrics, tool_calls=tool_calls)


class ChatCompletionsProvider:
    """Adapter for any client exposing chat.completions.create."""

    name = "chat_completions"

    def __init__(self, client: Any, default_model: str = ""):
        if client is None:
            raise ValueError("client is required for ChatCompletionsProvider")
        self._client = client
        self._default_model = default_model

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.0,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> ProviderResponse:
        start_time = time.perf_counter()
        response = await self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=response_format,
        )
        latency = time.perf_counter() - start_time

        usage = getattr(response, "usage", None)
        prompt_tokens = _get_usage_value(usage, "prompt_tokens")
        completion_tokens = _get_usage_value(usage, "completion_tokens")
        total_tokens = _get_usage_value(usage, "total_tokens")
        if not total_tokens:
            total_tokens = prompt_tokens + completion_tokens

        resolved_model = model or self._default_model or ""
        cost = estimate_cost(resolved_model, prompt_tokens, completion_tokens)
        message = response.choices[0].message
        content = message.content or ""
        tool_calls = _normalize_tool_calls(getattr(message, "tool_calls", None))
        metrics = InvocationMetrics(
            model=resolved_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency=latency,
            cost=cost,
        )
        return ProviderResponse(content=str(content), metrics=metrics, tool_calls=tool_calls)


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, client: Optional[Any] = None, api_key: Optional[str] = None, max_tokens: int = 1024):
        if not HAS_ANTHROPIC:
            raise ImportError("anthropic is not installed. Run `pip install anthropic` to enable this provider.")
        if client is None:
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable must be set for Anthropic provider")
            client = AsyncAnthropic(api_key=api_key)
        self._client = client
        self._max_tokens = max_tokens

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.0,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> ProviderResponse:
        system_messages = [m.get("content", "") for m in messages if m.get("role") == "system"]
        system_prompt = "\n".join(system_messages) if system_messages else None
        user_messages = [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in messages
            if m.get("role") != "system"
        ]

        start_time = time.perf_counter()
        response = await self._client.messages.create(
            model=model,
            system=system_prompt,
            messages=user_messages,
            temperature=temperature,
            max_tokens=self._max_tokens,
        )
        latency = time.perf_counter() - start_time

        usage = getattr(response, "usage", None)
        prompt_tokens = _get_usage_value(usage, "input_tokens")
        completion_tokens = _get_usage_value(usage, "output_tokens")
        total_tokens = prompt_tokens + completion_tokens

        content = ""
        tool_calls: List[Dict[str, Any]] = []
        if getattr(response, "content", None):
            first_chunk = response.content[0]
            content = getattr(first_chunk, "text", None) or getattr(first_chunk, "content", None) or str(first_chunk)

        metrics = InvocationMetrics(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency=latency,
            cost=estimate_cost(model, prompt_tokens, completion_tokens),
        )
        return ProviderResponse(content=str(content), metrics=metrics, tool_calls=tool_calls)


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: Optional[str] = None):
        if not HAS_GENAI:
            raise ImportError(
                "google-generativeai is not installed. Run `pip install google-generativeai` to enable this provider."
            )
        api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GENAI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable must be set for Gemini provider")
        genai.configure(api_key=api_key)

    @staticmethod
    def _to_prompt(messages: List[Dict[str, Any]]) -> str:
        parts = []
        for msg in messages:
            role = msg.get("role", "user").upper()
            parts.append(f"{role}: {msg.get('content', '')}")
        return "\n".join(parts)

    @staticmethod
    def _extract_text(response: Any) -> str:
        if response is None:
            return ""
        text = getattr(response, "text", None)
        if text:
            return str(text)
        candidates = getattr(response, "candidates", None) or []
        if candidates:
            candidate = candidates[0]
            content_parts = getattr(candidate, "content", None)
            parts = getattr(content_parts, "parts", None) if content_parts else None
            if parts:
                first_part = parts[0]
                return str(getattr(first_part, "text", first_part))
        return str(response)

    @staticmethod
    def _usage(response: Any) -> Dict[str, int]:
        usage = getattr(response, "usage_metadata", None)
        if not usage:
            return {"prompt": 0, "completion": 0, "total": 0}
        prompt = int(getattr(usage, "prompt_token_count", 0) or 0)
        completion = int(getattr(usage, "candidates_token_count", 0) or 0)
        total = int(getattr(usage, "total_token_count", prompt + completion) or 0)
        return {"prompt": prompt, "completion": completion, "total": total}

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.0,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> ProviderResponse:
        prompt = self._to_prompt(messages)

        def _generate() -> Any:
            generation_config = {"temperature": temperature}
            if response_format and response_format.get("type") == "json_object":
                generation_config["response_mime_type"] = "application/json"
            gemini_model = genai.GenerativeModel(model)
            return gemini_model.generate_content(prompt, generation_config=generation_config)

        start_time = time.perf_counter()
        response = await asyncio.to_thread(_generate)
        latency = time.perf_counter() - start_time

        usage = self._usage(response)
        prompt_tokens = usage["prompt"]
        completion_tokens = usage["completion"]
        total_tokens = usage["total"] or (prompt_tokens + completion_tokens)

        metrics = InvocationMetrics(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency=latency,
            cost=estimate_cost(model, prompt_tokens, completion_tokens),
        )
        content = self._extract_text(response)
        return ProviderResponse(content=str(content), metrics=metrics, tool_calls=_normalize_tool_calls(None))


class OllamaProvider:
    name = "ollama"

    def __init__(self, client: Optional[Any] = None, host: Optional[str] = None):
        if not HAS_OLLAMA:
            raise ImportError("ollama is not installed. Run `pip install ollama` to enable this provider.")
        if client is None:
            client = OllamaAsyncClient(host=host) if host else OllamaAsyncClient()
        self._client = client

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.0,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> ProviderResponse:
        payload_messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages]

        start_time = time.perf_counter()
        response = await self._client.chat(
            model=model,
            messages=payload_messages,
            options={"temperature": temperature},
        )
        latency = time.perf_counter() - start_time

        content = ""
        tool_calls: List[Dict[str, Any]] = []
        if isinstance(response, dict):
            content = str(response.get("message", {}).get("content", ""))
            prompt_tokens = int(response.get("prompt_eval_count", 0) or 0)
            completion_tokens = int(response.get("eval_count", 0) or 0)
        else:
            content = str(getattr(response, "message", {}).get("content", ""))
            prompt_tokens = int(getattr(response, "prompt_eval_count", 0) or 0)
            completion_tokens = int(getattr(response, "eval_count", 0) or 0)

        total_tokens = prompt_tokens + completion_tokens
        metrics = InvocationMetrics(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency=latency,
            cost=0.0,
        )
        return ProviderResponse(content=content, metrics=metrics, tool_calls=tool_calls)


def create_provider(name: str, client: Optional[Any] = None) -> BaseProvider:
    normalized = (name or "openai").lower()
    if normalized in {"openai", "oai"}:
        return OpenAIProvider(client=client)
    if normalized in {"anthropic", "claude"}:
        return AnthropicProvider(client=client)
    if normalized in {"gemini", "google", "google-genai"}:
        return GeminiProvider()
    if normalized in {"ollama"}:
        return OllamaProvider(client=client)
    raise ValueError(f"Unsupported provider '{name}'")
