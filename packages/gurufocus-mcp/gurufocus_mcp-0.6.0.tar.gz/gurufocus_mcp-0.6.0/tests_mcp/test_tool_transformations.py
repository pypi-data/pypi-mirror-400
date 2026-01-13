"""Tests for MCP tool input/output transformations.

These tests focus on HOW data is transformed, not WHETHER mocks are called.
Key areas tested:
1. Input transformations: Symbol normalization, validation edge cases
2. Output transformations: Partial data handling, None field behavior
3. Error transformations: API errors → ToolError conversion
4. Format transformations: TOON vs JSON output differences
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastmcp.client import Client
from fastmcp.exceptions import ToolError

from gurufocus_api.exceptions import (
    AuthenticationError,
    InvalidSymbolError,
    NetworkError,
    NotFoundError,
    RateLimitError,
)
from gurufocus_mcp.config import MCPServerSettings
from gurufocus_mcp.server import create_server


def extract_result(result: Any) -> Any:
    """Extract the actual data from a CallToolResult.

    The FastMCP Client.call_tool() returns a CallToolResult object
    with a 'data' attribute containing the actual result.
    """
    if hasattr(result, "data"):
        return result.data
    return result


# Add the API tests directory to path for factory imports
api_tests_path = Path(__file__).parent.parent.parent / "gurufocus-api" / "tests_api"
if str(api_tests_path) not in sys.path:
    sys.path.insert(0, str(api_tests_path))

# Import factories
from factories import (  # noqa: E402
    KeyRatiosFactory,
    SparseStockSummaryFactory,
    StockQuoteFactory,
    StockSummaryFactory,
)

# Import MCP factories - use explicit module import to avoid collision
import tests_mcp.factories as mcp_factories  # noqa: E402


def _create_mock_response(data: dict[str, Any]) -> MagicMock:
    """Create a mock response object with model_dump method."""
    mock = MagicMock()
    mock.model_dump = MagicMock(return_value=data)
    return mock


class TestSymbolInputTransformation:
    """Tests for symbol input normalization and validation."""

    @pytest.fixture
    def server(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("GURUFOCUS_API_TOKEN", "test-token")
        return create_server(MCPServerSettings(api_token="test-token"))

    @pytest.fixture
    async def client(self, server):
        async with Client(server) as client:
            yield client

    @pytest.mark.asyncio
    async def test_lowercase_symbol_normalized_to_uppercase(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify lowercase symbols are converted to uppercase before API call."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_summary", {"symbol": "aapl"})

        # Verify the API was called with UPPERCASE
        mock_client.stocks.get_summary.assert_called_once_with("AAPL")

    @pytest.mark.asyncio
    async def test_mixed_case_symbol_normalized(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify mixed case symbols are normalized to uppercase."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_summary", {"symbol": "AaPl"})
        mock_client.stocks.get_summary.assert_called_once_with("AAPL")

    @pytest.mark.asyncio
    async def test_symbol_whitespace_stripped(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify whitespace is stripped from symbols."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_summary", {"symbol": "  AAPL  "})
        mock_client.stocks.get_summary.assert_called_once_with("AAPL")

    @pytest.mark.asyncio
    async def test_symbol_with_exchange_prefix_accepted(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify symbols like 'NYSE:IBM' are accepted and normalized."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_summary", {"symbol": "nyse:ibm"})
        mock_client.stocks.get_summary.assert_called_once_with("NYSE:IBM")

    @pytest.mark.asyncio
    async def test_symbol_with_dot_accepted(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify symbols like 'BRK.A' are accepted."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_summary", {"symbol": "brk.a"})
        mock_client.stocks.get_summary.assert_called_once_with("BRK.A")

    @pytest.mark.asyncio
    async def test_international_symbol_with_suffix_accepted(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify international symbols like 'BMW.DE' are accepted."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_summary", {"symbol": "bmw.de"})
        mock_client.stocks.get_summary.assert_called_once_with("BMW.DE")

    @pytest.mark.asyncio
    async def test_hong_kong_symbol_accepted(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify Hong Kong symbols like '0700.HK' are accepted."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_summary", {"symbol": "0700.hk"})
        mock_client.stocks.get_summary.assert_called_once_with("0700.HK")

    @pytest.mark.asyncio
    async def test_empty_symbol_raises_tool_error(self, client: Client) -> None:
        """Verify empty symbols raise ToolError without hitting API."""
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("get_stock_summary", {"symbol": ""})

        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg

    @pytest.mark.asyncio
    async def test_whitespace_only_symbol_raises_tool_error(self, client: Client) -> None:
        """Verify whitespace-only symbols are rejected."""
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("get_stock_summary", {"symbol": "   "})

        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg

    @pytest.mark.asyncio
    async def test_very_long_symbol_raises_tool_error(self, client: Client) -> None:
        """Verify very long symbols (>15 chars) are rejected."""
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("get_stock_summary", {"symbol": "AVERYLONGSYMBOLNAME"})

        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg


class TestPartialDataHandling:
    """Tests for handling partial/sparse API responses.

    These test the REAL edge cases - what happens when the API returns
    200 OK but the data is incomplete?
    """

    @pytest.fixture
    def server(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("GURUFOCUS_API_TOKEN", "test-token")
        return create_server(MCPServerSettings(api_token="test-token"))

    @pytest.fixture
    async def client(self, server):
        async with Client(server) as client:
            yield client

    @pytest.mark.asyncio
    async def test_summary_with_minimal_data_returns_dict(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test handling when API returns minimal data."""
        # Use the sparse factory
        sparse_data = SparseStockSummaryFactory.build().model_dump(mode="json", exclude_none=True)
        mock_client = mcp_factories.create_mock_client(summary_data=sparse_data)
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_summary", {"symbol": "FAKE1", "format": "json"}
        )
        result = extract_result(raw_result)

        # Should not crash, should return what's available
        assert isinstance(result, dict)
        assert result.get("symbol") is not None

    @pytest.mark.asyncio
    async def test_empty_response_handled_gracefully(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test handling when API returns empty dict."""
        mock_client = mcp_factories.create_empty_response_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_summary", {"symbol": "FAKE1", "format": "json"}
        )
        result = extract_result(raw_result)

        # Should return empty dict, not crash
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_model_dump_called_with_exclude_none(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that model_dump is called with exclude_none=True."""
        mock_response = MagicMock()
        mock_response.model_dump = MagicMock(return_value={"symbol": "FAKE1", "price": 150.0})

        mock_client = MagicMock()
        mock_client.stocks = MagicMock()
        mock_client.stocks.get_summary = AsyncMock(return_value=mock_response)

        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_summary", {"symbol": "FAKE1", "format": "json"})

        # Verify model_dump was called with proper args to exclude None values
        mock_response.model_dump.assert_called_once_with(mode="json", exclude_none=True)

    @pytest.mark.asyncio
    async def test_response_preserves_non_none_fields(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that non-None fields are preserved in response."""
        test_data = {
            "symbol": "FAKE1",
            "general": {"company_name": "FakeCorp Inc.", "sector": "Technology"},
            "quality": {"gf_score": 85, "financial_strength": 8},
        }

        mock_response = _create_mock_response(test_data)
        mock_client = MagicMock()
        mock_client.stocks = MagicMock()
        mock_client.stocks.get_summary = AsyncMock(return_value=mock_response)

        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_summary", {"symbol": "FAKE1", "format": "json"}
        )
        result = extract_result(raw_result)

        assert result["symbol"] == "FAKE1"
        assert result["general"]["company_name"] == "FakeCorp Inc."
        assert result["quality"]["gf_score"] == 85


class TestErrorTransformation:
    """Tests for API error → ToolError transformation."""

    @pytest.fixture
    def server(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("GURUFOCUS_API_TOKEN", "test-token")
        return create_server(MCPServerSettings(api_token="test-token"))

    @pytest.fixture
    async def client(self, server):
        async with Client(server) as client:
            yield client

    @pytest.mark.asyncio
    async def test_invalid_symbol_error_becomes_tool_error(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that InvalidSymbolError is converted to ToolError."""
        mock_client = mcp_factories.create_error_client(
            InvalidSymbolError("INVALID"),
            methods=["stocks.get_summary"],
        )
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("get_stock_summary", {"symbol": "INVALID"})

        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg or "not found" in error_msg

    @pytest.mark.asyncio
    async def test_authentication_error_becomes_tool_error(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that AuthenticationError is converted to ToolError."""
        mock_client = mcp_factories.create_error_client(
            AuthenticationError("Invalid token"),
            methods=["stocks.get_summary"],
        )
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("get_stock_summary", {"symbol": "FAKE1"})

        error_msg = str(exc_info.value).lower()
        assert "authentication" in error_msg or "token" in error_msg

    @pytest.mark.asyncio
    async def test_rate_limit_error_becomes_tool_error(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that RateLimitError is converted to ToolError."""
        mock_client = mcp_factories.create_error_client(
            RateLimitError("Rate limit exceeded", retry_after=60),
            methods=["stocks.get_summary"],
        )
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("get_stock_summary", {"symbol": "FAKE1"})

        error_msg = str(exc_info.value).lower()
        assert "rate limit" in error_msg

    @pytest.mark.asyncio
    async def test_not_found_error_becomes_tool_error(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that NotFoundError is converted to ToolError."""
        mock_client = mcp_factories.create_error_client(
            NotFoundError("Data not found"),
            methods=["stocks.get_summary"],
        )
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("get_stock_summary", {"symbol": "FAKE1"})

        error_msg = str(exc_info.value).lower()
        assert "not found" in error_msg

    @pytest.mark.asyncio
    async def test_network_error_becomes_tool_error(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that NetworkError is converted to ToolError."""
        mock_client = mcp_factories.create_error_client(
            NetworkError("Connection failed"),
            methods=["stocks.get_summary"],
        )
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("get_stock_summary", {"symbol": "FAKE1"})

        error_msg = str(exc_info.value).lower()
        assert "network" in error_msg or "connection" in error_msg

    @pytest.mark.asyncio
    async def test_httpx_connect_error_becomes_tool_error(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that httpx.ConnectError is wrapped in ToolError."""
        mock_client = mcp_factories.create_error_client(
            httpx.ConnectError("Connection refused"),
            methods=["stocks.get_summary"],
        )
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        with pytest.raises(ToolError):
            await client.call_tool("get_stock_summary", {"symbol": "FAKE1"})

    @pytest.mark.asyncio
    async def test_httpx_timeout_error_becomes_tool_error(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that httpx.TimeoutException is wrapped in ToolError."""
        mock_client = mcp_factories.create_error_client(
            httpx.TimeoutException("Request timed out"),
            methods=["stocks.get_summary"],
        )
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        with pytest.raises(ToolError):
            await client.call_tool("get_stock_summary", {"symbol": "FAKE1"})

    @pytest.mark.asyncio
    async def test_generic_exception_becomes_tool_error(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that unexpected exceptions become ToolError."""
        mock_client = mcp_factories.create_error_client(
            RuntimeError("Unexpected internal error"),
            methods=["stocks.get_summary"],
        )
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        with pytest.raises(ToolError):
            await client.call_tool("get_stock_summary", {"symbol": "FAKE1"})


class TestFormatTransformation:
    """Tests for TOON vs JSON format differences."""

    @pytest.fixture
    def server(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("GURUFOCUS_API_TOKEN", "test-token")
        return create_server(MCPServerSettings(api_token="test-token"))

    @pytest.fixture
    async def client(self, server):
        async with Client(server) as client:
            yield client

    @pytest.mark.asyncio
    async def test_json_format_returns_dict(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that format='json' returns a dict."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_summary", {"symbol": "FAKE1", "format": "json"}
        )
        result = extract_result(raw_result)

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_toon_format_returns_string(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that format='toon' returns a string."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_summary", {"symbol": "FAKE1", "format": "toon"}
        )
        result = extract_result(raw_result)

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_default_format_is_toon(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that omitting format defaults to TOON (string)."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_summary",
            {"symbol": "FAKE1"},  # No format specified
        )
        result = extract_result(raw_result)

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_toon_string_is_non_empty(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that TOON format produces non-empty string."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_summary", {"symbol": "FAKE1", "format": "toon"}
        )
        result = extract_result(raw_result)

        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_json_preserves_all_fields(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that JSON format preserves all non-None fields."""
        test_data = {
            "symbol": "FAKE1",
            "general": {"company_name": "FakeCorp", "sector": "Technology"},
            "quality": {"gf_score": 75},
        }

        mock_response = _create_mock_response(test_data)
        mock_client = MagicMock()
        mock_client.stocks = MagicMock()
        mock_client.stocks.get_summary = AsyncMock(return_value=mock_response)

        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_summary", {"symbol": "FAKE1", "format": "json"}
        )
        result = extract_result(raw_result)

        assert result == test_data


class TestMultipleToolsInputTransformation:
    """Tests for input transformation across multiple tool types."""

    @pytest.fixture
    def server(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("GURUFOCUS_API_TOKEN", "test-token")
        return create_server(MCPServerSettings(api_token="test-token"))

    @pytest.fixture
    async def client(self, server):
        async with Client(server) as client:
            yield client

    @pytest.mark.asyncio
    async def test_get_stock_quote_normalizes_symbol(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that get_stock_quote normalizes symbols."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_quote", {"symbol": "  msft  "})
        mock_client.stocks.get_quote.assert_called_once_with("MSFT")

    @pytest.mark.asyncio
    async def test_get_stock_keyratios_normalizes_symbol(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that get_stock_keyratios normalizes symbols."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_keyratios", {"symbol": "googl"})
        mock_client.stocks.get_keyratios.assert_called_once_with("GOOGL")

    @pytest.mark.asyncio
    async def test_get_stock_gurus_normalizes_symbol(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that get_stock_gurus normalizes symbols."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_gurus", {"symbol": "nvda"})
        mock_client.stocks.get_gurus.assert_called_once_with("NVDA")

    @pytest.mark.asyncio
    async def test_get_stock_financials_normalizes_symbol(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that get_stock_financials normalizes symbols."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool("get_stock_financials", {"symbol": "tsla"})
        mock_client.stocks.get_financials.assert_called_once_with("TSLA", period_type="annual")


class TestIndicatorKeyValidation:
    """Tests for indicator key validation in get_stock_indicator."""

    @pytest.fixture
    def server(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("GURUFOCUS_API_TOKEN", "test-token")
        return create_server(MCPServerSettings(api_token="test-token"))

    @pytest.fixture
    async def client(self, server):
        async with Client(server) as client:
            yield client

    @pytest.mark.asyncio
    async def test_empty_indicator_key_raises_error(self, client: Client) -> None:
        """Test that empty indicator key raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool("get_stock_indicator", {"symbol": "AAPL", "indicator_key": ""})

        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg or "indicator" in error_msg

    @pytest.mark.asyncio
    async def test_whitespace_indicator_key_raises_error(self, client: Client) -> None:
        """Test that whitespace-only indicator key raises ToolError."""
        with pytest.raises(ToolError) as exc_info:
            await client.call_tool(
                "get_stock_indicator", {"symbol": "AAPL", "indicator_key": "   "}
            )

        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg or "indicator" in error_msg

    @pytest.mark.asyncio
    async def test_indicator_key_normalized_to_lowercase(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that indicator keys are normalized to lowercase."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool(
            "get_stock_indicator", {"symbol": "FAKE1", "indicator_key": "NET_INCOME"}
        )
        mock_client.stocks.get_indicator.assert_called_once_with("FAKE1", "net_income")

    @pytest.mark.asyncio
    async def test_indicator_key_whitespace_stripped(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that whitespace is stripped from indicator keys."""
        mock_client = mcp_factories.create_mock_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        await client.call_tool(
            "get_stock_indicator", {"symbol": "FAKE1", "indicator_key": "  roe  "}
        )
        mock_client.stocks.get_indicator.assert_called_once_with("FAKE1", "roe")


class TestFactoryGeneratedDataIntegration:
    """Tests using factory-generated data to verify tool output transformations."""

    @pytest.fixture
    def server(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("GURUFOCUS_API_TOKEN", "test-token")
        return create_server(MCPServerSettings(api_token="test-token"))

    @pytest.fixture
    async def client(self, server):
        async with Client(server) as client:
            yield client

    @pytest.mark.asyncio
    async def test_factory_summary_through_tool(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that factory-generated summary data flows through tool correctly."""
        # Generate data using factory
        summary = StockSummaryFactory.build()
        summary_data = summary.model_dump(mode="json", exclude_none=True)

        mock_client = mcp_factories.create_mock_client(summary_data=summary_data)
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_summary", {"symbol": "FAKE1", "format": "json"}
        )
        result = extract_result(raw_result)

        # Verify factory data is preserved
        assert "symbol" in result
        assert "general" in result or "quality" in result  # Some expected fields

    @pytest.mark.asyncio
    async def test_factory_quote_through_tool(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that factory-generated quote data flows through tool correctly."""
        quote = StockQuoteFactory.build()
        quote_data = quote.model_dump(mode="json", exclude_none=True)

        mock_client = mcp_factories.create_mock_client(quote_data=quote_data)
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_quote", {"symbol": "FAKE1", "format": "json"}
        )
        result = extract_result(raw_result)

        # Verify quote-specific fields
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_factory_keyratios_through_tool(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that factory-generated keyratios data flows through tool correctly."""
        keyratios = KeyRatiosFactory.build()
        keyratios_data = keyratios.model_dump(mode="json", exclude_none=True)

        mock_client = mcp_factories.create_mock_client(keyratios_data=keyratios_data)
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_keyratios", {"symbol": "FAKE1", "format": "json"}
        )
        result = extract_result(raw_result)

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_healthy_company_client_factory(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test using healthy company factory for keyratios."""
        mock_client = mcp_factories.create_healthy_company_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_keyratios", {"symbol": "FAKE1", "format": "json"}
        )
        result = extract_result(raw_result)

        # Healthy company should have strong metrics
        assert isinstance(result, dict)
        # Check for some keyratios-specific content
        if "altman_z_score" in result:
            assert result["altman_z_score"] > 2.99  # Safe zone

    @pytest.mark.asyncio
    async def test_distressed_company_client_factory(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test using distressed company factory for keyratios."""
        mock_client = mcp_factories.create_distressed_company_client()
        monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)

        raw_result = await client.call_tool(
            "get_stock_keyratios", {"symbol": "FAKE1", "format": "json"}
        )
        result = extract_result(raw_result)

        assert isinstance(result, dict)
        # Distressed company should have weak metrics
        if "altman_z_score" in result:
            assert result["altman_z_score"] < 1.81  # Distress zone
