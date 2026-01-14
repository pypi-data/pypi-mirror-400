"""Strict base64url encoding/decoding - NO padding allowed."""

from __future__ import annotations

import re


class Base64UrlError(ValueError):
    """Error raised for invalid base64url encoding/decoding."""

    pass


_RE_VALID = re.compile(r"^[A-Za-z0-9\-_]*$")

_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
_INV = {c: i for i, c in enumerate(_ALPHABET)}


def base64url_encode(data: bytes) -> str:
    """
    Encode bytes to base64url string without padding.

    Args:
        data: Bytes to encode

    Returns:
        Base64url encoded string (no padding)
    """
    if not data:
        return ""

    out: list[str] = []
    i = 0
    n = len(data)

    while i + 3 <= n:
        x = (data[i] << 16) | (data[i + 1] << 8) | data[i + 2]
        out.append(_ALPHABET[(x >> 18) & 63])
        out.append(_ALPHABET[(x >> 12) & 63])
        out.append(_ALPHABET[(x >> 6) & 63])
        out.append(_ALPHABET[x & 63])
        i += 3

    rem = n - i
    if rem == 1:
        x = data[i]
        out.append(_ALPHABET[(x >> 2) & 63])
        out.append(_ALPHABET[(x << 4) & 63])
    elif rem == 2:
        x = (data[i] << 8) | data[i + 1]
        out.append(_ALPHABET[(x >> 10) & 63])
        out.append(_ALPHABET[(x >> 4) & 63])
        out.append(_ALPHABET[(x << 2) & 63])

    return "".join(out)


def _decode_char(c: str) -> int:
    """Decode a single base64url character."""
    if c not in _INV:
        raise Base64UrlError(f"Invalid base64url character: {c}")
    return _INV[c]


def base64url_decode(s: str) -> bytes:
    """
    Decode base64url string to bytes.

    Rejects padding and non-canonical forms.

    Args:
        s: Base64url encoded string (no padding)

    Returns:
        Decoded bytes

    Raises:
        Base64UrlError: If input is not valid canonical base64url
    """
    if s == "":
        return b""

    if "=" in s:
        raise Base64UrlError("Padding is not allowed")
    if not _RE_VALID.match(s):
        raise Base64UrlError("Non-base64url characters present")
    if len(s) % 4 == 1:
        raise Base64UrlError("Invalid base64url length")

    out = bytearray()
    i = 0

    while i < len(s):
        remain = len(s) - i

        if remain >= 4:
            a = _decode_char(s[i])
            b = _decode_char(s[i + 1])
            c = _decode_char(s[i + 2])
            d = _decode_char(s[i + 3])
            x = (a << 18) | (b << 12) | (c << 6) | d
            out.extend([(x >> 16) & 255, (x >> 8) & 255, x & 255])
            i += 4
        elif remain == 2:
            a = _decode_char(s[i])
            b = _decode_char(s[i + 1])
            x = (a << 18) | (b << 12)
            out.append((x >> 16) & 255)
            i += 2
        elif remain == 3:
            a = _decode_char(s[i])
            b = _decode_char(s[i + 1])
            c = _decode_char(s[i + 2])
            x = (a << 18) | (b << 12) | (c << 6)
            out.extend([(x >> 16) & 255, (x >> 8) & 255])
            i += 3
        else:
            raise Base64UrlError("Invalid base64url length")

    # Strict canonical check: re-encode must match exactly
    if base64url_encode(bytes(out)) != s:
        raise Base64UrlError("Non-canonical base64url form")

    return bytes(out)
