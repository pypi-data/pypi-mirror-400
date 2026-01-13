"""Tests for MCP resources."""

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


class TestResourceRegistration:
    """Tests for resource registration."""

    def test_schema_resources_registered(self, server) -> None:
        """Test that schema resources are registered."""
        resource_count = len(server._resource_manager._resources)
        # 1 static resource: list_all_schemas (gurufocus://schemas)
        assert resource_count == 1

    def test_schema_templates_registered(self, server) -> None:
        """Test that schema resource templates are registered."""
        template_count = len(server._resource_manager._templates)
        # 2 templates: get_schema, get_category_schemas
        assert template_count == 2


class TestResourceDiscovery:
    """Tests for resource discovery via MCP protocol."""

    @pytest.mark.asyncio
    async def test_list_resources_includes_schemas(self, client: Client) -> None:
        """Test that list_resources returns schema resources."""
        resources = await client.list_resources()
        # 1 static resource: list_all_schemas
        assert len(resources) == 1
        assert any("schemas" in str(r.uri) for r in resources)

    @pytest.mark.asyncio
    async def test_schema_templates_via_protocol(self, client: Client) -> None:
        """Test that schema templates are returned via protocol."""
        templates = await client.list_resource_templates()
        # 2 templates for schema lookups
        assert len(templates) == 2


class TestResourceErrorHandling:
    """Tests for resource error handling."""

    @pytest.mark.asyncio
    async def test_invalid_resource_uri_raises_error(self, client: Client) -> None:
        """Test that invalid resource URI raises an error."""
        with pytest.raises(Exception, match="Unknown resource"):
            await client.read_resource("gurufocus://invalid/resource")
