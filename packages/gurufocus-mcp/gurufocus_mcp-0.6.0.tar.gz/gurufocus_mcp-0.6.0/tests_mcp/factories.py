"""MCP test factories - generates mock client responses.

This module provides factory functions for creating mock GuruFocusClient
instances with configurable responses. These are used to test MCP tool
execution without making real API calls.

Usage:
    from tests_mcp.factories import (
        create_mock_client,
        create_partial_response_client,
        create_error_client,
    )

    # Create a mock client with factory-generated data
    mock_client = create_mock_client()

    # Create with specific data overrides
    mock_client = create_mock_client(
        summary_data={"symbol": "AAPL", "company": {"name": "Apple"}}
    )

    # Create client that raises errors
    mock_client = create_error_client(httpx.TimeoutException("timeout"))

    # Monkeypatch in tests
    monkeypatch.setattr("gurufocus_mcp.tools.stocks.get_client", lambda ctx: mock_client)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

# Add the API tests directory to path so we can import factories
api_tests_path = Path(__file__).parent.parent.parent / "gurufocus-api" / "tests_api"
if str(api_tests_path) not in sys.path:
    sys.path.insert(0, str(api_tests_path))

# Import API factories (these generate realistic fake data)
from factories import (  # noqa: E402
    DistressedCompanyKeyRatiosFactory,
    EmptyKeyRatiosFactory,
    ETFListResponseFactory,
    ETFSectorWeightingResponseFactory,
    GuruListResponseFactory,
    HealthyCompanyKeyRatiosFactory,
    KeyRatiosFactory,
    SparseStockSummaryFactory,
    StockGurusResponseFactory,
    StockQuoteFactory,
    StockSummaryFactory,
)


def create_mock_client(
    summary_data: dict[str, Any] | None = None,
    quote_data: dict[str, Any] | None = None,
    keyratios_data: dict[str, Any] | None = None,
    gurus_data: dict[str, Any] | None = None,
    etf_list_data: dict[str, Any] | None = None,
    etf_sector_data: dict[str, Any] | None = None,
    gurulist_data: dict[str, Any] | None = None,
) -> MagicMock:
    """Create a mock GuruFocusClient with configurable responses.

    All data parameters are optional. If not provided, realistic fake data
    will be generated using the model factories.

    Args:
        summary_data: Override for stock summary response
        quote_data: Override for stock quote response
        keyratios_data: Override for key ratios response
        gurus_data: Override for stock gurus response
        etf_list_data: Override for ETF list response
        etf_sector_data: Override for ETF sector weighting response
        gurulist_data: Override for guru list response

    Returns:
        Configured MagicMock client with async methods

    Example:
        mock_client = create_mock_client()
        result = await mock_client.stocks.get_summary("AAPL")
        # result.model_dump() returns factory-generated data
    """
    client = MagicMock()

    # Generate data from factories if not provided
    if summary_data is None:
        summary_data = StockSummaryFactory.build().model_dump(mode="json", exclude_none=True)

    if quote_data is None:
        quote_data = StockQuoteFactory.build().model_dump(mode="json", exclude_none=True)

    if keyratios_data is None:
        keyratios_data = KeyRatiosFactory.build().model_dump(mode="json", exclude_none=True)

    if gurus_data is None:
        gurus_data = StockGurusResponseFactory.build().model_dump(mode="json", exclude_none=True)

    if etf_list_data is None:
        etf_list_data = ETFListResponseFactory.build().model_dump(mode="json", exclude_none=True)

    if etf_sector_data is None:
        etf_sector_data = ETFSectorWeightingResponseFactory.build().model_dump(
            mode="json", exclude_none=True
        )

    if gurulist_data is None:
        gurulist_data = GuruListResponseFactory.build().model_dump(mode="json", exclude_none=True)

    # Create mock response objects
    mock_summary = _create_mock_response(summary_data)
    mock_quote = _create_mock_response(quote_data)
    mock_keyratios = _create_mock_response(keyratios_data)
    mock_gurus = _create_mock_response(gurus_data)
    mock_etf_list = _create_mock_response(etf_list_data)
    mock_etf_sector = _create_mock_response(etf_sector_data)
    mock_gurulist = _create_mock_response(gurulist_data)

    # Wire up stocks endpoint
    client.stocks = MagicMock()
    client.stocks.get_summary = AsyncMock(return_value=mock_summary)
    client.stocks.get_quote = AsyncMock(return_value=mock_quote)
    client.stocks.get_keyratios = AsyncMock(return_value=mock_keyratios)
    client.stocks.get_gurus = AsyncMock(return_value=mock_gurus)
    client.stocks.get_financials = AsyncMock(return_value=mock_summary)  # Reuse summary shape
    client.stocks.get_dividend = AsyncMock(return_value=mock_summary)
    client.stocks.get_operating_data = AsyncMock(return_value=mock_summary)
    client.stocks.get_segments = AsyncMock(return_value=mock_summary)
    client.stocks.get_ownership = AsyncMock(return_value=mock_summary)
    client.stocks.get_executives = AsyncMock(return_value=mock_summary)
    client.stocks.get_trades_history = AsyncMock(return_value=mock_summary)
    client.stocks.get_indicators = AsyncMock(return_value=mock_summary)
    client.stocks.get_indicator = AsyncMock(return_value=mock_summary)
    client.stocks.get_indicator_history = AsyncMock(return_value=mock_summary)
    client.stocks.get_news_feed = AsyncMock(return_value=mock_summary)

    # Wire up gurus endpoint
    client.gurus = MagicMock()
    client.gurus.get_gurulist = AsyncMock(return_value=mock_gurulist)
    client.gurus.get_guru_picks = AsyncMock(return_value=mock_summary)
    client.gurus.get_guru_aggregated = AsyncMock(return_value=mock_summary)
    client.gurus.get_realtime_picks = AsyncMock(return_value=mock_summary)

    # Wire up ETF endpoint
    client.etfs = MagicMock()
    client.etfs.get_etf_list = AsyncMock(return_value=mock_etf_list)
    client.etfs.get_sector_weighting = AsyncMock(return_value=mock_etf_sector)

    # Wire up economic endpoint
    client.economic = MagicMock()
    client.economic.get_indicators_list = AsyncMock(return_value=mock_summary)
    client.economic.get_indicator = AsyncMock(return_value=mock_summary)
    client.economic.get_calendar = AsyncMock(return_value=mock_summary)

    # Wire up personal endpoint
    client.personal = MagicMock()
    client.personal.get_api_usage = AsyncMock(return_value=mock_summary)
    client.personal.get_user_screeners = AsyncMock(return_value=mock_summary)
    client.personal.get_portfolios = AsyncMock(return_value=mock_summary)

    # Wire up reference endpoint
    client.reference = MagicMock()
    client.reference.get_exchanges = AsyncMock(return_value=mock_summary)
    client.reference.get_indexes = AsyncMock(return_value=mock_summary)

    # Wire up politicians endpoint
    client.politicians = MagicMock()
    client.politicians.get_politicians = AsyncMock(return_value=mock_summary)
    client.politicians.get_transactions = AsyncMock(return_value=mock_summary)

    # Wire up insiders endpoint
    client.insiders = MagicMock()
    client.insiders.get_updates = AsyncMock(return_value=mock_summary)

    return client


def _create_mock_response(data: dict[str, Any]) -> MagicMock:
    """Create a mock response object with model_dump method.

    Args:
        data: Dictionary to return from model_dump()

    Returns:
        MagicMock with model_dump() configured
    """
    mock = MagicMock()
    mock.model_dump = MagicMock(return_value=data)
    return mock


def create_error_client(
    exception: Exception,
    methods: list[str] | None = None,
) -> MagicMock:
    """Create a mock client that raises exceptions.

    Use this to test error handling in MCP tools.

    Args:
        exception: Exception to raise when methods are called
        methods: List of method paths to configure (e.g., ["stocks.get_summary"])
                 If None, all stock methods will raise the exception

    Returns:
        MagicMock client that raises the specified exception

    Example:
        import httpx
        mock_client = create_error_client(httpx.TimeoutException("timeout"))

        # This will raise TimeoutException
        await mock_client.stocks.get_summary("AAPL")
    """
    client = MagicMock()

    # Default methods to configure
    if methods is None:
        methods = [
            "stocks.get_summary",
            "stocks.get_quote",
            "stocks.get_keyratios",
            "stocks.get_financials",
            "stocks.get_gurus",
            "gurus.get_gurulist",
            "etfs.get_etf_list",
        ]

    # Configure each method to raise the exception
    for method_path in methods:
        parts = method_path.split(".")
        obj = client
        for part in parts[:-1]:
            if not hasattr(obj, part) or getattr(obj, part) is None:
                setattr(obj, part, MagicMock())
            obj = getattr(obj, part)
        setattr(obj, parts[-1], AsyncMock(side_effect=exception))

    return client


def create_partial_response_client() -> MagicMock:
    """Create client returning valid 200 OK but with sparse/None data.

    This tests edge cases where API returns success but fields are missing.
    Use this to verify tools handle partial data gracefully.

    Returns:
        MagicMock client with sparse response data
    """
    # Use the sparse factory
    sparse_summary = SparseStockSummaryFactory.build().model_dump(mode="json", exclude_none=True)

    return create_mock_client(summary_data=sparse_summary)


def create_empty_response_client() -> MagicMock:
    """Create client returning completely empty responses.

    Use this to test handling of empty API responses.

    Returns:
        MagicMock client with empty dict responses
    """
    client = MagicMock()

    empty_response = _create_mock_response({})

    client.stocks = MagicMock()
    client.stocks.get_summary = AsyncMock(return_value=empty_response)
    client.stocks.get_quote = AsyncMock(return_value=empty_response)
    client.stocks.get_keyratios = AsyncMock(return_value=empty_response)

    client.gurus = MagicMock()
    client.gurus.get_gurulist = AsyncMock(return_value=empty_response)

    client.etfs = MagicMock()
    client.etfs.get_etf_list = AsyncMock(return_value=empty_response)

    return client


def create_healthy_company_client() -> MagicMock:
    """Create client returning data for a financially healthy company.

    Use this for risk analysis tests where you expect LOW risk ratings.

    Returns:
        MagicMock client with healthy company data
    """
    healthy_keyratios = HealthyCompanyKeyRatiosFactory.build().model_dump(
        mode="json", exclude_none=True
    )

    return create_mock_client(keyratios_data=healthy_keyratios)


def create_distressed_company_client() -> MagicMock:
    """Create client returning data for a financially distressed company.

    Use this for risk analysis tests where you expect HIGH risk ratings.

    Returns:
        MagicMock client with distressed company data
    """
    distressed_keyratios = DistressedCompanyKeyRatiosFactory.build().model_dump(
        mode="json", exclude_none=True
    )

    return create_mock_client(keyratios_data=distressed_keyratios)


def create_no_metrics_client() -> MagicMock:
    """Create client returning KeyRatios with all None metrics.

    Use this to test risk analysis behavior when no data is available.

    Returns:
        MagicMock client with empty metrics
    """
    empty_keyratios = EmptyKeyRatiosFactory.build().model_dump(mode="json", exclude_none=True)

    return create_mock_client(keyratios_data=empty_keyratios)


# =============================================================================
# Specific Response Builders
# =============================================================================


def build_summary_response(
    symbol: str = "FAKE1",
    company_name: str = "FakeCorp Inc.",
    current_price: float = 150.0,
    gf_score: int = 75,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build a custom stock summary response.

    This is useful when you need specific values for assertions.

    Args:
        symbol: Stock ticker symbol
        company_name: Company name
        current_price: Current stock price
        gf_score: GF Score (0-100)
        **kwargs: Additional fields to include

    Returns:
        Dictionary matching stock summary structure
    """
    base = StockSummaryFactory.build(symbol=symbol).model_dump(mode="json", exclude_none=True)

    # Override specific fields
    if "general" in base:
        base["general"]["company_name"] = company_name
        base["general"]["current_price"] = current_price
    if "quality" in base:
        base["quality"]["gf_score"] = gf_score

    # Apply any additional overrides
    for key, value in kwargs.items():
        if "." in key:
            # Handle nested keys like "general.sector"
            parts = key.split(".")
            obj = base
            for part in parts[:-1]:
                obj = obj.setdefault(part, {})
            obj[parts[-1]] = value
        else:
            base[key] = value

    return base


def build_keyratios_response(
    symbol: str = "FAKE1",
    altman_z_score: float | None = 3.0,
    piotroski_score: int | None = 7,
    debt_to_equity: float | None = 0.5,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build a custom key ratios response.

    Useful for testing specific risk scenarios.

    Args:
        symbol: Stock ticker symbol
        altman_z_score: Altman Z-Score (bankruptcy predictor)
        piotroski_score: Piotroski F-Score (0-9)
        debt_to_equity: Debt to equity ratio
        **kwargs: Additional fields

    Returns:
        Dictionary matching keyratios structure
    """
    base = KeyRatiosFactory.build(symbol=symbol).model_dump(mode="json", exclude_none=True)

    # Override specific fields
    if altman_z_score is not None:
        base["altman_z_score"] = altman_z_score
    if piotroski_score is not None:
        base["piotroski_score"] = piotroski_score
    if debt_to_equity is not None and "solvency" in base:
        base["solvency"]["debt_to_equity"] = debt_to_equity

    # Apply additional overrides
    for key, value in kwargs.items():
        if "." in key:
            parts = key.split(".")
            obj = base
            for part in parts[:-1]:
                obj = obj.setdefault(part, {})
            obj[parts[-1]] = value
        else:
            base[key] = value

    return base
