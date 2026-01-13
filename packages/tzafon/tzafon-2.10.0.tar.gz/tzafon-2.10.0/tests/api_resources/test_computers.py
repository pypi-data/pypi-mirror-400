# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tzafon import Computer, AsyncComputer
from tests.utils import assert_matches_type
from tzafon.types import (
    ComputerDragResponse,
    ComputerListResponse,
    ComputerClickResponse,
    ComputerDebugResponse,
    ComputerKeyUpResponse,
    ComputerCreateResponse,
    ComputerGetHTMLResponse,
    ComputerKeyDownResponse,
    ComputerMouseUpResponse,
    ComputerNavigateResponse,
    ComputerRetrieveResponse,
    ComputerTypeTextResponse,
    ComputerKeepAliveResponse,
    ComputerMouseDownResponse,
    ComputerRightClickResponse,
    ComputerDoubleClickResponse,
    ComputerPressHotkeyResponse,
    ComputerSetViewportResponse,
    ComputerExecuteBatchResponse,
    ComputerExecuteActionResponse,
    ComputerScrollViewportResponse,
    ComputerCaptureScreenshotResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestComputers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Computer) -> None:
        computer = client.computers.create()
        assert_matches_type(ComputerCreateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Computer) -> None:
        computer = client.computers.create(
            auto_kill=True,
            context_id="context_id",
            display={
                "height": 0,
                "scale": 0,
                "width": 0,
            },
            kind="kind",
            stealth={},
            timeout_seconds=0,
        )
        assert_matches_type(ComputerCreateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Computer) -> None:
        response = client.computers.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerCreateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Computer) -> None:
        with client.computers.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerCreateResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Computer) -> None:
        computer = client.computers.retrieve(
            "id",
        )
        assert_matches_type(ComputerRetrieveResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Computer) -> None:
        response = client.computers.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerRetrieveResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Computer) -> None:
        with client.computers.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerRetrieveResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Computer) -> None:
        computer = client.computers.list()
        assert_matches_type(ComputerListResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Computer) -> None:
        response = client.computers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerListResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Computer) -> None:
        with client.computers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerListResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_capture_screenshot(self, client: Computer) -> None:
        computer = client.computers.capture_screenshot(
            id="id",
        )
        assert_matches_type(ComputerCaptureScreenshotResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_capture_screenshot_with_all_params(self, client: Computer) -> None:
        computer = client.computers.capture_screenshot(
            id="id",
            base64=True,
            tab_id="tab_id",
        )
        assert_matches_type(ComputerCaptureScreenshotResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_capture_screenshot(self, client: Computer) -> None:
        response = client.computers.with_raw_response.capture_screenshot(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerCaptureScreenshotResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_capture_screenshot(self, client: Computer) -> None:
        with client.computers.with_streaming_response.capture_screenshot(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerCaptureScreenshotResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_capture_screenshot(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.capture_screenshot(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_click(self, client: Computer) -> None:
        computer = client.computers.click(
            id="id",
        )
        assert_matches_type(ComputerClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_click_with_all_params(self, client: Computer) -> None:
        computer = client.computers.click(
            id="id",
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_click(self, client: Computer) -> None:
        response = client.computers.with_raw_response.click(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_click(self, client: Computer) -> None:
        with client.computers.with_streaming_response.click(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerClickResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_click(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.click(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_connect_websocket(self, client: Computer) -> None:
        computer = client.computers.connect_websocket(
            "id",
        )
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_connect_websocket(self, client: Computer) -> None:
        response = client.computers.with_raw_response.connect_websocket(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_connect_websocket(self, client: Computer) -> None:
        with client.computers.with_streaming_response.connect_websocket(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert computer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_connect_websocket(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.connect_websocket(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_debug(self, client: Computer) -> None:
        computer = client.computers.debug(
            id="id",
        )
        assert_matches_type(ComputerDebugResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_debug_with_all_params(self, client: Computer) -> None:
        computer = client.computers.debug(
            id="id",
            command="command",
            max_output_length=0,
            tab_id="tab_id",
            timeout_seconds=0,
        )
        assert_matches_type(ComputerDebugResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_debug(self, client: Computer) -> None:
        response = client.computers.with_raw_response.debug(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerDebugResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_debug(self, client: Computer) -> None:
        with client.computers.with_streaming_response.debug(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerDebugResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_debug(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.debug(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_double_click(self, client: Computer) -> None:
        computer = client.computers.double_click(
            id="id",
        )
        assert_matches_type(ComputerDoubleClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_double_click_with_all_params(self, client: Computer) -> None:
        computer = client.computers.double_click(
            id="id",
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerDoubleClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_double_click(self, client: Computer) -> None:
        response = client.computers.with_raw_response.double_click(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerDoubleClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_double_click(self, client: Computer) -> None:
        with client.computers.with_streaming_response.double_click(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerDoubleClickResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_double_click(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.double_click(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_drag(self, client: Computer) -> None:
        computer = client.computers.drag(
            id="id",
        )
        assert_matches_type(ComputerDragResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_drag_with_all_params(self, client: Computer) -> None:
        computer = client.computers.drag(
            id="id",
            tab_id="tab_id",
            x1=0,
            x2=0,
            y1=0,
            y2=0,
        )
        assert_matches_type(ComputerDragResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_drag(self, client: Computer) -> None:
        response = client.computers.with_raw_response.drag(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerDragResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_drag(self, client: Computer) -> None:
        with client.computers.with_streaming_response.drag(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerDragResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_drag(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.drag(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_action(self, client: Computer) -> None:
        computer = client.computers.execute_action(
            id="id",
        )
        assert_matches_type(ComputerExecuteActionResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_action_with_all_params(self, client: Computer) -> None:
        computer = client.computers.execute_action(
            id="id",
            action={
                "auto_detect_encoding": True,
                "base64": True,
                "button": "button",
                "debug": {
                    "command": "command",
                    "max_output_length": 0,
                    "timeout_seconds": 0,
                },
                "dx": 0,
                "dy": 0,
                "height": 0,
                "include_context": True,
                "key": "key",
                "keys": ["string"],
                "ms": 0,
                "proxy_url": "proxy_url",
                "scale_factor": 0,
                "tab_id": "tab_id",
                "text": "text",
                "type": "type",
                "url": "url",
                "width": 0,
                "x": 0,
                "x1": 0,
                "x2": 0,
                "y": 0,
                "y1": 0,
                "y2": 0,
            },
        )
        assert_matches_type(ComputerExecuteActionResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_action(self, client: Computer) -> None:
        response = client.computers.with_raw_response.execute_action(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerExecuteActionResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_action(self, client: Computer) -> None:
        with client.computers.with_streaming_response.execute_action(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerExecuteActionResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_execute_action(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.execute_action(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_batch(self, client: Computer) -> None:
        computer = client.computers.execute_batch(
            id="id",
        )
        assert_matches_type(ComputerExecuteBatchResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_batch_with_all_params(self, client: Computer) -> None:
        computer = client.computers.execute_batch(
            id="id",
            actions=[
                {
                    "auto_detect_encoding": True,
                    "base64": True,
                    "button": "button",
                    "debug": {
                        "command": "command",
                        "max_output_length": 0,
                        "timeout_seconds": 0,
                    },
                    "dx": 0,
                    "dy": 0,
                    "height": 0,
                    "include_context": True,
                    "key": "key",
                    "keys": ["string"],
                    "ms": 0,
                    "proxy_url": "proxy_url",
                    "scale_factor": 0,
                    "tab_id": "tab_id",
                    "text": "text",
                    "type": "type",
                    "url": "url",
                    "width": 0,
                    "x": 0,
                    "x1": 0,
                    "x2": 0,
                    "y": 0,
                    "y1": 0,
                    "y2": 0,
                }
            ],
        )
        assert_matches_type(ComputerExecuteBatchResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_batch(self, client: Computer) -> None:
        response = client.computers.with_raw_response.execute_batch(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerExecuteBatchResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_batch(self, client: Computer) -> None:
        with client.computers.with_streaming_response.execute_batch(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerExecuteBatchResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_execute_batch(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.execute_batch(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_html(self, client: Computer) -> None:
        computer = client.computers.get_html(
            id="id",
        )
        assert_matches_type(ComputerGetHTMLResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_html_with_all_params(self, client: Computer) -> None:
        computer = client.computers.get_html(
            id="id",
            auto_detect_encoding=True,
            tab_id="tab_id",
        )
        assert_matches_type(ComputerGetHTMLResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_html(self, client: Computer) -> None:
        response = client.computers.with_raw_response.get_html(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerGetHTMLResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_html(self, client: Computer) -> None:
        with client.computers.with_streaming_response.get_html(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerGetHTMLResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_html(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.get_html(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_keep_alive(self, client: Computer) -> None:
        computer = client.computers.keep_alive(
            "id",
        )
        assert_matches_type(ComputerKeepAliveResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_keep_alive(self, client: Computer) -> None:
        response = client.computers.with_raw_response.keep_alive(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerKeepAliveResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_keep_alive(self, client: Computer) -> None:
        with client.computers.with_streaming_response.keep_alive(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerKeepAliveResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_keep_alive(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.keep_alive(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_key_down(self, client: Computer) -> None:
        computer = client.computers.key_down(
            id="id",
        )
        assert_matches_type(ComputerKeyDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_key_down_with_all_params(self, client: Computer) -> None:
        computer = client.computers.key_down(
            id="id",
            key="key",
            tab_id="tab_id",
        )
        assert_matches_type(ComputerKeyDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_key_down(self, client: Computer) -> None:
        response = client.computers.with_raw_response.key_down(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerKeyDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_key_down(self, client: Computer) -> None:
        with client.computers.with_streaming_response.key_down(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerKeyDownResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_key_down(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.key_down(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_key_up(self, client: Computer) -> None:
        computer = client.computers.key_up(
            id="id",
        )
        assert_matches_type(ComputerKeyUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_key_up_with_all_params(self, client: Computer) -> None:
        computer = client.computers.key_up(
            id="id",
            key="key",
            tab_id="tab_id",
        )
        assert_matches_type(ComputerKeyUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_key_up(self, client: Computer) -> None:
        response = client.computers.with_raw_response.key_up(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerKeyUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_key_up(self, client: Computer) -> None:
        with client.computers.with_streaming_response.key_up(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerKeyUpResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_key_up(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.key_up(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_mouse_down(self, client: Computer) -> None:
        computer = client.computers.mouse_down(
            id="id",
        )
        assert_matches_type(ComputerMouseDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_mouse_down_with_all_params(self, client: Computer) -> None:
        computer = client.computers.mouse_down(
            id="id",
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerMouseDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_mouse_down(self, client: Computer) -> None:
        response = client.computers.with_raw_response.mouse_down(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerMouseDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_mouse_down(self, client: Computer) -> None:
        with client.computers.with_streaming_response.mouse_down(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerMouseDownResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_mouse_down(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.mouse_down(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_mouse_up(self, client: Computer) -> None:
        computer = client.computers.mouse_up(
            id="id",
        )
        assert_matches_type(ComputerMouseUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_mouse_up_with_all_params(self, client: Computer) -> None:
        computer = client.computers.mouse_up(
            id="id",
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerMouseUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_mouse_up(self, client: Computer) -> None:
        response = client.computers.with_raw_response.mouse_up(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerMouseUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_mouse_up(self, client: Computer) -> None:
        with client.computers.with_streaming_response.mouse_up(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerMouseUpResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_mouse_up(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.mouse_up(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_navigate(self, client: Computer) -> None:
        computer = client.computers.navigate(
            id="id",
        )
        assert_matches_type(ComputerNavigateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_navigate_with_all_params(self, client: Computer) -> None:
        computer = client.computers.navigate(
            id="id",
            tab_id="tab_id",
            url="url",
        )
        assert_matches_type(ComputerNavigateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_navigate(self, client: Computer) -> None:
        response = client.computers.with_raw_response.navigate(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerNavigateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_navigate(self, client: Computer) -> None:
        with client.computers.with_streaming_response.navigate(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerNavigateResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_navigate(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.navigate(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_press_hotkey(self, client: Computer) -> None:
        computer = client.computers.press_hotkey(
            id="id",
        )
        assert_matches_type(ComputerPressHotkeyResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_press_hotkey_with_all_params(self, client: Computer) -> None:
        computer = client.computers.press_hotkey(
            id="id",
            keys=["string"],
            tab_id="tab_id",
        )
        assert_matches_type(ComputerPressHotkeyResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_press_hotkey(self, client: Computer) -> None:
        response = client.computers.with_raw_response.press_hotkey(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerPressHotkeyResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_press_hotkey(self, client: Computer) -> None:
        with client.computers.with_streaming_response.press_hotkey(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerPressHotkeyResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_press_hotkey(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.press_hotkey(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_right_click(self, client: Computer) -> None:
        computer = client.computers.right_click(
            id="id",
        )
        assert_matches_type(ComputerRightClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_right_click_with_all_params(self, client: Computer) -> None:
        computer = client.computers.right_click(
            id="id",
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerRightClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_right_click(self, client: Computer) -> None:
        response = client.computers.with_raw_response.right_click(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerRightClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_right_click(self, client: Computer) -> None:
        with client.computers.with_streaming_response.right_click(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerRightClickResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_right_click(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.right_click(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_scroll_viewport(self, client: Computer) -> None:
        computer = client.computers.scroll_viewport(
            id="id",
        )
        assert_matches_type(ComputerScrollViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_scroll_viewport_with_all_params(self, client: Computer) -> None:
        computer = client.computers.scroll_viewport(
            id="id",
            dx=0,
            dy=0,
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerScrollViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_scroll_viewport(self, client: Computer) -> None:
        response = client.computers.with_raw_response.scroll_viewport(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerScrollViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_scroll_viewport(self, client: Computer) -> None:
        with client.computers.with_streaming_response.scroll_viewport(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerScrollViewportResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_scroll_viewport(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.scroll_viewport(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_viewport(self, client: Computer) -> None:
        computer = client.computers.set_viewport(
            id="id",
        )
        assert_matches_type(ComputerSetViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_viewport_with_all_params(self, client: Computer) -> None:
        computer = client.computers.set_viewport(
            id="id",
            height=0,
            scale_factor=0,
            tab_id="tab_id",
            width=0,
        )
        assert_matches_type(ComputerSetViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set_viewport(self, client: Computer) -> None:
        response = client.computers.with_raw_response.set_viewport(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerSetViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set_viewport(self, client: Computer) -> None:
        with client.computers.with_streaming_response.set_viewport(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerSetViewportResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_set_viewport(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.set_viewport(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_stream_events(self, client: Computer) -> None:
        computer = client.computers.stream_events(
            "id",
        )
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_stream_events(self, client: Computer) -> None:
        response = client.computers.with_raw_response.stream_events(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_stream_events(self, client: Computer) -> None:
        with client.computers.with_streaming_response.stream_events(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert computer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_stream_events(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.stream_events(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_stream_screencast(self, client: Computer) -> None:
        computer = client.computers.stream_screencast(
            "id",
        )
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_stream_screencast(self, client: Computer) -> None:
        response = client.computers.with_raw_response.stream_screencast(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_stream_screencast(self, client: Computer) -> None:
        with client.computers.with_streaming_response.stream_screencast(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert computer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_stream_screencast(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.stream_screencast(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_terminate(self, client: Computer) -> None:
        computer = client.computers.terminate(
            "id",
        )
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_terminate(self, client: Computer) -> None:
        response = client.computers.with_raw_response.terminate(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_terminate(self, client: Computer) -> None:
        with client.computers.with_streaming_response.terminate(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert computer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_terminate(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.terminate(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_type_text(self, client: Computer) -> None:
        computer = client.computers.type_text(
            id="id",
        )
        assert_matches_type(ComputerTypeTextResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_type_text_with_all_params(self, client: Computer) -> None:
        computer = client.computers.type_text(
            id="id",
            tab_id="tab_id",
            text="text",
        )
        assert_matches_type(ComputerTypeTextResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_type_text(self, client: Computer) -> None:
        response = client.computers.with_raw_response.type_text(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = response.parse()
        assert_matches_type(ComputerTypeTextResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_type_text(self, client: Computer) -> None:
        with client.computers.with_streaming_response.type_text(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = response.parse()
            assert_matches_type(ComputerTypeTextResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_type_text(self, client: Computer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.computers.with_raw_response.type_text(
                id="",
            )


class TestAsyncComputers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.create()
        assert_matches_type(ComputerCreateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.create(
            auto_kill=True,
            context_id="context_id",
            display={
                "height": 0,
                "scale": 0,
                "width": 0,
            },
            kind="kind",
            stealth={},
            timeout_seconds=0,
        )
        assert_matches_type(ComputerCreateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerCreateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerCreateResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.retrieve(
            "id",
        )
        assert_matches_type(ComputerRetrieveResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerRetrieveResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerRetrieveResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.list()
        assert_matches_type(ComputerListResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerListResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerListResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_capture_screenshot(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.capture_screenshot(
            id="id",
        )
        assert_matches_type(ComputerCaptureScreenshotResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_capture_screenshot_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.capture_screenshot(
            id="id",
            base64=True,
            tab_id="tab_id",
        )
        assert_matches_type(ComputerCaptureScreenshotResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_capture_screenshot(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.capture_screenshot(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerCaptureScreenshotResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_capture_screenshot(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.capture_screenshot(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerCaptureScreenshotResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_capture_screenshot(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.capture_screenshot(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_click(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.click(
            id="id",
        )
        assert_matches_type(ComputerClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_click_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.click(
            id="id",
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_click(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.click(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_click(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.click(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerClickResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_click(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.click(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_connect_websocket(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.connect_websocket(
            "id",
        )
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_connect_websocket(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.connect_websocket(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_connect_websocket(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.connect_websocket(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert computer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_connect_websocket(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.connect_websocket(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_debug(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.debug(
            id="id",
        )
        assert_matches_type(ComputerDebugResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_debug_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.debug(
            id="id",
            command="command",
            max_output_length=0,
            tab_id="tab_id",
            timeout_seconds=0,
        )
        assert_matches_type(ComputerDebugResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_debug(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.debug(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerDebugResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_debug(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.debug(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerDebugResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_debug(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.debug(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_double_click(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.double_click(
            id="id",
        )
        assert_matches_type(ComputerDoubleClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_double_click_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.double_click(
            id="id",
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerDoubleClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_double_click(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.double_click(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerDoubleClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_double_click(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.double_click(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerDoubleClickResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_double_click(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.double_click(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_drag(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.drag(
            id="id",
        )
        assert_matches_type(ComputerDragResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_drag_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.drag(
            id="id",
            tab_id="tab_id",
            x1=0,
            x2=0,
            y1=0,
            y2=0,
        )
        assert_matches_type(ComputerDragResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_drag(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.drag(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerDragResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_drag(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.drag(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerDragResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_drag(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.drag(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_action(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.execute_action(
            id="id",
        )
        assert_matches_type(ComputerExecuteActionResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_action_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.execute_action(
            id="id",
            action={
                "auto_detect_encoding": True,
                "base64": True,
                "button": "button",
                "debug": {
                    "command": "command",
                    "max_output_length": 0,
                    "timeout_seconds": 0,
                },
                "dx": 0,
                "dy": 0,
                "height": 0,
                "include_context": True,
                "key": "key",
                "keys": ["string"],
                "ms": 0,
                "proxy_url": "proxy_url",
                "scale_factor": 0,
                "tab_id": "tab_id",
                "text": "text",
                "type": "type",
                "url": "url",
                "width": 0,
                "x": 0,
                "x1": 0,
                "x2": 0,
                "y": 0,
                "y1": 0,
                "y2": 0,
            },
        )
        assert_matches_type(ComputerExecuteActionResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_action(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.execute_action(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerExecuteActionResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_action(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.execute_action(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerExecuteActionResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_execute_action(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.execute_action(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_batch(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.execute_batch(
            id="id",
        )
        assert_matches_type(ComputerExecuteBatchResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_batch_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.execute_batch(
            id="id",
            actions=[
                {
                    "auto_detect_encoding": True,
                    "base64": True,
                    "button": "button",
                    "debug": {
                        "command": "command",
                        "max_output_length": 0,
                        "timeout_seconds": 0,
                    },
                    "dx": 0,
                    "dy": 0,
                    "height": 0,
                    "include_context": True,
                    "key": "key",
                    "keys": ["string"],
                    "ms": 0,
                    "proxy_url": "proxy_url",
                    "scale_factor": 0,
                    "tab_id": "tab_id",
                    "text": "text",
                    "type": "type",
                    "url": "url",
                    "width": 0,
                    "x": 0,
                    "x1": 0,
                    "x2": 0,
                    "y": 0,
                    "y1": 0,
                    "y2": 0,
                }
            ],
        )
        assert_matches_type(ComputerExecuteBatchResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_batch(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.execute_batch(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerExecuteBatchResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_batch(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.execute_batch(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerExecuteBatchResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_execute_batch(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.execute_batch(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_html(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.get_html(
            id="id",
        )
        assert_matches_type(ComputerGetHTMLResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_html_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.get_html(
            id="id",
            auto_detect_encoding=True,
            tab_id="tab_id",
        )
        assert_matches_type(ComputerGetHTMLResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_html(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.get_html(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerGetHTMLResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_html(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.get_html(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerGetHTMLResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_html(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.get_html(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_keep_alive(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.keep_alive(
            "id",
        )
        assert_matches_type(ComputerKeepAliveResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_keep_alive(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.keep_alive(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerKeepAliveResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_keep_alive(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.keep_alive(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerKeepAliveResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_keep_alive(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.keep_alive(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_key_down(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.key_down(
            id="id",
        )
        assert_matches_type(ComputerKeyDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_key_down_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.key_down(
            id="id",
            key="key",
            tab_id="tab_id",
        )
        assert_matches_type(ComputerKeyDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_key_down(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.key_down(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerKeyDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_key_down(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.key_down(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerKeyDownResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_key_down(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.key_down(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_key_up(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.key_up(
            id="id",
        )
        assert_matches_type(ComputerKeyUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_key_up_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.key_up(
            id="id",
            key="key",
            tab_id="tab_id",
        )
        assert_matches_type(ComputerKeyUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_key_up(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.key_up(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerKeyUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_key_up(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.key_up(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerKeyUpResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_key_up(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.key_up(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_mouse_down(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.mouse_down(
            id="id",
        )
        assert_matches_type(ComputerMouseDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_mouse_down_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.mouse_down(
            id="id",
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerMouseDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_mouse_down(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.mouse_down(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerMouseDownResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_mouse_down(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.mouse_down(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerMouseDownResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_mouse_down(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.mouse_down(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_mouse_up(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.mouse_up(
            id="id",
        )
        assert_matches_type(ComputerMouseUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_mouse_up_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.mouse_up(
            id="id",
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerMouseUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_mouse_up(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.mouse_up(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerMouseUpResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_mouse_up(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.mouse_up(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerMouseUpResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_mouse_up(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.mouse_up(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_navigate(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.navigate(
            id="id",
        )
        assert_matches_type(ComputerNavigateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_navigate_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.navigate(
            id="id",
            tab_id="tab_id",
            url="url",
        )
        assert_matches_type(ComputerNavigateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_navigate(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.navigate(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerNavigateResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_navigate(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.navigate(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerNavigateResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_navigate(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.navigate(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_press_hotkey(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.press_hotkey(
            id="id",
        )
        assert_matches_type(ComputerPressHotkeyResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_press_hotkey_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.press_hotkey(
            id="id",
            keys=["string"],
            tab_id="tab_id",
        )
        assert_matches_type(ComputerPressHotkeyResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_press_hotkey(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.press_hotkey(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerPressHotkeyResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_press_hotkey(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.press_hotkey(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerPressHotkeyResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_press_hotkey(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.press_hotkey(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_right_click(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.right_click(
            id="id",
        )
        assert_matches_type(ComputerRightClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_right_click_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.right_click(
            id="id",
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerRightClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_right_click(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.right_click(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerRightClickResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_right_click(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.right_click(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerRightClickResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_right_click(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.right_click(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_scroll_viewport(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.scroll_viewport(
            id="id",
        )
        assert_matches_type(ComputerScrollViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_scroll_viewport_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.scroll_viewport(
            id="id",
            dx=0,
            dy=0,
            tab_id="tab_id",
            x=0,
            y=0,
        )
        assert_matches_type(ComputerScrollViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_scroll_viewport(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.scroll_viewport(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerScrollViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_scroll_viewport(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.scroll_viewport(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerScrollViewportResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_scroll_viewport(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.scroll_viewport(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_viewport(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.set_viewport(
            id="id",
        )
        assert_matches_type(ComputerSetViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_viewport_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.set_viewport(
            id="id",
            height=0,
            scale_factor=0,
            tab_id="tab_id",
            width=0,
        )
        assert_matches_type(ComputerSetViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set_viewport(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.set_viewport(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerSetViewportResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set_viewport(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.set_viewport(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerSetViewportResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_set_viewport(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.set_viewport(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_stream_events(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.stream_events(
            "id",
        )
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_stream_events(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.stream_events(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_stream_events(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.stream_events(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert computer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_stream_events(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.stream_events(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_stream_screencast(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.stream_screencast(
            "id",
        )
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_stream_screencast(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.stream_screencast(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_stream_screencast(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.stream_screencast(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert computer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_stream_screencast(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.stream_screencast(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_terminate(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.terminate(
            "id",
        )
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_terminate(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.terminate(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert computer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_terminate(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.terminate(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert computer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_terminate(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.terminate(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_type_text(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.type_text(
            id="id",
        )
        assert_matches_type(ComputerTypeTextResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_type_text_with_all_params(self, async_client: AsyncComputer) -> None:
        computer = await async_client.computers.type_text(
            id="id",
            tab_id="tab_id",
            text="text",
        )
        assert_matches_type(ComputerTypeTextResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_type_text(self, async_client: AsyncComputer) -> None:
        response = await async_client.computers.with_raw_response.type_text(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        computer = await response.parse()
        assert_matches_type(ComputerTypeTextResponse, computer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_type_text(self, async_client: AsyncComputer) -> None:
        async with async_client.computers.with_streaming_response.type_text(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            computer = await response.parse()
            assert_matches_type(ComputerTypeTextResponse, computer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_type_text(self, async_client: AsyncComputer) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.computers.with_raw_response.type_text(
                id="",
            )
