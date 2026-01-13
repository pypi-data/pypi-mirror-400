# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ComputerCreateParams", "Display"]


class ComputerCreateParams(TypedDict, total=False):
    auto_kill: bool
    """If true (default), kill session after inactivity"""

    context_id: str

    display: Display

    kind: str
    """\"browser" (default) or "desktop" """

    stealth: object

    timeout_seconds: int


class Display(TypedDict, total=False):
    height: int

    scale: float

    width: int
