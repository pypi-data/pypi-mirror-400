"""
Orbit SDK Types
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional
from datetime import datetime


@dataclass
class OrbitConfig:
    """Configuration for initializing the SDK."""

    api_key: str
    """Your Orbit API key (orb_live_xxx or orb_test_xxx)"""

    base_url: str = "https://app.withorbit.io/api/v1"
    """Base URL for the Orbit API"""

    default_feature: Optional[str] = None
    """Default feature name to use for all events"""

    default_environment: Literal["production", "staging", "development"] = "production"
    """Default environment"""

    debug: bool = False
    """Enable debug logging"""

    batch_events: bool = True
    """Batch events before sending"""

    batch_size: int = 10
    """Maximum number of events to batch before sending"""

    batch_interval: float = 5.0
    """Maximum time (seconds) to wait before sending batched events"""

    retry: bool = True
    """Retry failed requests"""

    max_retries: int = 3
    """Maximum number of retries"""


@dataclass
class OrbitEvent:
    """Event sent to Orbit API."""

    model: str
    """Model name (e.g., 'gpt-4o', 'claude-3-opus')"""

    input_tokens: int
    """Number of input tokens"""

    output_tokens: int
    """Number of output tokens"""

    provider: Optional[str] = None
    """Provider name (auto-detected if not provided)"""

    latency_ms: Optional[int] = None
    """Latency in milliseconds"""

    timestamp: Optional[str] = None
    """ISO timestamp (defaults to now)"""

    feature: Optional[str] = None
    """Feature name for attribution"""

    environment: Optional[Literal["production", "staging", "development"]] = None
    """Environment"""

    status: Literal["success", "error", "timeout"] = "success"
    """Request status"""

    error_type: Optional[str] = None
    """Error type (if status is error)"""

    error_message: Optional[str] = None
    """Error message (if status is error)"""

    user_id: Optional[str] = None
    """Your application's user ID"""

    session_id: Optional[str] = None
    """Session ID"""

    request_id: Optional[str] = None
    """Unique request ID"""

    metadata: Optional[Dict[str, Any]] = None
    """Additional metadata"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data: Dict[str, Any] = {
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }

        if self.provider:
            data["provider"] = self.provider
        if self.latency_ms is not None:
            data["latency_ms"] = self.latency_ms
        if self.timestamp:
            data["timestamp"] = self.timestamp
        if self.feature:
            data["feature"] = self.feature
        if self.environment:
            data["environment"] = self.environment
        if self.status:
            data["status"] = self.status
        if self.error_type:
            data["error_type"] = self.error_type
        if self.error_message:
            data["error_message"] = self.error_message
        if self.user_id:
            data["user_id"] = self.user_id
        if self.session_id:
            data["session_id"] = self.session_id
        if self.request_id:
            data["request_id"] = self.request_id
        if self.metadata:
            data["metadata"] = self.metadata

        return data


@dataclass
class OrbitResponse:
    """Response from Orbit API."""

    success: bool
    received: int
    total_tokens: int
    total_cost_usd: float
    message: str


@dataclass
class WrapperOptions:
    """Options for wrapping OpenAI/Anthropic clients."""

    feature: Optional[str] = None
    """Feature name to attribute requests to"""

    environment: Optional[Literal["production", "staging", "development"]] = None
    """Environment for requests"""

    user_id: Optional[str] = None
    """Your application's user ID"""

    session_id: Optional[str] = None
    """Session ID"""

    metadata: Optional[Dict[str, Any]] = None
    """Additional metadata"""
