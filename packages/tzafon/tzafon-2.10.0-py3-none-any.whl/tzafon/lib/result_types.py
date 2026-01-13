"""Strongly-typed result helpers for better IntelliSense."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypedDict

if TYPE_CHECKING:
    from ..types.action_result import ActionResult

__all__ = [
    "ScreenshotResult",
    "HTMLResult",
    "DebugResult",
    "get_screenshot_url",
    "get_html_content",
    "get_debug_response",
]


class ScreenshotResult(TypedDict, total=False):
    """Result from screenshot action containing the image URL."""
    screenshot_url: str


class HTMLResult(TypedDict, total=False):
    """Result from html() action containing the page HTML."""
    html_content: str


class DebugResult(TypedDict, total=False):
    """Result from debug command containing command output."""
    debug_response: str


def get_screenshot_url(result: ActionResult) -> Optional[str]:
    """
    Extract screenshot URL from action result.

    Args:
        result: ActionResult from screenshot() call

    Returns:
        Screenshot URL if available, None otherwise
    """
    if result.result:
        return result.result.get("screenshot_url")  # type: ignore
    return None


def get_html_content(result: ActionResult) -> Optional[str]:
    """
    Extract HTML content from action result.

    Args:
        result: ActionResult from html() call

    Returns:
        HTML content if available, None otherwise
    """
    if result.result:
        return result.result.get("html_content")  # type: ignore
    return None


def get_debug_response(result: ActionResult) -> Optional[str]:
    """
    Extract debug command output from action result.

    Args:
        result: ActionResult from debug() call

    Returns:
        Command output if available, None otherwise
    """
    if result.result:
        return result.result.get("debug_response")  # type: ignore
    return None
