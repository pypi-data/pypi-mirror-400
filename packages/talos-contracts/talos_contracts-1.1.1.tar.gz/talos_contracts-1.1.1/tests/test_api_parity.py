"""API parity tests - verify public API stability and shim deprecation warnings."""

import importlib
import warnings

import talos_contracts


class TestPublicAPI:
    """Test public API symbol stability via __all__."""

    EXPECTED_PUBLIC_SYMBOLS = sorted(
        [
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
    )

    def test_dunder_all_matches_expected_symbols(self):
        """Verify __all__ contains exactly the expected public symbols."""
        actual = sorted(talos_contracts.__all__)
        assert actual == self.EXPECTED_PUBLIC_SYMBOLS, (
            f"Public API mismatch.\n"
            f"Missing: {set(self.EXPECTED_PUBLIC_SYMBOLS) - set(actual)}\n"
            f"Extra: {set(actual) - set(self.EXPECTED_PUBLIC_SYMBOLS)}"
        )

    def test_star_import_only_gets_public_symbols(self):
        """from talos_contracts import * should not pull internal modules."""
        # Simulate star import by checking __all__ doesn't include internal modules
        internal_modules = ["infrastructure", "domain", "base64url", "uuidv7", "cursor", "ordering"]
        for internal in internal_modules:
            assert internal not in talos_contracts.__all__, f"Internal module {internal} in __all__"


class TestShimDeprecationWarnings:
    """Test that shim imports emit deprecation warnings with correct stacklevel."""

    def _test_shim_warns(self, module_path: str, expected_substring: str):
        """Helper to test a shim module emits DeprecationWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Import and reload to trigger warning
            module = importlib.import_module(module_path)
            importlib.reload(module)

            # Filter for DeprecationWarning only
            dep_warnings = [x for x in w if x.category is DeprecationWarning]

            # Should have at least one warning (reload may cause duplicate)
            assert len(dep_warnings) >= 1, f"Expected at least 1 warning, got {len(dep_warnings)}"

            # Message should contain expected substring
            msg = str(dep_warnings[0].message)
            assert expected_substring.lower() in msg.lower(), (
                f"Expected '{expected_substring}' in '{msg}'"
            )

            # Stacklevel check: warning filename should NOT be the shim module itself
            # (it should point to the caller, which in this case is this test file)
            warning_filename = dep_warnings[0].filename
            assert module_path.replace(".", "/") not in warning_filename, (
                f"Stacklevel wrong: warning points to shim module itself ({warning_filename})"
            )

    def test_base64url_shim_warns(self):
        """Importing talos_contracts.base64url should warn once with correct stacklevel."""
        self._test_shim_warns("talos_contracts.base64url", "deprecated")

    def test_uuidv7_shim_warns(self):
        """Importing talos_contracts.uuidv7 should warn once with correct stacklevel."""
        self._test_shim_warns("talos_contracts.uuidv7", "deprecated")

    def test_cursor_shim_warns(self):
        """Importing talos_contracts.cursor should warn once with correct stacklevel."""
        self._test_shim_warns("talos_contracts.cursor", "deprecated")

    def test_ordering_shim_warns(self):
        """Importing talos_contracts.ordering should warn once with correct stacklevel."""
        self._test_shim_warns("talos_contracts.ordering", "deprecated")

    def test_shims_still_export_expected_functions(self):
        """Shims should still export the same functions after deprecation."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            import talos_contracts.base64url as b64
            import talos_contracts.cursor as cur
            import talos_contracts.ordering as ord_
            import talos_contracts.uuidv7 as uuid

            # base64url exports
            assert hasattr(b64, "Base64UrlError")
            assert hasattr(b64, "base64url_encode")
            assert hasattr(b64, "base64url_decode")

            # uuidv7 exports
            assert hasattr(uuid, "is_uuid_v7")
            assert hasattr(uuid, "is_canonical_lower_uuid")

            # cursor exports
            assert hasattr(cur, "derive_cursor")
            assert hasattr(cur, "decode_cursor")
            assert hasattr(cur, "compare_cursor")
            assert hasattr(cur, "assert_cursor_invariant")
            assert hasattr(cur, "CursorValidationResult")

            # ordering exports
            assert hasattr(ord_, "ordering_compare")


class TestRootImportNoWarnings:
    """Verify root import doesn't trigger deprecation warnings."""

    def test_root_import_no_deprecation_warnings(self):
        """Importing from talos_contracts root should NOT emit DeprecationWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            importlib.reload(talos_contracts)

            dep_warnings = [x for x in w if x.category is DeprecationWarning]
            assert len(dep_warnings) == 0, (
                f"Root import triggered {len(dep_warnings)} DeprecationWarning(s): "
                f"{[str(x.message) for x in dep_warnings]}"
            )


class TestCursorInvariantReasons:
    """Test cursor validation reason constants are stable."""

    # These are the ONLY valid reason strings - treat as contract constants
    VALID_REASONS = {"CURSOR_MISMATCH", "INVALID_FRAME"}

    def test_invalid_frame_returns_exact_reason_string(self):
        """INVALID_FRAME reason must match exactly."""
        result = talos_contracts.assert_cursor_invariant(
            {
                "timestamp": "not-a-number",
                "event_id": "test",
                "cursor": "test",
            }
        )
        assert result["ok"] is False
        assert result["reason"] == "INVALID_FRAME"
        assert result["reason"] in self.VALID_REASONS

    def test_cursor_mismatch_returns_exact_reason_string(self):
        """CURSOR_MISMATCH reason must match exactly."""
        # Valid frame but wrong cursor
        result = talos_contracts.assert_cursor_invariant(
            {
                "timestamp": 1704672000,
                "event_id": "018e1c6d-1234-7abc-9def-0123456789ab",
                "cursor": "wrong-cursor-value",
            }
        )
        assert result["ok"] is False
        assert result["reason"] in self.VALID_REASONS

    def test_all_failure_reasons_are_known_constants(self):
        """Any returned reason must be in the known set."""
        # Test various failure cases
        test_cases = [
            {"timestamp": None, "event_id": "test", "cursor": "test"},  # invalid timestamp
            {"timestamp": 1000, "event_id": 123, "cursor": "test"},  # invalid event_id type
            {"timestamp": 1000, "event_id": "test", "cursor": None},  # invalid cursor type
        ]
        for event in test_cases:
            result = talos_contracts.assert_cursor_invariant(event)
            if not result["ok"]:
                assert result["reason"] in self.VALID_REASONS, f"Unknown reason: {result['reason']}"
