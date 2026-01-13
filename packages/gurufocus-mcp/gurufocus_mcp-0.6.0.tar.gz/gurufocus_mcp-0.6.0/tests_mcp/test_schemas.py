"""Tests for schema resources."""

import pytest
from fastmcp.client import Client

from gurufocus_mcp.config import MCPServerSettings
from gurufocus_mcp.server import create_server


@pytest.fixture
def server(monkeypatch: pytest.MonkeyPatch):
    """Create a test server."""
    monkeypatch.setenv("GURUFOCUS_API_TOKEN", "test-token")
    settings = MCPServerSettings(api_token="test-token")
    return create_server(settings)


@pytest.fixture
async def client(server):
    """Create a client connected to the test server."""
    async with Client(server) as client:
        yield client


class TestListAllSchemas:
    """Tests for gurufocus://schemas resource."""

    @pytest.mark.asyncio
    async def test_list_schemas_returns_metadata(self, client: Client) -> None:
        """Test that list_all_schemas returns schema metadata."""
        result = await client.read_resource("gurufocus://schemas")

        # Result is a list with one item containing the JSON
        assert len(result) == 1
        content = result[0].text
        assert "total_schemas" in content
        assert "categories" in content
        assert "all_schemas" in content

    @pytest.mark.asyncio
    async def test_list_schemas_includes_categories(self, client: Client) -> None:
        """Test that categories are included in schema listing."""
        result = await client.read_resource("gurufocus://schemas")

        content = result[0].text
        # Check for expected categories
        assert "stock_fundamentals" in content
        assert "ratios" in content
        assert "dividends" in content


class TestGetSchema:
    """Tests for gurufocus://schemas/{model_name} resource."""

    @pytest.mark.asyncio
    async def test_get_schema_returns_json_schema(self, client: Client) -> None:
        """Test that get_schema returns a valid JSON schema."""
        result = await client.read_resource("gurufocus://schemas/StockSummary")

        assert len(result) == 1
        content = result[0].text
        assert "model_name" in content
        assert "StockSummary" in content
        assert "schema" in content

    @pytest.mark.asyncio
    async def test_get_schema_includes_python_import(self, client: Client) -> None:
        """Test that schema includes python import path."""
        result = await client.read_resource("gurufocus://schemas/KeyRatios")

        content = result[0].text
        assert "python_import" in content
        assert "from gurufocus_api.models import KeyRatios" in content

    @pytest.mark.asyncio
    async def test_get_schema_unknown_model_raises_error(self, client: Client) -> None:
        """Test that unknown model name raises an error."""
        with pytest.raises(Exception, match="Unknown model"):
            await client.read_resource("gurufocus://schemas/NonExistentModel")

    @pytest.mark.asyncio
    async def test_get_schema_suggestions_on_error(self, client: Client) -> None:
        """Test that error includes suggestions for similar names."""
        with pytest.raises(Exception, match="Did you mean"):
            await client.read_resource("gurufocus://schemas/stocksummary")

    @pytest.mark.asyncio
    async def test_get_various_schemas(self, client: Client) -> None:
        """Test fetching various schema types."""
        schemas_to_test = [
            "DividendHistory",
            "FinancialStatements",
            "OHLCHistory",
            "GuruList",
            "InsiderUpdatesResponse",
        ]

        for schema_name in schemas_to_test:
            result = await client.read_resource(f"gurufocus://schemas/{schema_name}")
            assert len(result) == 1
            assert schema_name in result[0].text


class TestGetCategorySchemas:
    """Tests for gurufocus://schemas/category/{category_name} resource."""

    @pytest.mark.asyncio
    async def test_get_category_returns_schemas(self, client: Client) -> None:
        """Test that category resource returns schemas."""
        result = await client.read_resource("gurufocus://schemas/category/stock_fundamentals")

        assert len(result) == 1
        content = result[0].text
        assert "category" in content
        assert "stock_fundamentals" in content
        assert "schemas" in content

    @pytest.mark.asyncio
    async def test_get_category_includes_model_count(self, client: Client) -> None:
        """Test that category includes model count."""
        result = await client.read_resource("gurufocus://schemas/category/ratios")

        content = result[0].text
        assert "model_count" in content

    @pytest.mark.asyncio
    async def test_get_category_unknown_raises_error(self, client: Client) -> None:
        """Test that unknown category raises an error."""
        with pytest.raises(Exception, match="Unknown category"):
            await client.read_resource("gurufocus://schemas/category/nonexistent")

    @pytest.mark.asyncio
    async def test_get_various_categories(self, client: Client) -> None:
        """Test fetching various categories."""
        categories_to_test = [
            "stock_fundamentals",
            "ratios",
            "price_volume",
            "dividends",
            "guru_institutional",
            "insider",
        ]

        for category in categories_to_test:
            result = await client.read_resource(f"gurufocus://schemas/category/{category}")
            assert len(result) == 1
            assert category in result[0].text
