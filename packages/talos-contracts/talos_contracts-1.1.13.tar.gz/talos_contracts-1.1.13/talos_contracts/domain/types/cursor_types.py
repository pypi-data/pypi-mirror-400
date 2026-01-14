"""Domain layer types: cursor validation types."""

from __future__ import annotations

from typing import Literal, TypedDict

CursorValidationReason = Literal["CURSOR_MISMATCH", "INVALID_FRAME"]


class CursorOk(TypedDict):
    """Successful cursor validation result."""

    ok: Literal[True]
    derived: str


class CursorBad(TypedDict):
    """Failed cursor validation result."""

    ok: Literal[False]
    derived: str
    reason: CursorValidationReason


CursorValidationResult = CursorOk | CursorBad


class DecodedCursor(TypedDict):
    """Decoded cursor structure."""

    timestamp: int
    event_id: str


class Event(TypedDict):
    """Event structure for ordering and cursor validation."""

    timestamp: int
    event_id: str
