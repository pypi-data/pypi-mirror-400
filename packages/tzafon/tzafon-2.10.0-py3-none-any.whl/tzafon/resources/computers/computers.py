# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from .tabs import (
    TabsResource,
    AsyncTabsResource,
    TabsResourceWithRawResponse,
    AsyncTabsResourceWithRawResponse,
    TabsResourceWithStreamingResponse,
    AsyncTabsResourceWithStreamingResponse,
)
from ...types import (
    computer_drag_params,
    computer_click_params,
    computer_debug_params,
    computer_create_params,
    computer_key_up_params,
    computer_get_html_params,
    computer_key_down_params,
    computer_mouse_up_params,
    computer_navigate_params,
    computer_type_text_params,
    computer_mouse_down_params,
    computer_right_click_params,
    computer_double_click_params,
    computer_press_hotkey_params,
    computer_set_viewport_params,
    computer_execute_batch_params,
    computer_execute_action_params,
    computer_scroll_viewport_params,
    computer_capture_screenshot_params,
)
from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.computer_drag_response import ComputerDragResponse
from ...types.computer_list_response import ComputerListResponse
from ...types.computer_click_response import ComputerClickResponse
from ...types.computer_debug_response import ComputerDebugResponse
from ...types.computer_create_response import ComputerCreateResponse
from ...types.computer_key_up_response import ComputerKeyUpResponse
from ...types.computer_get_html_response import ComputerGetHTMLResponse
from ...types.computer_key_down_response import ComputerKeyDownResponse
from ...types.computer_mouse_up_response import ComputerMouseUpResponse
from ...types.computer_navigate_response import ComputerNavigateResponse
from ...types.computer_retrieve_response import ComputerRetrieveResponse
from ...types.computer_type_text_response import ComputerTypeTextResponse
from ...types.computer_keep_alive_response import ComputerKeepAliveResponse
from ...types.computer_mouse_down_response import ComputerMouseDownResponse
from ...types.computer_right_click_response import ComputerRightClickResponse
from ...types.computer_double_click_response import ComputerDoubleClickResponse
from ...types.computer_press_hotkey_response import ComputerPressHotkeyResponse
from ...types.computer_set_viewport_response import ComputerSetViewportResponse
from ...types.computer_execute_batch_response import ComputerExecuteBatchResponse
from ...types.computer_execute_action_response import ComputerExecuteActionResponse
from ...types.computer_scroll_viewport_response import ComputerScrollViewportResponse
from ...types.computer_capture_screenshot_response import ComputerCaptureScreenshotResponse

__all__ = ["ComputersResource", "AsyncComputersResource"]


