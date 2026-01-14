"""Compatibility shim for base64url.

.. deprecated::
    Import from `talos_contracts` root instead.
"""

import warnings

warnings.warn(
    "Importing from talos_contracts.base64url is deprecated. "
    "Import from talos_contracts root instead.",
    DeprecationWarning,
    stacklevel=2,
)

from talos_contracts.infrastructure.base64url import (  # noqa: E402
    Base64UrlError,
    base64url_decode,
    base64url_encode,
)

__all__ = [
    "Base64UrlError",
    "base64url_encode",
    "base64url_decode",
]
