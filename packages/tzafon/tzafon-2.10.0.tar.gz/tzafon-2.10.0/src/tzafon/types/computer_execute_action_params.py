# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .._types import SequenceNotStr

__all__ = ["ComputerExecuteActionParams", "Action", "ActionDebug"]


class ComputerExecuteActionParams(TypedDict, total=False):
    action: Action


class ActionDebug(TypedDict, total=False):
    command: str

    max_output_length: int

    timeout_seconds: int


class Action(TypedDict, total=False):
    auto_detect_encoding: bool
    """For get_html_content"""

    base64: bool
    """For screenshot"""

    button: str

    debug: ActionDebug

    dx: float
    """For scrolling"""

    dy: float

    height: int

    include_context: bool
    """Include page context in response"""

    key: str
    """For key_down/key_up"""

    keys: SequenceNotStr[str]

    ms: int

    proxy_url: str

    scale_factor: float

    tab_id: str
    """For tab management (browser sessions only)"""

    text: str

    type: str
    """
    click|double_click|right_click|drag|type|keypress|scroll|wait|screenshot|go_to_url|debug|get_html_content|set_viewport|list_tabs|new_tab|switch_tab|close_tab|key_down|key_up|mouse_down|mouse_up
    """

    url: str

    width: int
    """For set_viewport"""

    x: float

    x1: float
    """For dragging/scrolling"""

    x2: float
    """For dragging"""

    y: float

    y1: float

    y2: float
