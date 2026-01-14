"""Golden vector tests - shared with TypeScript for cross-language parity."""

import json
from pathlib import Path

import pytest

from talos_contracts import (
    Base64UrlError,
    assert_cursor_invariant,
    base64url_decode,
    base64url_encode,
    compare_cursor,
    decode_cursor,
    derive_cursor,
    is_canonical_lower_uuid,
    is_uuid_v7,
    ordering_compare,
)


@pytest.fixture
def vectors():
    """Load golden vectors from JSON."""
    vectors_path = Path(__file__).parent / "vectors" / "golden.json"
    with open(vectors_path) as f:
        return json.load(f)


class TestBase64urlGoldenVectors:
    """Base64url golden vector tests."""

    def test_encode_vectors(self, vectors):
        """Test encode vectors match expected output."""
        for tc in vectors["base64url"]["encode"]:
            input_bytes = bytes(tc["input"])
            result = base64url_encode(input_bytes)
            assert result == tc["expected"], (
                f"encode({tc['input']}) = {result}, expected {tc['expected']}"
            )

    def test_decode_vectors(self, vectors):
        """Test decode vectors match expected output."""
        for tc in vectors["base64url"]["decode"]:
            result = base64url_decode(tc["input"])
            assert list(result) == tc["expected"], f"decode({tc['input']}) = {list(result)}"

    def test_invalid_vectors_raise(self, vectors):
        """Test invalid inputs raise Base64UrlError."""
        for tc in vectors["base64url"]["invalid"]:
            with pytest.raises(Base64UrlError):
                base64url_decode(tc["input"])


class TestUuidv7GoldenVectors:
    """UUIDv7 golden vector tests."""

    def test_valid_uuids(self, vectors):
        """Test valid UUIDv7 strings are accepted."""
        for uuid in vectors["uuidv7"]["valid"]:
            assert is_uuid_v7(uuid) is True, f"is_uuid_v7({uuid}) should be True"

    def test_invalid_uuids(self, vectors):
        """Test invalid UUIDv7 strings are rejected."""
        for uuid in vectors["uuidv7"]["invalid"]:
            assert is_uuid_v7(uuid) is False, f"is_uuid_v7({uuid}) should be False"

    def test_canonical_lower(self, vectors):
        """Test canonical lowercase detection."""
        for tc in vectors["uuidv7"]["canonical_lower"]:
            result = is_canonical_lower_uuid(tc["input"])
            assert result == tc["expected"], f"is_canonical_lower_uuid({tc['input']}) = {result}"

    def test_valid_but_not_canonical(self, vectors):
        """Test UUIDs that are valid v7 but not canonical lowercase."""
        for tc in vectors["uuidv7"]["valid_but_not_canonical"]:
            assert is_uuid_v7(tc["input"]) == tc["isV7"]
            assert is_canonical_lower_uuid(tc["input"]) == tc["isCanonicalLower"]


class TestCursorGoldenVectors:
    """Cursor golden vector tests."""

    def test_derive_vectors(self, vectors):
        """Test derive_cursor matches expected output."""
        for tc in vectors["cursor"]["derive"]:
            result = derive_cursor(tc["timestamp"], tc["event_id"])
            assert result == tc["expected"], (
                f"derive_cursor({tc['timestamp']}, {tc['event_id']}) = {result}"
            )

    def test_decode_vectors(self, vectors):
        """Test decode_cursor matches expected output."""
        for tc in vectors["cursor"]["decode"]:
            result = decode_cursor(tc["input"])
            assert result["timestamp"] == tc["expected"]["timestamp"]
            assert result["event_id"] == tc["expected"]["event_id"]

    def test_compare_vectors(self, vectors):
        """Test compare_cursor matches expected output."""
        for tc in vectors["cursor"]["compare"]:
            result = compare_cursor(tc["a"], tc["b"])
            assert result == tc["expected"], (
                f"compare_cursor returns {result}, expected {tc['expected']}"
            )

    def test_invariant_vectors(self, vectors):
        """Test assert_cursor_invariant matches expected output."""
        for tc in vectors["cursor"]["invariant"]:
            event = tc["event"]
            expected = tc["expected"]
            result = assert_cursor_invariant(event)
            assert result["ok"] == expected["ok"]
            if not expected["ok"] and "reason" in expected:
                assert result.get("reason") == expected["reason"]


class TestOrderingGoldenVectors:
    """Ordering golden vector tests."""

    def test_compare_vectors(self, vectors):
        """Test ordering_compare matches expected output."""
        for tc in vectors["ordering"]["compare"]:
            result = ordering_compare(tc["a"], tc["b"])
            assert result == tc["expected"], (
                f"ordering_compare returns {result}, expected {tc['expected']}"
            )
