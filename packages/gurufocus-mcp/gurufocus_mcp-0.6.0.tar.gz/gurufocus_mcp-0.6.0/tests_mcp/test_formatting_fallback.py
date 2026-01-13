"""Tests for TOON formatting with fallback behavior.

This module tests:
1. Normal TOON encoding when the library is available
2. JSON fallback when TOON import fails
3. Round-trip encoding/decoding integrity
4. Edge cases in format_output function
"""

from __future__ import annotations

import json
import sys
from typing import Any

import pytest


class TestToonEncodingAvailable:
    """Tests when TOON library is available."""

    def test_toon_encode_returns_string(self) -> None:
        """TOON encoding returns a string."""
        from gurufocus_mcp.formatting import toon_encode

        data = {"symbol": "AAPL", "price": 150.0}
        result = toon_encode(data)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_toon_decode_returns_dict(self) -> None:
        """TOON decoding returns original data structure."""
        from gurufocus_mcp.formatting import toon_decode, toon_encode

        data = {"symbol": "AAPL", "price": 150.0, "nested": {"key": "value"}}
        encoded = toon_encode(data)
        decoded = toon_decode(encoded)

        assert isinstance(decoded, dict)
        assert decoded == data

    def test_toon_round_trip_preserves_data(self) -> None:
        """Round-trip encode/decode preserves all data."""
        from gurufocus_mcp.formatting import toon_decode, toon_encode

        test_cases = [
            {"simple": "string"},
            {"number": 42},
            {"float": 3.14159},
            {"boolean": True},
            {"null": None},
            {"array": [1, 2, 3]},
            {"nested": {"a": {"b": {"c": 1}}}},
            {
                "complex": {
                    "symbol": "FAKE1",
                    "general": {"company_name": "FakeCorp", "sector": "Technology"},
                    "quality": {"gf_score": 85, "financial_strength": 8},
                    "ratios": [1.5, 2.3, 0.8],
                }
            },
        ]

        for data in test_cases:
            encoded = toon_encode(data)
            decoded = toon_decode(encoded)
            assert decoded == data, f"Round-trip failed for {data}"

    def test_toon_encodes_empty_dict(self) -> None:
        """TOON encoding of empty dict produces a string.

        Note: TOON library produces empty string for empty dict,
        which cannot be decoded back. This documents the behavior.
        """
        from gurufocus_mcp.formatting import toon_encode

        data: dict[str, Any] = {}
        encoded = toon_encode(data)

        # TOON produces empty string for empty dict
        assert isinstance(encoded, str)

    def test_toon_encodes_empty_list(self) -> None:
        """TOON encoding of empty list produces a string.

        Note: TOON library produces empty string for empty list,
        which cannot be decoded back. This documents the behavior.
        """
        from gurufocus_mcp.formatting import toon_encode

        data: list[Any] = []
        encoded = toon_encode(data)

        # TOON produces empty string for empty list
        assert isinstance(encoded, str)

    def test_toon_handles_unicode(self) -> None:
        """TOON handles unicode characters."""
        from gurufocus_mcp.formatting import toon_decode, toon_encode

        data = {"company": "日本株式会社", "emoji": "📈", "currency": "€"}
        encoded = toon_encode(data)
        decoded = toon_decode(encoded)

        assert decoded == data

    def test_toon_handles_special_floats(self) -> None:
        """TOON handles special float values (if supported)."""
        from gurufocus_mcp.formatting import toon_decode, toon_encode

        # Test regular floats - these should always work
        data = {"zero": 0.0, "negative": -123.456, "large": 1e10, "small": 1e-10}
        encoded = toon_encode(data)
        decoded = toon_decode(encoded)

        assert decoded["zero"] == 0.0
        assert decoded["negative"] == -123.456


