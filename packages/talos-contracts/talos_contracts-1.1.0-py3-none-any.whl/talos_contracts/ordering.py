"""Event ordering comparison: (timestamp DESC, event_id DESC)."""

from __future__ import annotations

from typing import Literal


def ordering_compare(
    a: dict[str, int | str],
    b: dict[str, int | str],
) -> Literal[-1, 0, 1]:
    """
    Compare two events for ordering.

    Returns -1 if a should come before b (a is "greater" in DESC order)
    Returns 0 if equal
    Returns 1 if a should come after b

    Ordering: timestamp DESC, then event_id DESC

    Args:
        a: Dict with 'timestamp' and 'event_id'
        b: Dict with 'timestamp' and 'event_id'

    Returns:
        -1, 0, or 1
    """
    a_ts = a["timestamp"]
    b_ts = b["timestamp"]
    a_eid = a["event_id"]
    b_eid = b["event_id"]

    # DESC timestamp: higher timestamp comes first
    if a_ts > b_ts:
        return -1
    if a_ts < b_ts:
        return 1

    # DESC event_id: higher event_id comes first (lexicographic)
    if a_eid > b_eid:
        return -1
    if a_eid < b_eid:
        return 1

    return 0
