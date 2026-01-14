"""
Google Gemini Wrapper
Automatically tracks Google Gemini API calls with Orbit

IMPORTANT: All tracking is non-blocking and runs in a background thread.
This wrapper adds zero latency to your AI responses.
"""

import time
import uuid
from functools import wraps
from typing import Any, Iterator, Optional, TypeVar

from ..types import WrapperOptions

T = TypeVar("T")


def wrap_google(
    client: T,
    orbit: Any,  # OrbitClient - avoid circular import
    default_options: Optional[WrapperOptions] = None,
) -> T:
    """
    Wrap a Google GenAI client to automatically track all content generations.

    IMPORTANT: Tracking is completely non-blocking - it adds zero latency
    to your AI responses. All tracking happens in a background thread.

    Usage:
        from google import genai
        from withorbit_sdk import Orbit

        orbit = Orbit(api_key="orb_live_xxx")
        client = genai.Client(api_key="your-gemini-api-key")
        wrapped = orbit.wrap_google(client, WrapperOptions(feature="chat"))

        # All calls automatically tracked (zero overhead)
        response = wrapped.models.generate_content(
            model="gemini-2.0-flash",
            contents="Hello, how are you?",
        )
    """
    original_generate_content = client.models.generate_content
    original_generate_content_stream = client.models.generate_content_stream

    @wraps(original_generate_content)
    def wrapped_generate_content(*args: Any, **kwargs: Any) -> Any:
        # Merge options
        options = default_options or WrapperOptions()

        start_time = time.time()
        request_id = str(uuid.uuid4())
        model = kwargs.get("model", args[0] if args else "unknown")

        try:
            response = original_generate_content(*args, **kwargs)

            # Non-streaming response - track latency BEFORE returning
            latency_ms = int((time.time() - start_time) * 1000)

            # Extract token counts from usage_metadata
            input_tokens = 0
            output_tokens = 0
            actual_model = model

            if hasattr(response, "usage_metadata") and response.usage_metadata:
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

            if hasattr(response, "model_version") and response.model_version:
                actual_model = response.model_version

            # Non-blocking: track() returns immediately (background thread)
            orbit.track(
                model=actual_model,
                provider="google",
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
                provider="google",
                latency_ms=latency_ms,
                request_id=request_id,
                feature=options.feature,
                environment=options.environment,
                user_id=options.user_id,
                session_id=options.session_id,
                metadata=options.metadata,
            )

            raise

    @wraps(original_generate_content_stream)
    def wrapped_generate_content_stream(*args: Any, **kwargs: Any) -> Any:
        # Merge options
        options = default_options or WrapperOptions()

        start_time = time.time()
        request_id = str(uuid.uuid4())
        model = kwargs.get("model", args[0] if args else "unknown")

        try:
            stream = original_generate_content_stream(*args, **kwargs)
            return _wrap_stream(
                stream,
                model,
                start_time,
                request_id,
                orbit,
                options,
            )
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_type = _extract_error_type(e)
            error_message = str(e)

            orbit.track_error(
                model=model,
                error_type=error_type,
                error_message=error_message,
                provider="google",
                latency_ms=latency_ms,
                request_id=request_id,
                feature=options.feature,
                environment=options.environment,
                user_id=options.user_id,
                session_id=options.session_id,
                metadata=options.metadata,
            )

            raise

    client.models.generate_content = wrapped_generate_content
    client.models.generate_content_stream = wrapped_generate_content_stream
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

    class WrappedStream:
        def __init__(self, inner_stream: Any):
            self._inner = inner_stream

        def __iter__(self) -> Iterator[Any]:
            nonlocal input_tokens, output_tokens, actual_model

            try:
                for chunk in self._inner:
                    # Capture usage metadata from chunks (usually in final chunk)
                    if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
                        input_tokens = getattr(chunk.usage_metadata, "prompt_token_count", 0) or 0
                        output_tokens = getattr(chunk.usage_metadata, "candidates_token_count", 0) or 0

                    yield chunk

                latency_ms = int((time.time() - start_time) * 1000)

                # Non-blocking: track() returns immediately (background thread)
                orbit.track(
                    model=actual_model,
                    provider="google",
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
                    provider="google",
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
    """Extract error type from Google Gemini errors."""
    # Check for gRPC status codes (used by Google APIs)
    if hasattr(error, "code"):
        code = error.code
        if callable(code):
            code = code()
        if isinstance(code, int):
            if code == 8 or code == 429:
                return "rate_limit_exceeded"
            if code == 16 or code == 401:
                return "invalid_api_key"
            if code == 3 or code == 400:
                return "invalid_request"
            if code == 7 or code == 403:
                return "permission_denied"
            if code == 5 or code == 404:
                return "not_found"
            if code == 13 or code == 14 or code >= 500:
                return "server_error"

    # Check for HTTP status codes
    if hasattr(error, "status_code"):
        status = error.status_code
        if status == 429:
            return "rate_limit_exceeded"
        if status == 401:
            return "invalid_api_key"
        if status == 400:
            return "invalid_request"
        if status == 403:
            return "permission_denied"
        if status >= 500:
            return "server_error"

    # Check error message patterns
    error_msg = str(error).lower()
    if "quota" in error_msg or "rate limit" in error_msg:
        return "rate_limit_exceeded"
    if "api key" in error_msg or "authentication" in error_msg:
        return "invalid_api_key"
    if "permission" in error_msg:
        return "permission_denied"

    return "unknown_error"
