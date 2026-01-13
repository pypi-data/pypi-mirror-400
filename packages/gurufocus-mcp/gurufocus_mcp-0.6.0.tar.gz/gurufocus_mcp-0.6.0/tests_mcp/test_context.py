"""Tests for MCP context utilities."""

from unittest.mock import MagicMock

import pytest
from fastmcp.exceptions import ToolError

from gurufocus_mcp.context import get_client


class TestGetClient:
    """Tests for get_client helper."""

    def test_get_client_returns_client_when_initialized(self) -> None:
        """Test that get_client returns client from context when available."""
        mock_client = MagicMock()
        mock_ctx = MagicMock()
        mock_ctx.fastmcp.state = {"client": mock_client}

        result = get_client(mock_ctx)

        assert result is mock_client

    def test_get_client_raises_when_client_none(self) -> None:
        """Test that get_client raises ToolError when client is None."""
        mock_ctx = MagicMock()
        mock_ctx.fastmcp.state = {"client": None}

        with pytest.raises(ToolError) as exc_info:
            get_client(mock_ctx)

        assert "not initialized" in str(exc_info.value)
        assert "GURUFOCUS_API_TOKEN" in str(exc_info.value)

    def test_get_client_raises_when_state_missing(self) -> None:
        """Test that get_client raises ToolError when state is missing."""
        mock_ctx = MagicMock()
        mock_ctx.fastmcp.state = {}

        with pytest.raises(ToolError) as exc_info:
            get_client(mock_ctx)

        assert "not initialized" in str(exc_info.value)

    def test_get_client_handles_missing_state_attribute(self) -> None:
        """Test that get_client handles missing state attribute gracefully."""
        mock_ctx = MagicMock()
        # Make state return {} for getattr with default
        del mock_ctx.fastmcp.state  # Remove state attribute

        with pytest.raises(ToolError) as exc_info:
            get_client(mock_ctx)

        assert "not initialized" in str(exc_info.value)
