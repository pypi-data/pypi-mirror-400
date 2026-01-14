"""
Orbit SDK Client
Core client for sending events to Orbit API

IMPORTANT: This SDK is designed to be completely non-blocking.
All tracking operations run in background threads and never delay AI responses.
"""

import atexit
import logging
import queue
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar

import httpx

from .types import OrbitConfig, OrbitEvent, OrbitResponse, WrapperOptions

logger = logging.getLogger("orbit")

T = TypeVar("T")


class OrbitClient:
    """
    Core Orbit client for tracking LLM usage.

    IMPORTANT: All tracking is non-blocking and runs in a background thread.
    This ensures AI responses are never delayed by tracking operations.

    Usage:
        client = OrbitClient(OrbitConfig(api_key="orb_live_xxx"))
        client.track(model="gpt-4o", input_tokens=100, output_tokens=50)
    """

    def __init__(self, config: OrbitConfig):
        if not config.api_key:
            raise ValueError("Orbit API key is required")

        if not config.api_key.startswith("orb_"):
            raise ValueError('Invalid Orbit API key format. Keys should start with "orb_"')

        self._config = config

        # Thread-safe queue for events (non-blocking)
        self._event_queue: queue.Queue[OrbitEvent] = queue.Queue()
        self._batch_buffer: List[OrbitEvent] = []
        self._batch_lock = threading.Lock()

        # Background worker thread
        self._shutdown_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

        # HTTP client (used only by worker thread)
        self._http_client = httpx.Client(timeout=30.0)

        # Register shutdown handler
        atexit.register(self.shutdown)

        if config.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

        self._log("Orbit SDK initialized (non-blocking mode)")

    def _log(self, msg: str, *args: Any) -> None:
        if self._config.debug:
            logger.debug(msg, *args)

    def _warn(self, msg: str, *args: Any) -> None:
        logger.warning(msg, *args)

    def _worker_loop(self) -> None:
        """Background worker that processes events without blocking the main thread."""
        last_flush_time = time.time()

        while not self._shutdown_event.is_set():
            try:
                # Try to get events from queue (with timeout for periodic flush)
                try:
                    event = self._event_queue.get(timeout=0.1)
                    with self._batch_lock:
                        self._batch_buffer.append(event)
                except queue.Empty:
                    pass

                # Check if we should flush
                should_flush = False
                with self._batch_lock:
                    buffer_size = len(self._batch_buffer)
                    time_since_flush = time.time() - last_flush_time

                    if buffer_size >= self._config.batch_size:
                        should_flush = True
                    elif buffer_size > 0 and time_since_flush >= self._config.batch_interval:
                        should_flush = True

                if should_flush:
                    self._flush_batch()
                    last_flush_time = time.time()

            except Exception as e:
                self._warn(f"Worker error: {e}")

        # Final flush on shutdown
        self._flush_batch()

    def _flush_batch(self) -> None:
        """Flush buffered events (called from worker thread only)."""
        with self._batch_lock:
            if not self._batch_buffer:
                return
            events = self._batch_buffer.copy()
            self._batch_buffer.clear()

        try:
            self._send_events_internal(events)
        except Exception as e:
            self._warn(f"Failed to send events: {e}")
            # Events are lost on failure - this is intentional to never block

    def track(
        self,
        model: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        *,
        event: Optional[OrbitEvent] = None,
        **kwargs: Any,
    ) -> None:
        """
        Track a single event (non-blocking).

        This method returns immediately - the event is sent in the background.
        It will never delay your AI responses.

        Can be called with an OrbitEvent object or with keyword arguments:
            client.track(model="gpt-4o", input_tokens=100, output_tokens=50)
        """
        try:
            if event is None:
                if model is None:
                    self._warn("track() called without model - ignoring")
                    return
                event = OrbitEvent(
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    **kwargs,
                )

            enriched_event = self._enrich_event(event)

            # Non-blocking: just add to queue
            self._event_queue.put_nowait(enriched_event)
            self._log("Event queued (non-blocking)")

        except Exception as e:
            # Never raise - tracking must never affect AI calls
            self._warn(f"Track failed (silently ignored): {e}")

    def track_many(self, events: List[OrbitEvent]) -> None:
        """Track multiple events at once (non-blocking)."""
        try:
            for event in events:
                enriched_event = self._enrich_event(event)
                self._event_queue.put_nowait(enriched_event)
            self._log(f"{len(events)} events queued (non-blocking)")
        except Exception as e:
            self._warn(f"TrackMany failed (silently ignored): {e}")

    def flush(self) -> None:
        """Request a flush of queued events (non-blocking)."""
        # The worker thread will handle flushing
        pass

    def track_error(
        self,
        model: str,
        error_type: str,
        error_message: str,
        **kwargs: Any,
    ) -> None:
        """Track an error event (non-blocking)."""
        self.track(
            model=model,
            input_tokens=kwargs.pop("input_tokens", 0),
            output_tokens=0,
            status="error",
            error_type=error_type,
            error_message=error_message,
            **kwargs,
        )

    def _enrich_event(self, event: OrbitEvent) -> OrbitEvent:
        """Add default values to event."""
        if not event.feature and self._config.default_feature:
            event.feature = self._config.default_feature
        if not event.environment:
            event.environment = self._config.default_environment
        if not event.status:
            event.status = "success"
        if not event.timestamp:
            event.timestamp = datetime.utcnow().isoformat() + "Z"
        return event

    def _send_events_internal(self, events: List[OrbitEvent]) -> OrbitResponse:
        """Send events to the Orbit API (called from worker thread)."""
        self._log(f"Sending {len(events)} event(s)")

        last_error: Optional[Exception] = None
        max_attempts = self._config.max_retries if self._config.retry else 1

        for attempt in range(1, max_attempts + 1):
            try:
                response = self._http_client.post(
                    f"{self._config.base_url}/ingest",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self._config.api_key}",
                    },
                    json={"events": [e.to_dict() for e in events]},
                )

                if not response.is_success:
                    error_body = response.json() if response.content else {}
                    raise Exception(error_body.get("error", f"HTTP {response.status_code}"))

                data = response.json()
                result = OrbitResponse(
                    success=data.get("success", True),
                    received=data.get("received", len(events)),
                    total_tokens=data.get("total_tokens", 0),
                    total_cost_usd=data.get("total_cost_usd", 0.0),
                    message=data.get("message", ""),
                )

                self._log(
                    f"Successfully sent {result.received} event(s), cost: ${result.total_cost_usd:.6f}"
                )
                return result

            except Exception as e:
                last_error = e
                self._warn(f"Attempt {attempt}/{max_attempts} failed: {e}")

                if attempt < max_attempts:
                    # Exponential backoff: 0.1s, 0.2s, 0.4s, ...
                    delay = 0.1 * (2 ** (attempt - 1))
                    time.sleep(delay)

        raise last_error or Exception("Failed to send events")

    def shutdown(self) -> None:
        """Shutdown the client and flush remaining events."""
        self._log("Shutting down...")

        # Signal worker to stop
        self._shutdown_event.set()

        # Wait for worker to finish (with timeout)
        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)

        self._http_client.close()
        self._log("Shutdown complete")

    def __enter__(self) -> "OrbitClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.shutdown()


