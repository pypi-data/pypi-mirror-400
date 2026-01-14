"""
OpenAI Wrapper
Automatically tracks OpenAI API calls with Orbit

IMPORTANT: All tracking is non-blocking and runs in a background thread.
This wrapper adds zero latency to your AI responses.
"""

import time
import uuid
from functools import wraps
from typing import Any, Iterator, Optional, TypeVar

from ..types import WrapperOptions

T = TypeVar("T")


def wrap_openai(
    client: T,
    orbit: Any,  # OrbitClient - avoid circular import
    default_options: Optional[WrapperOptions] = None,
) -> T:
    """
    Wrap an OpenAI client to automatically track all chat completions.

    IMPORTANT: Tracking is completely non-blocking - it adds zero latency
    to your AI responses. All tracking happens in a background thread.

    Usage:
        from openai import OpenAI
        from withorbit_sdk import Orbit

        orbit = Orbit(api_key="orb_live_xxx")
        openai = orbit.wrap_openai(OpenAI(), WrapperOptions(feature="chat"))

        # All calls automatically tracked (zero overhead)
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello!"}],
        )
    """
    original_create = client.chat.completions.create

    @wraps(original_create)
    def wrapped_create(*args: Any, **kwargs: Any) -> Any:
        # Merge options
        options = default_options or WrapperOptions()

        start_time = time.time()
        request_id = str(uuid.uuid4())
        model = kwargs.get("model", args[0] if args else "unknown")
        stream = kwargs.get("stream", False)

        try:
            response = original_create(*args, **kwargs)

            if stream:
                return _wrap_stream(
                    response,
                    model,
                    start_time,
                    request_id,
                    orbit,
                    options,
                )

            # Non-streaming response - track latency BEFORE returning
            latency_ms = int((time.time() - start_time) * 1000)

            # Non-blocking: track() returns immediately (background thread)
            orbit.track(
                model=getattr(response, "model", model),
                provider="openai",
                input_tokens=getattr(response.usage, "prompt_tokens", 0) if response.usage else 0,
                output_tokens=getattr(response.usage, "completion_tokens", 0) if response.usage else 0,
                latency_ms=latency_ms,
                status="success",
                request_id=request_id,
                feature=options.feature,
                environment=options.environment,
                user_id=options.user_id,
                session_id=options.session_id,
                metadata=options.metadata,
            )

            return response

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_type = _extract_error_type(e)
            error_message = str(e)

            # Non-blocking: track_error() returns immediately
            orbit.track_error(
                model=model,
                error_type=error_type,
                error_message=error_message,
                provider="openai",
                latency_ms=latency_ms,
                request_id=request_id,
                feature=options.feature,
                environment=options.environment,
                user_id=options.user_id,
                session_id=options.session_id,
                metadata=options.metadata,
            )

            raise

    client.chat.completions.create = wrapped_create
    return client


def _wrap_stream(
    stream: Iterator[Any],
    model: str,
    start_time: float,
    request_id: str,
    orbit: Any,
    options: WrapperOptions,
) -> Iterator[Any]:
    """Wrap a streaming response to track usage when complete (non-blocking)."""
    input_tokens = 0
    output_tokens = 0
    actual_model = model

    try:
        for chunk in stream:
            # Capture model name
            if hasattr(chunk, "model") and chunk.model:
                actual_model = chunk.model

            # Capture usage if available
            if hasattr(chunk, "usage") and chunk.usage:
                input_tokens = getattr(chunk.usage, "prompt_tokens", 0)
                output_tokens = getattr(chunk.usage, "completion_tokens", 0)

            yield chunk

        latency_ms = int((time.time() - start_time) * 1000)

        # Non-blocking: track() returns immediately (background thread)
        orbit.track(
            model=actual_model,
            provider="openai",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            status="success",
            request_id=request_id,
            feature=options.feature,
            environment=options.environment,
            user_id=options.user_id,
            session_id=options.session_id,
            metadata=options.metadata,
        )

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        error_type = _extract_error_type(e)
        error_message = str(e)

        # Non-blocking: track_error() returns immediately
        orbit.track_error(
            model=actual_model,
            error_type=error_type,
            error_message=error_message,
            provider="openai",
            latency_ms=latency_ms,
            request_id=request_id,
            feature=options.feature,
            environment=options.environment,
            user_id=options.user_id,
            session_id=options.session_id,
            metadata=options.metadata,
        )

        raise


def _extract_error_type(error: Exception) -> str:
    """Extract error type from OpenAI errors."""
    if hasattr(error, "code") and error.code:
        return str(error.code)
    if hasattr(error, "type") and error.type:
        return str(error.type)
    if hasattr(error, "status_code"):
        status = error.status_code
        if status == 429:
            return "rate_limit_exceeded"
        if status == 401:
            return "invalid_api_key"
        if status == 400:
            return "invalid_request"
        if status >= 500:
            return "server_error"

    return "unknown_error"
