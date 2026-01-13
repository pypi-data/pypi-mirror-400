"""Perf API Client for Python."""

import json
import time
import random
from typing import Iterator, Optional, Dict, Any, List, AsyncIterator

import httpx

from .types import (
    ChatResponse,
    ChatStreamChunk,
)
from .exceptions import (
    PerfError,
    RateLimitError,
    UsageLimitError,
    AuthenticationError,
    NetworkError,
    PerfTimeoutError,
)


DEFAULT_BASE_URL = "https://api.withperf.pro"
DEFAULT_TIMEOUT = 120.0  # 2 minutes
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # 1 second


class PerfClient:
    """Synchronous client for interacting with the Perf API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ):
        """
        Initialize the Perf client.

        Args:
            api_key: Your Perf API key (starts with pk_)
            base_url: API base URL (default: https://api.withperf.pro)
            timeout: Request timeout in seconds (default: 120)
            max_retries: Maximum retry attempts (default: 3)
            retry_delay: Base delay between retries in seconds (default: 1)
        """
        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def chat(
        self,
        messages: List[Dict[str, Any]],
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_cost_per_call: Optional[float] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> ChatResponse:
        """
        Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model override
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            max_cost_per_call: Maximum cost in USD
            metadata: Custom metadata to attach

        Returns:
            ChatResponse with completion and metadata

        Raises:
            PerfError: On API errors
            NetworkError: On network failures
            PerfTimeoutError: On request timeout
        """
        request_data: Dict[str, Any] = {
            "messages": messages,
        }

        if model is not None:
            request_data["model"] = model
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        if temperature is not None:
            request_data["temperature"] = temperature
        if top_p is not None:
            request_data["top_p"] = top_p
        if max_cost_per_call is not None:
            request_data["max_cost_per_call"] = max_cost_per_call
        if metadata is not None:
            request_data["metadata"] = metadata

        response = self._request_with_retry("/v1/chat", request_data)
        return ChatResponse.model_validate(response)

    def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_cost_per_call: Optional[float] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Iterator[ChatStreamChunk]:
        """
        Send a streaming chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model override
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            max_cost_per_call: Maximum cost in USD
            metadata: Custom metadata to attach

        Yields:
            ChatStreamChunk for each streamed piece

        Raises:
            PerfError: On API errors
            NetworkError: On network failures
            PerfTimeoutError: On request timeout
        """
        request_data: Dict[str, Any] = {
            "messages": messages,
            "stream": True,
        }

        if model is not None:
            request_data["model"] = model
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        if temperature is not None:
            request_data["temperature"] = temperature
        if top_p is not None:
            request_data["top_p"] = top_p
        if max_cost_per_call is not None:
            request_data["max_cost_per_call"] = max_cost_per_call
        if metadata is not None:
            request_data["metadata"] = metadata

        try:
            with self._client.stream(
                "POST",
                "/v1/chat/stream",
                json=request_data,
            ) as response:
                if response.status_code != 200:
                    error_body = response.read()
                    self._handle_error_response(
                        response.status_code, error_body, response.headers
                    )

                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:].strip()

                        if data == "[DONE]":
                            return

                        try:
                            chunk_data = json.loads(data)
                            yield ChatStreamChunk.model_validate(chunk_data)
                        except Exception:
                            # Skip malformed JSON
                            continue

        except httpx.TimeoutException as e:
            raise PerfTimeoutError(self.timeout) from e
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}", e) from e

    def chat_stream_to_string(
        self,
        messages: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> str:
        """
        Send a streaming request and collect all content into a string.

        Args:
            messages: List of message dicts
            **kwargs: Additional arguments passed to chat_stream

        Returns:
            Complete response content as a string
        """
        content_parts = []

        for chunk in self.chat_stream(messages, **kwargs):
            if chunk.choices and chunk.choices[0].delta.content:
                content_parts.append(chunk.choices[0].delta.content)

        return "".join(content_parts)

    def _request_with_retry(
        self, path: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make a request with automatic retry on retryable errors."""
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                return self._do_request(path, data)
            except PerfError as e:
                last_error = e

                if not e.is_retryable or attempt == self.max_retries:
                    raise

                # Calculate delay with exponential backoff
                delay = self.retry_delay * (2**attempt)

                # Use retry-after header if available
                if isinstance(e, RateLimitError) and e.retry_after:
                    delay = float(e.retry_after)

                # Add jitter
                delay += random.random()

                time.sleep(delay)

        raise last_error or Exception("Max retries exceeded")

    def _do_request(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a single request to the API."""
        try:
            response = self._client.post(path, json=data)

            if response.status_code != 200:
                self._handle_error_response(
                    response.status_code,
                    response.content,
                    response.headers,
                )

            return response.json()

        except httpx.TimeoutException as e:
            raise PerfTimeoutError(self.timeout) from e
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}", e) from e

    def _handle_error_response(
        self,
        status_code: int,
        body: bytes,
        headers: httpx.Headers,
    ) -> None:
        """Parse and raise appropriate error from response."""
        try:
            error_data = json.loads(body)
            error_info = error_data.get("error", {})
        except Exception:
            error_info = {
                "code": "internal_error",
                "message": f"HTTP {status_code}",
                "type": "api_error",
            }

        code = error_info.get("code", "internal_error")
        message = error_info.get("message", "Unknown error")
        error_type = error_info.get("type", "api_error")
        request_id = error_info.get("request_id")

        if code == "rate_limit_exceeded":
            retry_after = headers.get("Retry-After")
            raise RateLimitError(
                message,
                request_id,
                int(retry_after) if retry_after else None,
            )
        elif code == "usage_limit_exceeded":
            raise UsageLimitError(message, request_id)
        elif code == "invalid_api_key":
            raise AuthenticationError(message, request_id)
        else:
            raise PerfError(message, code, error_type, status_code, request_id)


class AsyncPerfClient:
    """Async client for interacting with the Perf API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ):
        """
        Initialize the async Perf client.

        Args:
            api_key: Your Perf API key (starts with pk_)
            base_url: API base URL (default: https://api.withperf.pro)
            timeout: Request timeout in seconds (default: 120)
            max_retries: Maximum retry attempts (default: 3)
            retry_delay: Base delay between retries in seconds (default: 1)
        """
        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_cost_per_call: Optional[float] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> ChatResponse:
        """
        Send a chat completion request asynchronously.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model override
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            max_cost_per_call: Maximum cost in USD
            metadata: Custom metadata to attach

        Returns:
            ChatResponse with completion and metadata
        """
        request_data: Dict[str, Any] = {"messages": messages}

        if model is not None:
            request_data["model"] = model
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        if temperature is not None:
            request_data["temperature"] = temperature
        if top_p is not None:
            request_data["top_p"] = top_p
        if max_cost_per_call is not None:
            request_data["max_cost_per_call"] = max_cost_per_call
        if metadata is not None:
            request_data["metadata"] = metadata

        response = await self._request_with_retry("/v1/chat", request_data)
        return ChatResponse.model_validate(response)

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_cost_per_call: Optional[float] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> AsyncIterator[ChatStreamChunk]:
        """
        Send a streaming chat completion request asynchronously.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Optional model override
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            max_cost_per_call: Maximum cost in USD
            metadata: Custom metadata to attach

        Yields:
            ChatStreamChunk for each streamed piece
        """
        request_data: Dict[str, Any] = {"messages": messages, "stream": True}

        if model is not None:
            request_data["model"] = model
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        if temperature is not None:
            request_data["temperature"] = temperature
        if top_p is not None:
            request_data["top_p"] = top_p
        if max_cost_per_call is not None:
            request_data["max_cost_per_call"] = max_cost_per_call
        if metadata is not None:
            request_data["metadata"] = metadata

        try:
            async with self._client.stream(
                "POST",
                "/v1/chat/stream",
                json=request_data,
            ) as response:
                if response.status_code != 200:
                    error_body = await response.aread()
                    self._handle_error_response(
                        response.status_code, error_body, response.headers
                    )

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:].strip()

                        if data == "[DONE]":
                            return

                        try:
                            chunk_data = json.loads(data)
                            yield ChatStreamChunk.model_validate(chunk_data)
                        except Exception:
                            continue

        except httpx.TimeoutException as e:
            raise PerfTimeoutError(self.timeout) from e
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}", e) from e

    async def chat_stream_to_string(
        self,
        messages: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> str:
        """
        Send a streaming request and collect all content into a string.

        Args:
            messages: List of message dicts
            **kwargs: Additional arguments passed to chat_stream

        Returns:
            Complete response content as a string
        """
        content_parts = []

        async for chunk in self.chat_stream(messages, **kwargs):
            if chunk.choices and chunk.choices[0].delta.content:
                content_parts.append(chunk.choices[0].delta.content)

        return "".join(content_parts)

    async def _request_with_retry(
        self, path: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make a request with automatic retry on retryable errors."""
        import asyncio

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                return await self._do_request(path, data)
            except PerfError as e:
                last_error = e

                if not e.is_retryable or attempt == self.max_retries:
                    raise

                delay = self.retry_delay * (2**attempt)

                if isinstance(e, RateLimitError) and e.retry_after:
                    delay = float(e.retry_after)

                delay += random.random()
                await asyncio.sleep(delay)

        raise last_error or Exception("Max retries exceeded")

    async def _do_request(
        self, path: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make a single request to the API."""
        try:
            response = await self._client.post(path, json=data)

            if response.status_code != 200:
                self._handle_error_response(
                    response.status_code,
                    response.content,
                    response.headers,
                )

            return response.json()

        except httpx.TimeoutException as e:
            raise PerfTimeoutError(self.timeout) from e
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}", e) from e

    def _handle_error_response(
        self,
        status_code: int,
        body: bytes,
        headers: httpx.Headers,
    ) -> None:
        """Parse and raise appropriate error from response."""
        try:
            error_data = json.loads(body)
            error_info = error_data.get("error", {})
        except Exception:
            error_info = {
                "code": "internal_error",
                "message": f"HTTP {status_code}",
                "type": "api_error",
            }

        code = error_info.get("code", "internal_error")
        message = error_info.get("message", "Unknown error")
        error_type = error_info.get("type", "api_error")
        request_id = error_info.get("request_id")

        if code == "rate_limit_exceeded":
            retry_after = headers.get("Retry-After")
            raise RateLimitError(
                message,
                request_id,
                int(retry_after) if retry_after else None,
            )
        elif code == "usage_limit_exceeded":
            raise UsageLimitError(message, request_id)
        elif code == "invalid_api_key":
            raise AuthenticationError(message, request_id)
        else:
            raise PerfError(message, code, error_type, status_code, request_id)
