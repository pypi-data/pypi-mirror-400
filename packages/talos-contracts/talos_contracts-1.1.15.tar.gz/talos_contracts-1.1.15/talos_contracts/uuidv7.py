"""Compatibility shim for uuidv7.

.. deprecated::
    Import from `talos_contracts` root instead.
"""

import warnings

warnings.warn(
    "Importing from talos_contracts.uuidv7 is deprecated. "
    "Import from talos_contracts root instead.",
    DeprecationWarning,
    stacklevel=2,
)

from talos_contracts.infrastructure.uuidv7 import (  # noqa: E402
    is_canonical_lower_uuid,
    is_uuid_v7,
)

__all__ = [
    "is_uuid_v7",
    "is_canonical_lower_uuid",
]
