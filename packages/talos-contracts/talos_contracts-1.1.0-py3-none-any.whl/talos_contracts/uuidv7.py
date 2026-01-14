"""UUIDv7 validation."""

from __future__ import annotations

import re

_RE_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def is_uuid_v7(value: str) -> bool:
    """
    Check if a string is a valid UUIDv7.

    Validates:
    - UUID format
    - Version nibble is 7
    - Variant nibble is 8, 9, a, or b

    Args:
        value: String to validate

    Returns:
        True if valid UUIDv7, False otherwise
    """
    if not _RE_UUID.match(value):
        return False

    # Version nibble is first nibble of 3rd group (position 14)
    version = value[14]
    if version.lower() != "7":
        return False

    # Variant is first nibble of 4th group (position 19): 8, 9, a, b
    variant = value[19].lower()
    return variant in ("8", "9", "a", "b")


def is_canonical_lower_uuid(value: str) -> bool:
    """
    Check if a UUID is in canonical lowercase form.

    Args:
        value: UUID string to check

    Returns:
        True if all lowercase, False otherwise
    """
    return value == value.lower()
