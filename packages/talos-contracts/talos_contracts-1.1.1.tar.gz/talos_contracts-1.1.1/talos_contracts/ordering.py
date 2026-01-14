"""Compatibility shim for ordering.

.. deprecated::
    Import from `talos_contracts` root instead.
"""

import warnings

warnings.warn(
    "Importing from talos_contracts.ordering is deprecated. "
    "Import from talos_contracts root instead.",
    DeprecationWarning,
    stacklevel=2,
)

from talos_contracts.domain.logic.ordering import ordering_compare  # noqa: E402

__all__ = [
    "ordering_compare",
]