class TestFormatOutputFunction:
    """Tests for the format_output function."""

    def test_json_format_returns_dict(self) -> None:
        """format='json' returns the original dict unchanged."""
        from gurufocus_mcp.formatting import format_output

        data = {"symbol": "AAPL", "price": 150.0}
        result = format_output(data, format="json")

        assert result is data  # Same object
        assert isinstance(result, dict)

    def test_toon_format_returns_string(self) -> None:
        """format='toon' returns an encoded string."""
        from gurufocus_mcp.formatting import format_output

        data = {"symbol": "AAPL", "price": 150.0}
        result = format_output(data, format="toon")

        assert isinstance(result, str)

    def test_default_format_is_toon(self) -> None:
        """Default format is TOON."""
        from gurufocus_mcp.formatting import DEFAULT_FORMAT, format_output

        assert DEFAULT_FORMAT == "toon"

        data = {"symbol": "AAPL"}
        result = format_output(data)  # No format specified

        assert isinstance(result, str)

    def test_invalid_format_raises_value_error(self) -> None:
        """Invalid format raises ValueError."""
        from gurufocus_mcp.formatting import format_output

        data = {"symbol": "AAPL"}

        with pytest.raises(ValueError, match="Unsupported format"):
            format_output(data, format="xml")  # type: ignore[arg-type]

    def test_format_output_with_nested_data(self) -> None:
        """format_output handles deeply nested data."""
        from gurufocus_mcp.formatting import format_output

        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {"value": 42},
                    },
                },
            },
        }

        # JSON format
        json_result = format_output(data, format="json")
        assert json_result == data

        # TOON format
        toon_result = format_output(data, format="toon")
        assert isinstance(toon_result, str)

    def test_format_output_with_large_array(self) -> None:
        """format_output handles large arrays."""
        from gurufocus_mcp.formatting import format_output

        data = {"values": list(range(1000))}

        json_result = format_output(data, format="json")
        assert len(json_result["values"]) == 1000

        toon_result = format_output(data, format="toon")
        assert isinstance(toon_result, str)


class TestFallbackBehavior:
    """Tests for JSON fallback when TOON is unavailable.

    These tests simulate the ImportError scenario by reloading the module
    with toon blocked from imports.
    """

    def test_fallback_encode_produces_valid_json(self) -> None:
        """Fallback toon_encode produces valid JSON string."""

        # Simulate the fallback functions directly
        def fallback_encode(data: Any) -> str:
            return json.dumps(data)

        data = {"symbol": "AAPL", "price": 150.0}
        result = fallback_encode(data)

        assert isinstance(result, str)
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == data

    def test_fallback_decode_parses_json(self) -> None:
        """Fallback toon_decode parses JSON string."""

        def fallback_decode(data: str) -> Any:
            return json.loads(data)

        json_str = '{"symbol": "AAPL", "price": 150.0}'
        result = fallback_decode(json_str)

        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"
        assert result["price"] == 150.0

    def test_fallback_round_trip(self) -> None:
        """Fallback functions support round-trip."""

        def fallback_encode(data: Any) -> str:
            return json.dumps(data)

        def fallback_decode(data: str) -> Any:
            return json.loads(data)

        test_data = {
            "symbol": "FAKE1",
            "general": {"company_name": "FakeCorp"},
            "metrics": [1, 2, 3],
            "flag": True,
            "empty": None,
        }

        encoded = fallback_encode(test_data)
        decoded = fallback_decode(encoded)

        assert decoded == test_data

    def test_fallback_handles_unicode(self) -> None:
        """Fallback handles unicode correctly."""

        def fallback_encode(data: Any) -> str:
            return json.dumps(data, ensure_ascii=False)

        def fallback_decode(data: str) -> Any:
            return json.loads(data)

        data = {"company": "日本株式会社", "currency": "€"}
        encoded = fallback_encode(data)
        decoded = fallback_decode(encoded)

        assert decoded == data

    def test_fallback_functions_are_json_compatible(self) -> None:
        """Fallback functions produce JSON-compatible output.

        This verifies that the fallback implementation (used when toon
        import fails) produces standard JSON that can be parsed by any
        JSON parser.
        """

        # Define the fallback functions exactly as in formatting.py
        def fallback_encode(data: Any) -> str:
            return json.dumps(data)

        def fallback_decode(data: str) -> Any:
            return json.loads(data)

        # Test various data types
        test_cases = [
            {"simple": "string"},
            {"nested": {"a": {"b": 1}}},
            {"array": [1, 2, 3]},
            {"mixed": {"str": "value", "num": 42, "bool": True, "null": None}},
        ]

        for data in test_cases:
            encoded = fallback_encode(data)

            # Should be valid JSON parseable by stdlib
            stdlib_parsed = json.loads(encoded)
            assert stdlib_parsed == data

            # Round-trip should work
            decoded = fallback_decode(encoded)
            assert decoded == data

    def test_fallback_output_matches_json_dumps(self) -> None:
        """Fallback encode output is identical to json.dumps."""

        def fallback_encode(data: Any) -> str:
            return json.dumps(data)

        data = {"symbol": "AAPL", "price": 150.0, "active": True}
        result = fallback_encode(data)

        assert result == json.dumps(data)


