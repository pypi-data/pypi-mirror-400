"""Lightweight wrapper for cleaner API - lives in lib/ to avoid Stainless regeneration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .._client import Computer as TzafonClient
    from ..types.action_result import ActionResult

__all__ = ["ComputerSession"]


class ComputerSession:
    """
    High-level session wrapper with cleaner API and context manager support.

    This wraps a computer instance and provides:
    - Automatic ID management (no need to pass computer_id to each call)
    - Context manager support for automatic cleanup
    - Simplified method signatures
    - Better IntelliSense through typed helper methods

    Example:
        ```python
        from tzafon import Computer

        client = Computer()
        with client.create(kind="browser") as computer:
            computer.navigate("https://example.com")
            result = computer.screenshot()
            url = computer.get_screenshot_url(result)
            # Automatically terminates on exit
        ```
    """

    def __init__(self, client: TzafonClient, computer_id: str) -> None:
        """
        Initialize session wrapper.

        Args:
            client: The Computer client instance
            computer_id: The computer/session ID
        """
        self._client = client
        self.id = computer_id

    def navigate(self, url: str) -> ActionResult:
        """
        Navigate to a URL.

        Args:
            url: The URL to navigate to (e.g., "https://example.com")

        Returns:
            ActionResult with status and timestamp
        """
        return self._client.computers.navigate(self.id, url=url)

    def type(self, text: str) -> ActionResult:
        """
        Type text into the currently focused element.

        Args:
            text: The text to type

        Returns:
            ActionResult with status and timestamp
        """
        return self._client.computers.type_text(self.id, text=text)

    def click(self, x: float, y: float) -> ActionResult:
        """
        Click at specific coordinates.

        Args:
            x: X coordinate (pixels from left)
            y: Y coordinate (pixels from top)

        Returns:
            ActionResult with status and timestamp
        """
        return self._client.computers.click(self.id, x=x, y=y)

    def screenshot(self, base64: bool = False) -> ActionResult:
        """
        Capture a screenshot of the current viewport.

        Args:
            base64: If True, return base64-encoded image data instead of URL

        Returns:
            ActionResult with result.screenshot_url containing the image URL.
            Use get_screenshot_url() helper to extract the URL with type safety.

        Example:
            ```python
            result = computer.screenshot()
            url = computer.get_screenshot_url(result)
            ```
        """
        return self._client.computers.capture_screenshot(self.id, base64=base64)

    def double_click(self, x: float, y: float) -> ActionResult:
        """
        Double-click at specific coordinates.

        Args:
            x: X coordinate (pixels from left)
            y: Y coordinate (pixels from top)

        Returns:
            ActionResult with status and timestamp
        """
        return self._client.computers.double_click(self.id, x=x, y=y)

    def right_click(self, x: float, y: float) -> ActionResult:
        """
        Right-click at specific coordinates.

        Args:
            x: X coordinate (pixels from left)
            y: Y coordinate (pixels from top)

        Returns:
            ActionResult with status and timestamp
        """
        return self._client.computers.right_click(self.id, x=x, y=y)

    def drag(self, x1: float, y1: float, x2: float, y2: float) -> ActionResult:
        """
        Perform click-and-drag from one point to another.

        Args:
            x1: Starting X coordinate
            y1: Starting Y coordinate
            x2: Ending X coordinate
            y2: Ending Y coordinate

        Returns:
            ActionResult with status and timestamp
        """
        return self._client.computers.drag(self.id, x1=x1, y1=y1, x2=x2, y2=y2)

    def hotkey(self, *keys: str) -> ActionResult:
        """
        Press a keyboard shortcut combination.

        Args:
            *keys: Keys to press together (e.g., "Control", "c" for Ctrl+C)
                  Can be passed as separate arguments or as a single list/tuple

        Returns:
            ActionResult with status and timestamp

        Example:
            ```python
            computer.hotkey("Control", "c")  # Copy - varargs style
            computer.hotkey(["Control", "v"])  # Paste - list style
            computer.hotkey("Control", "Shift", "p")  # Multiple modifiers
            ```
        """
        # Handle both hotkey("a", "b") and hotkey(["a", "b"]) calling styles
        if len(keys) == 1 and isinstance(keys[0], (list, tuple)):
            keys_list = list(keys[0])
        else:
            keys_list = list(keys)
        
        return self._client.computers.execute_action(self.id, action={"type": "keypress", "keys": keys_list})

    def scroll(self, dx: float = 0, dy: float = 0, x: float = 0, y: float = 0) -> ActionResult:
        """
        Scroll the viewport.

        Args:
            dx: Horizontal scroll delta (positive = right, negative = left)
            dy: Vertical scroll delta (positive = down, negative = up)
            x: Starting X coordinate for the scroll action
            y: Starting Y coordinate for the scroll action

        Returns:
            ActionResult with status and timestamp
        """
        return self._client.computers.scroll_viewport(self.id, dx=dx, dy=dy, x=x, y=y)

    def wait(self, seconds: float) -> ActionResult:
        """
        Wait for a specified number of seconds on the remote computer.

        Args:
            seconds: Number of seconds to wait (can be fractional, e.g., 0.5 for half a second)

        Returns:
            ActionResult with status and timestamp

        Example:
            ```python
            result = computer.wait(1)      # Wait 1 second
            result = computer.wait(0.5)    # Wait 500 milliseconds
            result = computer.wait(2.5)    # Wait 2.5 seconds
            ```
        """
        ms = int(seconds * 1000)
        return self._client.computers.execute_action(self.id, action={"type": "wait", "ms": ms})

    def html(self, auto_detect_encoding: bool = False) -> ActionResult:
        """
        Get the HTML content of the current page.

        Args:
            auto_detect_encoding: Automatically detect and handle character encoding

        Returns:
            ActionResult with result.html_content containing the page HTML.
            Use get_html_content() helper to extract the HTML with type safety.

        Example:
            ```python
            result = computer.html()
            html = computer.get_html_content(result)
            ```
        """
        return self._client.computers.get_html(self.id, auto_detect_encoding=auto_detect_encoding)

    def debug(self, command: str, timeout_seconds: int = 120, max_output_length: int = 65536) -> ActionResult:
        """
        Execute a shell command inside the session.

        Args:
            command: Shell command to execute
            timeout_seconds: Command timeout in seconds (default: 120)
            max_output_length: Maximum output length in bytes (default: 65536)

        Returns:
            ActionResult with result.debug_response containing command output.
            Use get_debug_response() helper to extract output with type safety.

        Example:
            ```python
            result = computer.debug("ls -la")
            output = computer.get_debug_response(result)
            ```
        """
        return self._client.computers.debug(
            self.id,
            command=command,
            timeout_seconds=timeout_seconds,
            max_output_length=max_output_length
        )

    def set_viewport(self, width: int, height: int, scale_factor: float = 1.0) -> ActionResult:
        """
        Change the browser viewport dimensions.

        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
            scale_factor: Device pixel ratio / zoom level (default: 1.0)

        Returns:
            ActionResult with status and timestamp
        """
        return self._client.computers.set_viewport(
            self.id,
            width=width,
            height=height,
            scale_factor=scale_factor
        )

    # Typed helper methods for extracting results

    def get_screenshot_url(self, result: ActionResult) -> Optional[str]:
        """
        Extract screenshot URL from action result with type safety.

        Args:
            result: ActionResult from screenshot() call

        Returns:
            Screenshot URL if available, None otherwise
        """
        if result.result:
            return result.result.get("screenshot_url")  # type: ignore
        return None

    def get_html_content(self, result: ActionResult) -> Optional[str]:
        """
        Extract HTML content from action result with type safety.

        Args:
            result: ActionResult from html() call

        Returns:
            HTML content if available, None otherwise
        """
        if result.result:
            return result.result.get("html_content")  # type: ignore
        return None

    def get_debug_response(self, result: ActionResult) -> Optional[str]:
        """
        Extract debug command output from action result with type safety.

        Args:
            result: ActionResult from debug() call

        Returns:
            Command output if available, None otherwise
        """
        if result.result:
            return result.result.get("debug_response")  # type: ignore
        return None

    def terminate(self) -> None:
        """
        Terminate the computer session and clean up resources.

        Note: When using the context manager (with statement), this is called automatically.
        """
        self._client.computers.terminate(self.id)

    def __enter__(self) -> ComputerSession:
        """Context manager entry - returns self for use in with statement."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - automatically terminates the session."""
        self.terminate()
