"""
Orbit SDK
Track, monitor, and optimize your AI spend

Usage:
    from withorbit_sdk import Orbit

    orbit = Orbit(api_key="orb_live_xxx")

    # Manual tracking
    orbit.track(
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        feature="chat-assistant",
    )

    # Or wrap your OpenAI/Anthropic client for automatic tracking
    from openai import OpenAI

    openai = orbit.wrap_openai(OpenAI())
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    # Usage automatically tracked!
"""

from .client import OrbitClient, Orbit
from .types import OrbitConfig, OrbitEvent, OrbitResponse, WrapperOptions

__version__ = "0.1.3"
__all__ = [
    "Orbit",
    "OrbitClient",
    "OrbitConfig",
    "OrbitEvent",
    "OrbitResponse",
    "WrapperOptions",
]