class ComputersResource(SyncAPIResource):
    @cached_property
    def tabs(self) -> TabsResource:
        return TabsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ComputersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/tzafon/computer-python#accessing-raw-response-data-eg-headers
        """
        return ComputersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ComputersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/tzafon/computer-python#with_streaming_response
        """
        return ComputersResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        auto_kill: bool | Omit = omit,
        context_id: str | Omit = omit,
        display: computer_create_params.Display | Omit = omit,
        kind: str | Omit = omit,
        stealth: object | Omit = omit,
        timeout_seconds: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerCreateResponse:
        """Create a new automation session.

        Set kind to "browser" for web automation or
        "desktop" for OS-level automation. Defaults to "browser" if not specified.

        Args:
          auto_kill: If true (default), kill session after inactivity

          kind: "browser" (default) or "desktop"

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/computers",
            body=maybe_transform(
                {
                    "auto_kill": auto_kill,
                    "context_id": context_id,
                    "display": display,
                    "kind": kind,
                    "stealth": stealth,
                    "timeout_seconds": timeout_seconds,
                },
                computer_create_params.ComputerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerRetrieveResponse:
        """
        Get the current status and metadata of a computer instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/computers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerRetrieveResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerListResponse:
        """List all active computers for the user's organization"""
        return self._get(
            "/computers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerListResponse,
        )

    def capture_screenshot(
        self,
        id: str,
        *,
        base64: bool | Omit = omit,
        tab_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerCaptureScreenshotResponse:
        """
        Take a screenshot of the current browser viewport, optionally as base64.
        Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/screenshot",
            body=maybe_transform(
                {
                    "base64": base64,
                    "tab_id": tab_id,
                },
                computer_capture_screenshot_params.ComputerCaptureScreenshotParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerCaptureScreenshotResponse,
        )

    def click(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerClickResponse:
        """Perform a left mouse click at the specified x,y coordinates.

        Coordinates are
        screenshot pixel positions - send exactly what you see in the
        screenshot/screencast image. If target is at pixel (500, 300) in the image, send
        x=500, y=300. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/click",
            body=maybe_transform(
                {
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_click_params.ComputerClickParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerClickResponse,
        )

    def connect_websocket(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Establish WebSocket for real-time bidirectional communication

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/computers/{id}/ws",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def debug(
        self,
        id: str,
        *,
        command: str | Omit = omit,
        max_output_length: int | Omit = omit,
        tab_id: str | Omit = omit,
        timeout_seconds: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerDebugResponse:
        """
        Execute a shell command with optional timeout and output length limits.
        Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/debug",
            body=maybe_transform(
                {
                    "command": command,
                    "max_output_length": max_output_length,
                    "tab_id": tab_id,
                    "timeout_seconds": timeout_seconds,
                },
                computer_debug_params.ComputerDebugParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerDebugResponse,
        )

    def double_click(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerDoubleClickResponse:
        """Perform a double mouse click at the specified x,y coordinates.

        Coordinates are
        screenshot pixel positions. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/double-click",
            body=maybe_transform(
                {
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_double_click_params.ComputerDoubleClickParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerDoubleClickResponse,
        )

    def drag(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x1: float | Omit = omit,
        x2: float | Omit = omit,
        y1: float | Omit = omit,
        y2: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerDragResponse:
        """Perform a click-and-drag action from (x1,y1) to (x2,y2).

        Coordinates are
        screenshot pixel positions. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/drag",
            body=maybe_transform(
                {
                    "tab_id": tab_id,
                    "x1": x1,
                    "x2": x2,
                    "y1": y1,
                    "y2": y2,
                },
                computer_drag_params.ComputerDragParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerDragResponse,
        )

    def execute_action(
        self,
        id: str,
        *,
        action: computer_execute_action_params.Action | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerExecuteActionResponse:
        """
        Execute a single action such as screenshot, click, type, navigate, scroll,
        debug, set_viewport, get_html_content or other computer use actions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/execute",
            body=maybe_transform({"action": action}, computer_execute_action_params.ComputerExecuteActionParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerExecuteActionResponse,
        )

    def execute_batch(
        self,
        id: str,
        *,
        actions: Iterable[computer_execute_batch_params.Action] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerExecuteBatchResponse:
        """
        Execute a batch of actions in sequence, stopping on first error

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/batch",
            body=maybe_transform({"actions": actions}, computer_execute_batch_params.ComputerExecuteBatchParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerExecuteBatchResponse,
        )

    def get_html(
        self,
        id: str,
        *,
        auto_detect_encoding: bool | Omit = omit,
        tab_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerGetHTMLResponse:
        """Get the HTML content of the current browser page.

        Optionally specify tab_id
        (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/html",
            body=maybe_transform(
                {
                    "auto_detect_encoding": auto_detect_encoding,
                    "tab_id": tab_id,
                },
                computer_get_html_params.ComputerGetHTMLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerGetHTMLResponse,
        )

    def keep_alive(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerKeepAliveResponse:
        """
        Extend the timeout for a computer session and verify it is still running

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/keepalive",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerKeepAliveResponse,
        )

    def key_down(
        self,
        id: str,
        *,
        key: str | Omit = omit,
        tab_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerKeyDownResponse:
        """Press and hold a keyboard key.

        Use with key_up for complex interactions.
        Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/key-down",
            body=maybe_transform(
                {
                    "key": key,
                    "tab_id": tab_id,
                },
                computer_key_down_params.ComputerKeyDownParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerKeyDownResponse,
        )

    def key_up(
        self,
        id: str,
        *,
        key: str | Omit = omit,
        tab_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerKeyUpResponse:
        """Release a keyboard key that was previously pressed with key_down.

        Optionally
        specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/key-up",
            body=maybe_transform(
                {
                    "key": key,
                    "tab_id": tab_id,
                },
                computer_key_up_params.ComputerKeyUpParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerKeyUpResponse,
        )

    def mouse_down(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerMouseDownResponse:
        """
        Press and hold the left mouse button at the specified x,y coordinates.
        Coordinates are screenshot pixel positions. Optionally specify tab_id (browser
        sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/mouse-down",
            body=maybe_transform(
                {
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_mouse_down_params.ComputerMouseDownParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerMouseDownResponse,
        )

    def mouse_up(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerMouseUpResponse:
        """Release the left mouse button at the specified x,y coordinates.

        Coordinates are
        screenshot pixel positions. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/mouse-up",
            body=maybe_transform(
                {
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_mouse_up_params.ComputerMouseUpParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerMouseUpResponse,
        )

    def navigate(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerNavigateResponse:
        """Navigate the browser to a specified URL.

        Optionally specify tab_id to navigate a
        specific tab (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/navigate",
            body=maybe_transform(
                {
                    "tab_id": tab_id,
                    "url": url,
                },
                computer_navigate_params.ComputerNavigateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerNavigateResponse,
        )

    def press_hotkey(
        self,
        id: str,
        *,
        keys: SequenceNotStr[str] | Omit = omit,
        tab_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerPressHotkeyResponse:
        """Press a combination of keys (e.g., ["Control", "c"] for copy).

        Optionally
        specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/hotkey",
            body=maybe_transform(
                {
                    "keys": keys,
                    "tab_id": tab_id,
                },
                computer_press_hotkey_params.ComputerPressHotkeyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerPressHotkeyResponse,
        )

    def right_click(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerRightClickResponse:
        """Perform a right mouse click at the specified x,y coordinates.

        Coordinates are
        screenshot pixel positions. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/right-click",
            body=maybe_transform(
                {
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_right_click_params.ComputerRightClickParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerRightClickResponse,
        )

    def scroll_viewport(
        self,
        id: str,
        *,
        dx: float | Omit = omit,
        dy: float | Omit = omit,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerScrollViewportResponse:
        """Scroll at the specified x,y position by delta dx,dy.

        Coordinates are screenshot
        pixel positions. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/scroll",
            body=maybe_transform(
                {
                    "dx": dx,
                    "dy": dy,
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_scroll_viewport_params.ComputerScrollViewportParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerScrollViewportResponse,
        )

    def set_viewport(
        self,
        id: str,
        *,
        height: int | Omit = omit,
        scale_factor: float | Omit = omit,
        tab_id: str | Omit = omit,
        width: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerSetViewportResponse:
        """Change the browser viewport dimensions and scale factor.

        Optionally specify
        tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/viewport",
            body=maybe_transform(
                {
                    "height": height,
                    "scale_factor": scale_factor,
                    "tab_id": tab_id,
                    "width": width,
                },
                computer_set_viewport_params.ComputerSetViewportParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerSetViewportResponse,
        )

    def stream_events(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Stream real-time events using Server-Sent Events (SSE)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/computers/{id}/events",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def stream_screencast(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Stream only screencast frames (base64 JPEG images) using Server-Sent Events
        (SSE) for live browser viewing

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/computers/{id}/screencast",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def terminate(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Terminate and clean up a computer instance, stopping the session and recording
        metrics

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/computers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def type_text(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        text: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerTypeTextResponse:
        """Type text into the currently focused element in the browser.

        Optionally specify
        tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/computers/{id}/type",
            body=maybe_transform(
                {
                    "tab_id": tab_id,
                    "text": text,
                },
                computer_type_text_params.ComputerTypeTextParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerTypeTextResponse,
        )


class AsyncComputersResource(AsyncAPIResource):
    @cached_property
    def tabs(self) -> AsyncTabsResource:
        return AsyncTabsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncComputersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/tzafon/computer-python#accessing-raw-response-data-eg-headers
        """
        return AsyncComputersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncComputersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/tzafon/computer-python#with_streaming_response
        """
        return AsyncComputersResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        auto_kill: bool | Omit = omit,
        context_id: str | Omit = omit,
        display: computer_create_params.Display | Omit = omit,
        kind: str | Omit = omit,
        stealth: object | Omit = omit,
        timeout_seconds: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerCreateResponse:
        """Create a new automation session.

        Set kind to "browser" for web automation or
        "desktop" for OS-level automation. Defaults to "browser" if not specified.

        Args:
          auto_kill: If true (default), kill session after inactivity

          kind: "browser" (default) or "desktop"

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/computers",
            body=await async_maybe_transform(
                {
                    "auto_kill": auto_kill,
                    "context_id": context_id,
                    "display": display,
                    "kind": kind,
                    "stealth": stealth,
                    "timeout_seconds": timeout_seconds,
                },
                computer_create_params.ComputerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerRetrieveResponse:
        """
        Get the current status and metadata of a computer instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/computers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerRetrieveResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerListResponse:
        """List all active computers for the user's organization"""
        return await self._get(
            "/computers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerListResponse,
        )

    async def capture_screenshot(
        self,
        id: str,
        *,
        base64: bool | Omit = omit,
        tab_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerCaptureScreenshotResponse:
        """
        Take a screenshot of the current browser viewport, optionally as base64.
        Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/screenshot",
            body=await async_maybe_transform(
                {
                    "base64": base64,
                    "tab_id": tab_id,
                },
                computer_capture_screenshot_params.ComputerCaptureScreenshotParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerCaptureScreenshotResponse,
        )

    async def click(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerClickResponse:
        """Perform a left mouse click at the specified x,y coordinates.

        Coordinates are
        screenshot pixel positions - send exactly what you see in the
        screenshot/screencast image. If target is at pixel (500, 300) in the image, send
        x=500, y=300. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/click",
            body=await async_maybe_transform(
                {
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_click_params.ComputerClickParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerClickResponse,
        )

    async def connect_websocket(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Establish WebSocket for real-time bidirectional communication

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/computers/{id}/ws",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def debug(
        self,
        id: str,
        *,
        command: str | Omit = omit,
        max_output_length: int | Omit = omit,
        tab_id: str | Omit = omit,
        timeout_seconds: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerDebugResponse:
        """
        Execute a shell command with optional timeout and output length limits.
        Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/debug",
            body=await async_maybe_transform(
                {
                    "command": command,
                    "max_output_length": max_output_length,
                    "tab_id": tab_id,
                    "timeout_seconds": timeout_seconds,
                },
                computer_debug_params.ComputerDebugParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerDebugResponse,
        )

    async def double_click(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerDoubleClickResponse:
        """Perform a double mouse click at the specified x,y coordinates.

        Coordinates are
        screenshot pixel positions. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/double-click",
            body=await async_maybe_transform(
                {
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_double_click_params.ComputerDoubleClickParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerDoubleClickResponse,
        )

    async def drag(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x1: float | Omit = omit,
        x2: float | Omit = omit,
        y1: float | Omit = omit,
        y2: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerDragResponse:
        """Perform a click-and-drag action from (x1,y1) to (x2,y2).

        Coordinates are
        screenshot pixel positions. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/drag",
            body=await async_maybe_transform(
                {
                    "tab_id": tab_id,
                    "x1": x1,
                    "x2": x2,
                    "y1": y1,
                    "y2": y2,
                },
                computer_drag_params.ComputerDragParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerDragResponse,
        )

    async def execute_action(
        self,
        id: str,
        *,
        action: computer_execute_action_params.Action | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerExecuteActionResponse:
        """
        Execute a single action such as screenshot, click, type, navigate, scroll,
        debug, set_viewport, get_html_content or other computer use actions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/execute",
            body=await async_maybe_transform(
                {"action": action}, computer_execute_action_params.ComputerExecuteActionParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerExecuteActionResponse,
        )

    async def execute_batch(
        self,
        id: str,
        *,
        actions: Iterable[computer_execute_batch_params.Action] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerExecuteBatchResponse:
        """
        Execute a batch of actions in sequence, stopping on first error

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/batch",
            body=await async_maybe_transform(
                {"actions": actions}, computer_execute_batch_params.ComputerExecuteBatchParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerExecuteBatchResponse,
        )

    async def get_html(
        self,
        id: str,
        *,
        auto_detect_encoding: bool | Omit = omit,
        tab_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerGetHTMLResponse:
        """Get the HTML content of the current browser page.

        Optionally specify tab_id
        (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/html",
            body=await async_maybe_transform(
                {
                    "auto_detect_encoding": auto_detect_encoding,
                    "tab_id": tab_id,
                },
                computer_get_html_params.ComputerGetHTMLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerGetHTMLResponse,
        )

    async def keep_alive(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerKeepAliveResponse:
        """
        Extend the timeout for a computer session and verify it is still running

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/keepalive",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerKeepAliveResponse,
        )

    async def key_down(
        self,
        id: str,
        *,
        key: str | Omit = omit,
        tab_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerKeyDownResponse:
        """Press and hold a keyboard key.

        Use with key_up for complex interactions.
        Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/key-down",
            body=await async_maybe_transform(
                {
                    "key": key,
                    "tab_id": tab_id,
                },
                computer_key_down_params.ComputerKeyDownParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerKeyDownResponse,
        )

    async def key_up(
        self,
        id: str,
        *,
        key: str | Omit = omit,
        tab_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerKeyUpResponse:
        """Release a keyboard key that was previously pressed with key_down.

        Optionally
        specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/key-up",
            body=await async_maybe_transform(
                {
                    "key": key,
                    "tab_id": tab_id,
                },
                computer_key_up_params.ComputerKeyUpParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerKeyUpResponse,
        )

    async def mouse_down(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerMouseDownResponse:
        """
        Press and hold the left mouse button at the specified x,y coordinates.
        Coordinates are screenshot pixel positions. Optionally specify tab_id (browser
        sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/mouse-down",
            body=await async_maybe_transform(
                {
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_mouse_down_params.ComputerMouseDownParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerMouseDownResponse,
        )

    async def mouse_up(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerMouseUpResponse:
        """Release the left mouse button at the specified x,y coordinates.

        Coordinates are
        screenshot pixel positions. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/mouse-up",
            body=await async_maybe_transform(
                {
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_mouse_up_params.ComputerMouseUpParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerMouseUpResponse,
        )

    async def navigate(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerNavigateResponse:
        """Navigate the browser to a specified URL.

        Optionally specify tab_id to navigate a
        specific tab (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/navigate",
            body=await async_maybe_transform(
                {
                    "tab_id": tab_id,
                    "url": url,
                },
                computer_navigate_params.ComputerNavigateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerNavigateResponse,
        )

    async def press_hotkey(
        self,
        id: str,
        *,
        keys: SequenceNotStr[str] | Omit = omit,
        tab_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerPressHotkeyResponse:
        """Press a combination of keys (e.g., ["Control", "c"] for copy).

        Optionally
        specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/hotkey",
            body=await async_maybe_transform(
                {
                    "keys": keys,
                    "tab_id": tab_id,
                },
                computer_press_hotkey_params.ComputerPressHotkeyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerPressHotkeyResponse,
        )

    async def right_click(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerRightClickResponse:
        """Perform a right mouse click at the specified x,y coordinates.

        Coordinates are
        screenshot pixel positions. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/right-click",
            body=await async_maybe_transform(
                {
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_right_click_params.ComputerRightClickParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerRightClickResponse,
        )

    async def scroll_viewport(
        self,
        id: str,
        *,
        dx: float | Omit = omit,
        dy: float | Omit = omit,
        tab_id: str | Omit = omit,
        x: float | Omit = omit,
        y: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerScrollViewportResponse:
        """Scroll at the specified x,y position by delta dx,dy.

        Coordinates are screenshot
        pixel positions. Optionally specify tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/scroll",
            body=await async_maybe_transform(
                {
                    "dx": dx,
                    "dy": dy,
                    "tab_id": tab_id,
                    "x": x,
                    "y": y,
                },
                computer_scroll_viewport_params.ComputerScrollViewportParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerScrollViewportResponse,
        )

    async def set_viewport(
        self,
        id: str,
        *,
        height: int | Omit = omit,
        scale_factor: float | Omit = omit,
        tab_id: str | Omit = omit,
        width: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerSetViewportResponse:
        """Change the browser viewport dimensions and scale factor.

        Optionally specify
        tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/viewport",
            body=await async_maybe_transform(
                {
                    "height": height,
                    "scale_factor": scale_factor,
                    "tab_id": tab_id,
                    "width": width,
                },
                computer_set_viewport_params.ComputerSetViewportParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerSetViewportResponse,
        )

    async def stream_events(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Stream real-time events using Server-Sent Events (SSE)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/computers/{id}/events",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def stream_screencast(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Stream only screencast frames (base64 JPEG images) using Server-Sent Events
        (SSE) for live browser viewing

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/computers/{id}/screencast",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def terminate(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Terminate and clean up a computer instance, stopping the session and recording
        metrics

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/computers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def type_text(
        self,
        id: str,
        *,
        tab_id: str | Omit = omit,
        text: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ComputerTypeTextResponse:
        """Type text into the currently focused element in the browser.

        Optionally specify
        tab_id (browser sessions only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/computers/{id}/type",
            body=await async_maybe_transform(
                {
                    "tab_id": tab_id,
                    "text": text,
                },
                computer_type_text_params.ComputerTypeTextParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ComputerTypeTextResponse,
        )


class ComputersResourceWithRawResponse:
    def __init__(self, computers: ComputersResource) -> None:
        self._computers = computers

        self.create = to_raw_response_wrapper(
            computers.create,
        )
        self.retrieve = to_raw_response_wrapper(
            computers.retrieve,
        )
        self.list = to_raw_response_wrapper(
            computers.list,
        )
        self.capture_screenshot = to_raw_response_wrapper(
            computers.capture_screenshot,
        )
        self.click = to_raw_response_wrapper(
            computers.click,
        )
        self.connect_websocket = to_raw_response_wrapper(
            computers.connect_websocket,
        )
        self.debug = to_raw_response_wrapper(
            computers.debug,
        )
        self.double_click = to_raw_response_wrapper(
            computers.double_click,
        )
        self.drag = to_raw_response_wrapper(
            computers.drag,
        )
        self.execute_action = to_raw_response_wrapper(
            computers.execute_action,
        )
        self.execute_batch = to_raw_response_wrapper(
            computers.execute_batch,
        )
        self.get_html = to_raw_response_wrapper(
            computers.get_html,
        )
        self.keep_alive = to_raw_response_wrapper(
            computers.keep_alive,
        )
        self.key_down = to_raw_response_wrapper(
            computers.key_down,
        )
        self.key_up = to_raw_response_wrapper(
            computers.key_up,
        )
        self.mouse_down = to_raw_response_wrapper(
            computers.mouse_down,
        )
        self.mouse_up = to_raw_response_wrapper(
            computers.mouse_up,
        )
        self.navigate = to_raw_response_wrapper(
            computers.navigate,
        )
        self.press_hotkey = to_raw_response_wrapper(
            computers.press_hotkey,
        )
        self.right_click = to_raw_response_wrapper(
            computers.right_click,
        )
        self.scroll_viewport = to_raw_response_wrapper(
            computers.scroll_viewport,
        )
        self.set_viewport = to_raw_response_wrapper(
            computers.set_viewport,
        )
        self.stream_events = to_raw_response_wrapper(
            computers.stream_events,
        )
        self.stream_screencast = to_raw_response_wrapper(
            computers.stream_screencast,
        )
        self.terminate = to_raw_response_wrapper(
            computers.terminate,
        )
        self.type_text = to_raw_response_wrapper(
            computers.type_text,
        )

    @cached_property
    def tabs(self) -> TabsResourceWithRawResponse:
        return TabsResourceWithRawResponse(self._computers.tabs)


class AsyncComputersResourceWithRawResponse:
    def __init__(self, computers: AsyncComputersResource) -> None:
        self._computers = computers

        self.create = async_to_raw_response_wrapper(
            computers.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            computers.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            computers.list,
        )
        self.capture_screenshot = async_to_raw_response_wrapper(
            computers.capture_screenshot,
        )
        self.click = async_to_raw_response_wrapper(
            computers.click,
        )
        self.connect_websocket = async_to_raw_response_wrapper(
            computers.connect_websocket,
        )
        self.debug = async_to_raw_response_wrapper(
            computers.debug,
        )
        self.double_click = async_to_raw_response_wrapper(
            computers.double_click,
        )
        self.drag = async_to_raw_response_wrapper(
            computers.drag,
        )
        self.execute_action = async_to_raw_response_wrapper(
            computers.execute_action,
        )
        self.execute_batch = async_to_raw_response_wrapper(
            computers.execute_batch,
        )
        self.get_html = async_to_raw_response_wrapper(
            computers.get_html,
        )
        self.keep_alive = async_to_raw_response_wrapper(
            computers.keep_alive,
        )
        self.key_down = async_to_raw_response_wrapper(
            computers.key_down,
        )
        self.key_up = async_to_raw_response_wrapper(
            computers.key_up,
        )
        self.mouse_down = async_to_raw_response_wrapper(
            computers.mouse_down,
        )
        self.mouse_up = async_to_raw_response_wrapper(
            computers.mouse_up,
        )
        self.navigate = async_to_raw_response_wrapper(
            computers.navigate,
        )
        self.press_hotkey = async_to_raw_response_wrapper(
            computers.press_hotkey,
        )
        self.right_click = async_to_raw_response_wrapper(
            computers.right_click,
        )
        self.scroll_viewport = async_to_raw_response_wrapper(
            computers.scroll_viewport,
        )
        self.set_viewport = async_to_raw_response_wrapper(
            computers.set_viewport,
        )
        self.stream_events = async_to_raw_response_wrapper(
            computers.stream_events,
        )
        self.stream_screencast = async_to_raw_response_wrapper(
            computers.stream_screencast,
        )
        self.terminate = async_to_raw_response_wrapper(
            computers.terminate,
        )
        self.type_text = async_to_raw_response_wrapper(
            computers.type_text,
        )

    @cached_property
    def tabs(self) -> AsyncTabsResourceWithRawResponse:
        return AsyncTabsResourceWithRawResponse(self._computers.tabs)


class ComputersResourceWithStreamingResponse:
    def __init__(self, computers: ComputersResource) -> None:
        self._computers = computers

        self.create = to_streamed_response_wrapper(
            computers.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            computers.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            computers.list,
        )
        self.capture_screenshot = to_streamed_response_wrapper(
            computers.capture_screenshot,
        )
        self.click = to_streamed_response_wrapper(
            computers.click,
        )
        self.connect_websocket = to_streamed_response_wrapper(
            computers.connect_websocket,
        )
        self.debug = to_streamed_response_wrapper(
            computers.debug,
        )
        self.double_click = to_streamed_response_wrapper(
            computers.double_click,
        )
        self.drag = to_streamed_response_wrapper(
            computers.drag,
        )
        self.execute_action = to_streamed_response_wrapper(
            computers.execute_action,
        )
        self.execute_batch = to_streamed_response_wrapper(
            computers.execute_batch,
        )
        self.get_html = to_streamed_response_wrapper(
            computers.get_html,
        )
        self.keep_alive = to_streamed_response_wrapper(
            computers.keep_alive,
        )
        self.key_down = to_streamed_response_wrapper(
            computers.key_down,
        )
        self.key_up = to_streamed_response_wrapper(
            computers.key_up,
        )
        self.mouse_down = to_streamed_response_wrapper(
            computers.mouse_down,
        )
        self.mouse_up = to_streamed_response_wrapper(
            computers.mouse_up,
        )
        self.navigate = to_streamed_response_wrapper(
            computers.navigate,
        )
        self.press_hotkey = to_streamed_response_wrapper(
            computers.press_hotkey,
        )
        self.right_click = to_streamed_response_wrapper(
            computers.right_click,
        )
        self.scroll_viewport = to_streamed_response_wrapper(
            computers.scroll_viewport,
        )
        self.set_viewport = to_streamed_response_wrapper(
            computers.set_viewport,
        )
        self.stream_events = to_streamed_response_wrapper(
            computers.stream_events,
        )
        self.stream_screencast = to_streamed_response_wrapper(
            computers.stream_screencast,
        )
        self.terminate = to_streamed_response_wrapper(
            computers.terminate,
        )
        self.type_text = to_streamed_response_wrapper(
            computers.type_text,
        )

    @cached_property
    def tabs(self) -> TabsResourceWithStreamingResponse:
        return TabsResourceWithStreamingResponse(self._computers.tabs)


class AsyncComputersResourceWithStreamingResponse:
    def __init__(self, computers: AsyncComputersResource) -> None:
        self._computers = computers

        self.create = async_to_streamed_response_wrapper(
            computers.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            computers.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            computers.list,
        )
        self.capture_screenshot = async_to_streamed_response_wrapper(
            computers.capture_screenshot,
        )
        self.click = async_to_streamed_response_wrapper(
            computers.click,
        )
        self.connect_websocket = async_to_streamed_response_wrapper(
            computers.connect_websocket,
        )
        self.debug = async_to_streamed_response_wrapper(
            computers.debug,
        )
        self.double_click = async_to_streamed_response_wrapper(
            computers.double_click,
        )
        self.drag = async_to_streamed_response_wrapper(
            computers.drag,
        )
        self.execute_action = async_to_streamed_response_wrapper(
            computers.execute_action,
        )
        self.execute_batch = async_to_streamed_response_wrapper(
            computers.execute_batch,
        )
        self.get_html = async_to_streamed_response_wrapper(
            computers.get_html,
        )
        self.keep_alive = async_to_streamed_response_wrapper(
            computers.keep_alive,
        )
        self.key_down = async_to_streamed_response_wrapper(
            computers.key_down,
        )
        self.key_up = async_to_streamed_response_wrapper(
            computers.key_up,
        )
        self.mouse_down = async_to_streamed_response_wrapper(
            computers.mouse_down,
        )
        self.mouse_up = async_to_streamed_response_wrapper(
            computers.mouse_up,
        )
        self.navigate = async_to_streamed_response_wrapper(
            computers.navigate,
        )
        self.press_hotkey = async_to_streamed_response_wrapper(
            computers.press_hotkey,
        )
        self.right_click = async_to_streamed_response_wrapper(
            computers.right_click,
        )
        self.scroll_viewport = async_to_streamed_response_wrapper(
            computers.scroll_viewport,
        )
        self.set_viewport = async_to_streamed_response_wrapper(
            computers.set_viewport,
        )
        self.stream_events = async_to_streamed_response_wrapper(
            computers.stream_events,
        )
        self.stream_screencast = async_to_streamed_response_wrapper(
            computers.stream_screencast,
        )
        self.terminate = async_to_streamed_response_wrapper(
            computers.terminate,
        )
        self.type_text = async_to_streamed_response_wrapper(
            computers.type_text,
        )

    @cached_property
    def tabs(self) -> AsyncTabsResourceWithStreamingResponse:
        return AsyncTabsResourceWithStreamingResponse(self._computers.tabs)