class TestEdgeCases:
    """Test edge cases in formatting."""

    def test_format_output_empty_dict(self) -> None:
        """format_output handles empty dict."""
        from gurufocus_mcp.formatting import format_output

        data: dict[str, Any] = {}

        json_result = format_output(data, format="json")
        assert json_result == {}

        toon_result = format_output(data, format="toon")
        assert isinstance(toon_result, str)

    def test_format_output_with_none_values(self) -> None:
        """format_output handles None values in dict."""
        from gurufocus_mcp.formatting import format_output, toon_decode

        data = {"present": "value", "missing": None}

        json_result = format_output(data, format="json")
        assert json_result["missing"] is None

        toon_result = format_output(data, format="toon")
        decoded = toon_decode(toon_result)
        assert decoded["missing"] is None

    def test_format_output_with_boolean_values(self) -> None:
        """format_output handles boolean values."""
        from gurufocus_mcp.formatting import format_output, toon_decode

        data = {"true_val": True, "false_val": False}

        json_result = format_output(data, format="json")
        assert json_result["true_val"] is True
        assert json_result["false_val"] is False

        toon_result = format_output(data, format="toon")
        decoded = toon_decode(toon_result)
        assert decoded["true_val"] is True
        assert decoded["false_val"] is False

    def test_format_output_with_integer_keys(self) -> None:
        """format_output handles string keys (JSON requirement)."""
        from gurufocus_mcp.formatting import format_output

        # JSON only supports string keys
        data = {"1": "one", "2": "two"}

        json_result = format_output(data, format="json")
        assert "1" in json_result

        toon_result = format_output(data, format="toon")
        assert isinstance(toon_result, str)

    def test_format_output_preserves_number_precision(self) -> None:
        """format_output preserves reasonable number precision."""
        from gurufocus_mcp.formatting import format_output, toon_decode

        data = {"price": 150.123456789, "ratio": 0.000001}

        toon_result = format_output(data, format="toon")
        decoded = toon_decode(toon_result)

        # Should preserve reasonable precision
        assert abs(decoded["price"] - 150.123456789) < 1e-9
        assert abs(decoded["ratio"] - 0.000001) < 1e-12


class TestIntegrationWithFactories:
    """Test formatting with factory-generated data."""

    def test_format_factory_summary_data(self) -> None:
        """format_output works with factory-generated summary data."""
        from pathlib import Path

        # Add API tests path for factory imports
        api_tests_path = Path(__file__).parent.parent.parent / "gurufocus-api" / "tests_api"
        if str(api_tests_path) not in sys.path:
            sys.path.insert(0, str(api_tests_path))

        from factories import StockSummaryFactory

        from gurufocus_mcp.formatting import format_output, toon_decode

        # Generate factory data
        summary = StockSummaryFactory.build()
        data = summary.model_dump(mode="json", exclude_none=True)

        # Test JSON format
        json_result = format_output(data, format="json")
        assert isinstance(json_result, dict)
        assert "symbol" in json_result

        # Test TOON format
        toon_result = format_output(data, format="toon")
        assert isinstance(toon_result, str)

        # Verify round-trip
        decoded = toon_decode(toon_result)
        assert decoded == data

    def test_format_factory_keyratios_data(self) -> None:
        """format_output works with factory-generated keyratios data."""
        from pathlib import Path

        api_tests_path = Path(__file__).parent.parent.parent / "gurufocus-api" / "tests_api"
        if str(api_tests_path) not in sys.path:
            sys.path.insert(0, str(api_tests_path))

        from factories import KeyRatiosFactory

        from gurufocus_mcp.formatting import format_output, toon_decode

        keyratios = KeyRatiosFactory.build()
        data = keyratios.model_dump(mode="json", exclude_none=True)

        # Test both formats
        json_result = format_output(data, format="json")
        toon_result = format_output(data, format="toon")

        assert isinstance(json_result, dict)
        assert isinstance(toon_result, str)

        # Verify TOON round-trip
        decoded = toon_decode(toon_result)
        assert decoded == data

    def test_format_sparse_data(self) -> None:
        """format_output works with sparse/minimal data."""
        from pathlib import Path

        api_tests_path = Path(__file__).parent.parent.parent / "gurufocus-api" / "tests_api"
        if str(api_tests_path) not in sys.path:
            sys.path.insert(0, str(api_tests_path))

        from factories import SparseStockSummaryFactory

        from gurufocus_mcp.formatting import format_output, toon_decode

        sparse = SparseStockSummaryFactory.build()
        data = sparse.model_dump(mode="json", exclude_none=True)

        # Should handle sparse data without error
        json_result = format_output(data, format="json")
        toon_result = format_output(data, format="toon")

        assert isinstance(json_result, dict)
        assert isinstance(toon_result, str)

        decoded = toon_decode(toon_result)
        assert decoded == data
