"""
Anthropic Wrapper
Automatically tracks Anthropic API calls with Orbit

IMPORTANT: All tracking is non-blocking and runs in a background thread.
This wrapper adds zero latency to your AI responses.
"""

import time
import uuid
from functools import wraps
from typing import Any, Iterator, Optional, TypeVar

from ..types import WrapperOptions

T = TypeVar("T")


def wrap_anthropic(
    client: T,
    orbit: Any,  # OrbitClient - avoid circular import
    default_options: Optional[WrapperOptions] = None,
) -> T:
    """
    Wrap an Anthropic client to automatically track all messages.

    IMPORTANT: Tracking is completely non-blocking - it adds zero latency
    to your AI responses. All tracking happens in a background thread.

    Usage:
        from anthropic import Anthropic
        from withorbit_sdk import Orbit

        orbit = Orbit(api_key="orb_live_xxx")
        anthropic = orbit.wrap_anthropic(Anthropic(), WrapperOptions(feature="chat"))

        # All calls automatically tracked (zero overhead)
        message = anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": "Hello!"}],
        )
    """
    original_create = client.messages.create

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
                provider="anthropic",
                input_tokens=response.usage.input_tokens if response.usage else 0,
                output_tokens=response.usage.output_tokens if response.usage else 0,
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
                provider="anthropic",
                latency_ms=latency_ms,
                request_id=request_id,
                feature=options.feature,
                environment=options.environment,
                user_id=options.user_id,
                session_id=options.session_id,
                metadata=options.metadata,
            )

            raise

    client.messages.create = wrapped_create
    return client


def _wrap_stream(
    stream: Any,
    model: str,
    start_time: float,
    request_id: str,
    orbit: Any,
    options: WrapperOptions,
) -> Any:
    """Wrap a streaming response to track usage when complete (non-blocking)."""
    input_tokens = 0
    output_tokens = 0
    actual_model = model

    # For Anthropic's stream, we need to handle the context manager
    class WrappedStream:
        def __init__(self, inner_stream: Any):
            self._inner = inner_stream

        def __iter__(self) -> Iterator[Any]:
            nonlocal input_tokens, output_tokens, actual_model

            try:
                for event in self._inner:
                    # Capture model from message_start event
                    if hasattr(event, "type"):
                        if event.type == "message_start" and hasattr(event, "message"):
                            actual_model = getattr(event.message, "model", model)
                            if hasattr(event.message, "usage"):
                                input_tokens = event.message.usage.input_tokens

                        # Capture output tokens from message_delta event
                        if event.type == "message_delta" and hasattr(event, "usage"):
                            output_tokens = getattr(event.usage, "output_tokens", 0)

                    yield event

                latency_ms = int((time.time() - start_time) * 1000)

                # Non-blocking: track() returns immediately (background thread)
                orbit.track(
                    model=actual_model,
                    provider="anthropic",
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
                    provider="anthropic",
                    latency_ms=latency_ms,
                    request_id=request_id,
                    feature=options.feature,
                    environment=options.environment,
                    user_id=options.user_id,
                    session_id=options.session_id,
                    metadata=options.metadata,
                )

                raise

        def __enter__(self) -> "WrappedStream":
            if hasattr(self._inner, "__enter__"):
                self._inner.__enter__()
            return self

        def __exit__(self, *args: Any) -> None:
            if hasattr(self._inner, "__exit__"):
                self._inner.__exit__(*args)

    return WrappedStream(stream)


def _extract_error_type(error: Exception) -> str:
    """Extract error type from Anthropic errors."""
    if hasattr(error, "error") and isinstance(error.error, dict):
        error_type = error.error.get("type")
        if error_type:
            return str(error_type)

    if hasattr(error, "status_code"):
        status = error.status_code
        if status == 429:
            return "rate_limit_error"
        if status == 401:
            return "authentication_error"
        if status == 400:
            return "invalid_request_error"
        if status == 529:
            return "overloaded_error"
        if status >= 500:
            return "api_error"

    return "unknown_error"
