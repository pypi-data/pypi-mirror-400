"""Vector-driven tests for talos-contracts Python package."""

import json
from pathlib import Path

import pytest

from talos_contracts import (
    Base64UrlError,
    base64url_decode,
    base64url_encode,
    derive_cursor,
    is_uuid_v7,
    ordering_compare,
)

ROOT = Path(__file__).resolve().parents[2]
V = ROOT / "test_vectors"


def test_base64url_valid():
    """Test valid base64url encoding/decoding cases."""
    data = json.loads((V / "base64url.json").read_text())
    for case in data["valid"]:
        b = bytes.fromhex(case["bytes_hex"])
        assert base64url_encode(b) == case["encoded"]
        assert base64url_decode(case["encoded"]).hex() == case["bytes_hex"]


def test_base64url_invalid():
    """Test that invalid base64url strings are rejected."""
    data = json.loads((V / "base64url.json").read_text())
    for s in data["invalid"]:
        with pytest.raises(Base64UrlError):
            base64url_decode(s)


def test_cursor_derivation():
    """Test cursor derivation matches golden vectors."""
    vec = json.loads((V / "cursor_derivation.json").read_text())
    for c in vec:
        assert derive_cursor(c["timestamp"], c["event_id"]) == c["expected_cursor"]


def test_uuidv7_valid():
    """Test valid UUIDv7 strings."""
    data = json.loads((V / "uuidv7.json").read_text())
    for v in data["valid"]:
        assert is_uuid_v7(v) is True


def test_uuidv7_invalid():
    """Test invalid UUIDv7 strings."""
    data = json.loads((V / "uuidv7.json").read_text())
    for inv in data["invalid"]:
        assert is_uuid_v7(inv) is False


def test_ordering_pairs():
    """Test event ordering comparison."""
    vec = json.loads((V / "ordering.json").read_text())
    for c in vec:
        assert ordering_compare(c["a"], c["b"]) == c["expected"]
