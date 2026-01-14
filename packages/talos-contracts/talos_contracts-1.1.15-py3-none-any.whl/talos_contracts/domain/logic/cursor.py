"""Domain logic: cursor operations.

D4=B: Invalid frames do not throw from validation, return INVALID_FRAME.
"""

from __future__ import annotations

from typing import Any

from talos_contracts.domain.types.cursor_types import CursorValidationResult, DecodedCursor
from talos_contracts.infrastructure.base64url import base64url_decode, base64url_encode
from talos_contracts.infrastructure.uuidv7 import is_canonical_lower_uuid, is_uuid_v7


def _is_valid_unix_seconds_int(n: Any) -> bool:
    """Check if n is a valid unix seconds integer."""
    return isinstance(n, int) and n >= 0


def _is_canonical_ts_str(s: str) -> bool:
    """Check if timestamp string is canonical (no leading zeros except "0")."""
    if not s.isdigit():
        return False
    return not (len(s) > 1 and s.startswith("0"))


def derive_cursor(timestamp: int, event_id: str) -> str:
    """
    Derive a cursor from timestamp and event_id.

    cursor = base64url(utf8("{timestamp}:{event_id}"))

    Args:
        timestamp: Unix seconds integer
        event_id: Event ID (should be UUIDv7)

    Returns:
        Base64url encoded cursor

    Raises:
        ValueError: If timestamp is not a valid unix seconds integer
    """
    if not _is_valid_unix_seconds_int(timestamp):
        raise ValueError("timestamp must be unix seconds integer")
    plain = f"{timestamp}:{event_id}".encode()
    return base64url_encode(plain)


def decode_cursor(cursor: str) -> DecodedCursor:
    """
    Decode a cursor to {timestamp, event_id}.

    Args:
        cursor: Base64url encoded cursor

    Returns:
        DecodedCursor TypedDict with 'timestamp' and 'event_id'

    Raises:
        ValueError: If cursor format is invalid
    """
    raw = base64url_decode(cursor).decode("utf-8")

    colon_idx = raw.find(":")
    if colon_idx == -1:
        raise ValueError("cursor frame must be '{timestamp}:{event_id}'")

    ts_str = raw[:colon_idx]
    event_id = raw[colon_idx + 1 :]

    if not _is_canonical_ts_str(ts_str):
        raise ValueError("timestamp is not canonical base-10")

    ts = int(ts_str)
    if not _is_valid_unix_seconds_int(ts):
        raise ValueError("timestamp out of range")

    if not is_uuid_v7(event_id):
        raise ValueError("event_id is not uuidv7")
    if not is_canonical_lower_uuid(event_id):
        raise ValueError("event_id must be lowercase canonical uuid")

    return {"timestamp": ts, "event_id": event_id}


def compare_cursor(a: str, b: str) -> int:
    """
    Compare two cursors.

    Args:
        a: First cursor
        b: Second cursor

    Returns:
        -1 if a < b, 0 if equal, 1 if a > b
    """
    da = decode_cursor(a)
    db = decode_cursor(b)

    if da["timestamp"] < db["timestamp"]:
        return -1
    if da["timestamp"] > db["timestamp"]:
        return 1

    if da["event_id"] < db["event_id"]:
        return -1
    if da["event_id"] > db["event_id"]:
        return 1

    return 0


def assert_cursor_invariant(event: dict[str, Any]) -> CursorValidationResult:
    """
    Validate that an event's cursor matches the derived cursor.

    D4=B: Does not throw on invalid frames, returns { ok: False, reason: "INVALID_FRAME" }

    Args:
        event: Dict with 'timestamp', 'event_id', and 'cursor' keys

    Returns:
        CursorValidationResult with ok=True/False and reason if failed
    """
    ts = event.get("timestamp")
    eid = event.get("event_id")
    cur = event.get("cursor")

    # Frame checks first (D4=B: do not throw)
    if not isinstance(ts, int) or ts < 0 or not isinstance(eid, str) or not isinstance(cur, str):
        return {"ok": False, "derived": "", "reason": "INVALID_FRAME"}

    # Decode cursor must be strict base64url + canonical frame. If it fails, INVALID_FRAME.
    try:
        decode_cursor(cur)
    except Exception:
        derived = derive_cursor(ts, eid)
        return {"ok": False, "derived": derived, "reason": "INVALID_FRAME"}

    # Derived cursor must match exactly (CURSOR_MISMATCH)
    derived = derive_cursor(ts, eid)
    if cur != derived:
        return {"ok": False, "derived": derived, "reason": "CURSOR_MISMATCH"}

    # Also enforce event_id canonical uuidv7 for the event frame
    if not is_uuid_v7(eid) or not is_canonical_lower_uuid(eid):
        return {"ok": False, "derived": derived, "reason": "INVALID_FRAME"}

    return {"ok": True, "derived": derived}