class Orbit(OrbitClient):
    """
    Main Orbit class with convenience methods for wrapping LLM clients.

    Usage:
        orbit = Orbit(api_key="orb_live_xxx")

        # Manual tracking
        orbit.track(model="gpt-4o", input_tokens=100, output_tokens=50)

        # Automatic tracking with OpenAI
        from openai import OpenAI
        openai = orbit.wrap_openai(OpenAI())
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        config: Optional[OrbitConfig] = None,
        **kwargs: Any,
    ):
        if config is not None:
            super().__init__(config)
        elif api_key is not None:
            super().__init__(OrbitConfig(api_key=api_key, **kwargs))
        else:
            raise ValueError("Either api_key or config must be provided")

    def wrap_openai(
        self,
        client: T,
        default_options: Optional[WrapperOptions] = None,
    ) -> T:
        """
        Wrap an OpenAI client for automatic tracking.

        Usage:
            from openai import OpenAI
            openai = orbit.wrap_openai(OpenAI(), WrapperOptions(feature="chat"))
        """
        from .wrappers.openai import wrap_openai

        return wrap_openai(client, self, default_options)

    def wrap_anthropic(
        self,
        client: T,
        default_options: Optional[WrapperOptions] = None,
    ) -> T:
        """
        Wrap an Anthropic client for automatic tracking.

        Usage:
            from anthropic import Anthropic
            anthropic = orbit.wrap_anthropic(Anthropic(), WrapperOptions(feature="chat"))
        """
        from .wrappers.anthropic import wrap_anthropic

        return wrap_anthropic(client, self, default_options)

    def wrap_google(
        self,
        client: T,
        default_options: Optional[WrapperOptions] = None,
    ) -> T:
        """
        Wrap a Google GenAI client for automatic tracking.

        Usage:
            from google import genai
            client = genai.Client(api_key="your-gemini-api-key")
            wrapped = orbit.wrap_google(client, WrapperOptions(feature="chat"))
        """
        from .wrappers.google import wrap_google

        return wrap_google(client, self, default_options)
