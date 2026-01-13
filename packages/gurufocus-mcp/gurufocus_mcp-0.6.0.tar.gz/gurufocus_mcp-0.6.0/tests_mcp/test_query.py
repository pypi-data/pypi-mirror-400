"""Tests for JMESPath query functionality."""

import pytest
from pydantic import BaseModel

from gurufocus_mcp.query import QUERY_EXAMPLES, apply_query


class TestApplyQuery:
    """Tests for apply_query function."""

    def test_apply_query_with_dict_returns_filtered_data(self) -> None:
        """Test that apply_query filters dict data correctly."""
        data = {"items": [{"a": 1}, {"a": 2}, {"a": 3}], "count": 3}

        result = apply_query(data, "items[:2]")

        assert result == [{"a": 1}, {"a": 2}]

    def test_apply_query_with_pydantic_model(self) -> None:
        """Test that apply_query works with Pydantic models."""

        class TestModel(BaseModel):
            items: list[dict]
            count: int

        model = TestModel(items=[{"a": 1}, {"a": 2}, {"a": 3}], count=3)

        result = apply_query(model, "items[*].a")

        assert result == [1, 2, 3]

    def test_apply_query_with_none_returns_full_data(self) -> None:
        """Test that apply_query with None query returns full data."""
        data = {"items": [1, 2, 3]}

        result = apply_query(data, None)

        assert result == {"items": [1, 2, 3]}

    def test_apply_query_projection(self) -> None:
        """Test JMESPath projection queries."""
        data = {
            "periods": [
                {"period": "2024", "revenue": 100, "profit": 20},
                {"period": "2023", "revenue": 90, "profit": 15},
            ]
        }

        result = apply_query(data, "periods[*].{period: period, revenue: revenue}")

        assert result == [
            {"period": "2024", "revenue": 100},
            {"period": "2023", "revenue": 90},
        ]

    def test_apply_query_filter_expression(self) -> None:
        """Test JMESPath filter expressions."""
        data = {"items": [{"type": "buy", "amount": 100}, {"type": "sell", "amount": 50}]}

        result = apply_query(data, "items[?type=='buy']")

        assert result == [{"type": "buy", "amount": 100}]

    def test_apply_query_nested_access(self) -> None:
        """Test nested field access."""
        data = {"company": {"financials": {"revenue": 1000}}}

        result = apply_query(data, "company.financials.revenue")

        assert result == 1000

    def test_apply_query_invalid_syntax_raises_value_error(self) -> None:
        """Test that invalid JMESPath syntax raises ValueError."""
        data = {"items": [1, 2, 3]}

        with pytest.raises(ValueError, match="Invalid JMESPath query"):
            apply_query(data, "[[[invalid")

    def test_apply_query_returns_none_for_nonexistent_path(self) -> None:
        """Test that non-existent paths return None."""
        data = {"items": [1, 2, 3]}

        result = apply_query(data, "nonexistent")

        assert result is None


class TestQueryExamples:
    """Tests for QUERY_EXAMPLES documentation."""

    def test_query_examples_has_financials(self) -> None:
        """Test that financials examples are provided."""
        assert "financials" in QUERY_EXAMPLES
        assert "recent_5_periods" in QUERY_EXAMPLES["financials"]
        assert "revenue_trend" in QUERY_EXAMPLES["financials"]

    def test_query_examples_has_keyratios(self) -> None:
        """Test that keyratios examples are provided."""
        assert "keyratios" in QUERY_EXAMPLES
        assert "profitability" in QUERY_EXAMPLES["keyratios"]
        assert "valuation" in QUERY_EXAMPLES["keyratios"]

    def test_query_examples_has_ohlc(self) -> None:
        """Test that ohlc examples are provided."""
        assert "ohlc" in QUERY_EXAMPLES
        assert "recent_5_bars" in QUERY_EXAMPLES["ohlc"]
        assert "close_prices" in QUERY_EXAMPLES["ohlc"]

    def test_query_examples_are_valid_jmespath(self) -> None:
        """Test that all example queries are valid JMESPath syntax."""
        import jmespath

        for _category, examples in QUERY_EXAMPLES.items():
            for _name, query in examples.items():
                # Should not raise
                jmespath.compile(query)
