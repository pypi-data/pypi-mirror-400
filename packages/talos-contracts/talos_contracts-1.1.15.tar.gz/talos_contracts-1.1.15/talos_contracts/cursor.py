"""Compatibility shim for cursor.

.. deprecated::
    Import from `talos_contracts` root instead.
"""

import warnings

warnings.warn(
    "Importing from talos_contracts.cursor is deprecated. "
    "Import from talos_contracts root instead.",
    DeprecationWarning,
    stacklevel=2,
)

from talos_contracts.domain.logic.cursor import (  # noqa: E402
    assert_cursor_invariant,
    compare_cursor,
    decode_cursor,
    derive_cursor,
)
from talos_contracts.domain.types.cursor_types import (  # noqa: E402
    CursorValidationResult,
)

__all__ = [
    "derive_cursor",
    "decode_cursor",
    "compare_cursor",
    "assert_cursor_invariant",
    "CursorValidationResult",
]
