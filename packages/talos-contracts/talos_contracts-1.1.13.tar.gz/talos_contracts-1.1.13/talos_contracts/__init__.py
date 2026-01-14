"""Talos Protocol contracts - schemas, types, and helper functions.

Public API - all exports are stable and backward-compatible.
"""

# Infrastructure layer
# Domain layer - logic
from talos_contracts.domain.logic import (
    assert_cursor_invariant,
    compare_cursor,
    decode_cursor,
    derive_cursor,
    ordering_compare,
)

# Domain layer - types
from talos_contracts.domain.types import (
    CursorBad,
    CursorOk,
    CursorValidationReason,
    CursorValidationResult,
    DecodedCursor,
)
from talos_contracts.infrastructure import (
    Base64UrlError,
    base64url_decode,
    base64url_encode,
    is_canonical_lower_uuid,
    is_uuid_v7,
)

__all__ = [
    # Infrastructure: Base64url
    "Base64UrlError",
    "base64url_encode",
    "base64url_decode",
    # Infrastructure: UUIDv7
    "is_uuid_v7",
    "is_canonical_lower_uuid",
    # Domain: Cursor types
    "CursorValidationReason",
    "CursorOk",
    "CursorBad",
    "CursorValidationResult",
    "DecodedCursor",
    # Domain: Cursor operations
    "derive_cursor",
    "decode_cursor",
    "compare_cursor",
    "assert_cursor_invariant",
    # Domain: Ordering
    "ordering_compare",
]
