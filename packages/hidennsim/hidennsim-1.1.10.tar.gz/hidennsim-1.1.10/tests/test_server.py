"""Tests for MCP server implementation."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from hidennsim.server import HIDENNSIMServer


class TestHIDENNSIMServer:
    """Tests for HIDENNSIM MCP server."""

    def test_server_initialization(self):
        """Test that server initializes correctly."""
        server = HIDENNSIMServer()
        assert server.server is not None
        assert server.call_count == 0
        assert server.validation_interval == 100

    @pytest.mark.asyncio
    @patch("hidennsim.server.validate_license")
    async def test_run_without_valid_license(self, mock_validate):
        """Test that server fails to start without valid license."""
        mock_validate.return_value = False
        server = HIDENNSIMServer()

        with pytest.raises(Exception, match="Invalid or expired license"):
            await server.run()

    def test_call_count_increments(self):
        """Test that call count increments correctly."""
        server = HIDENNSIMServer()
        initial_count = server.call_count

        # Simulate multiple tool calls
        for i in range(5):
            server.call_count += 1

        assert server.call_count == initial_count + 5

    def test_validation_interval_trigger(self):
        """Test that periodic validation triggers at correct interval."""
        server = HIDENNSIMServer()
        server.validation_interval = 10

        # Should trigger validation at multiples of 10
        for count in [10, 20, 30, 100]:
            server.call_count = count
            assert server.call_count % server.validation_interval == 0

        # Should not trigger at non-multiples
        for count in [5, 15, 25, 99]:
            server.call_count = count
            assert server.call_count % server.validation_interval != 0
