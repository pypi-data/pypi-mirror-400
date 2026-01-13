"""Custom library extensions - safe from Stainless regeneration."""

from .wrapper import ComputerSession
from .result_types import (
    ScreenshotResult,
    HTMLResult,
    DebugResult,
    get_screenshot_url,
    get_html_content,
    get_debug_response,
)

__all__ = [
    "ComputerSession",
    "ScreenshotResult",
    "HTMLResult",
    "DebugResult",
    "get_screenshot_url",
    "get_html_content",
    "get_debug_response",
]
