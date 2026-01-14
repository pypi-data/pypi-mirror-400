from unittest.mock import AsyncMock, patch

import pytest

from wayfinder_paths.vaults.adapters.hyperlend_adapter.adapter import HyperlendAdapter


class TestHyperlendAdapter:
    """Test cases for HyperlendAdapter"""

    @pytest.fixture
    def mock_hyperlend_client(self):
        """Mock HyperlendClient for testing"""
        mock_client = AsyncMock()
        return mock_client

    @pytest.fixture
    def adapter(self, mock_hyperlend_client):
        """Create a HyperlendAdapter instance with mocked client for testing"""
        with patch(
            "wayfinder_paths.vaults.adapters.hyperlend_adapter.adapter.HyperlendClient",
            return_value=mock_hyperlend_client,
        ):
            return HyperlendAdapter()

    @pytest.mark.asyncio
    async def test_get_stable_markets_success(self, adapter, mock_hyperlend_client):
        """Test successful stable markets retrieval"""
        mock_response = {
            "markets": [
                {
                    "chain_id": 999,
                    "underlying_token": "0x1234...",
                    "symbol": "USDT",
                    "apy": 0.05,
                    "available_liquidity": 1000000,
                    "buffer_bps": 100,
                    "min_buffer_tokens": 100.0,
                },
                {
                    "chain_id": 999,
                    "underlying_token": "0x5678...",
                    "symbol": "USDC",
                    "apy": 0.04,
                    "available_liquidity": 2000000,
                    "buffer_bps": 100,
                    "min_buffer_tokens": 100.0,
                },
            ]
        }
        mock_hyperlend_client.get_stable_markets = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_stable_markets(
            chain_id=999,
            required_underlying_tokens=1000.0,
            buffer_bps=100,
            min_buffer_tokens=100.0,
        )

        assert success is True
        assert data == mock_response
        mock_hyperlend_client.get_stable_markets.assert_called_once_with(
            chain_id=999,
            required_underlying_tokens=1000.0,
            buffer_bps=100,
            min_buffer_tokens=100.0,
            is_stable_symbol=None,
        )

    @pytest.mark.asyncio
    async def test_get_stable_markets_minimal_params(
        self, adapter, mock_hyperlend_client
    ):
        """Test stable markets retrieval with only required chain_id"""
        mock_response = {
            "markets": [
                {
                    "chain_id": 999,
                    "underlying_token": "0x1234...",
                    "symbol": "USDT",
                    "apy": 0.05,
                }
            ]
        }
        mock_hyperlend_client.get_stable_markets = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_stable_markets(chain_id=999)

        assert success is True
        assert data == mock_response
        mock_hyperlend_client.get_stable_markets.assert_called_once_with(
            chain_id=999,
            required_underlying_tokens=None,
            buffer_bps=None,
            min_buffer_tokens=None,
            is_stable_symbol=None,
        )

    @pytest.mark.asyncio
    async def test_get_stable_markets_partial_params(
        self, adapter, mock_hyperlend_client
    ):
        """Test stable markets retrieval with partial optional parameters"""
        mock_response = {"markets": []}
        mock_hyperlend_client.get_stable_markets = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_stable_markets(
            chain_id=999, required_underlying_tokens=500.0
        )

        assert success is True
        assert data == mock_response
        mock_hyperlend_client.get_stable_markets.assert_called_once_with(
            chain_id=999,
            required_underlying_tokens=500.0,
            buffer_bps=None,
            min_buffer_tokens=None,
            is_stable_symbol=None,
        )

    @pytest.mark.asyncio
    async def test_get_stable_markets_failure(self, adapter, mock_hyperlend_client):
        """Test stable markets retrieval failure"""
        mock_hyperlend_client.get_stable_markets = AsyncMock(
            side_effect=Exception("API Error: Connection timeout")
        )

        success, data = await adapter.get_stable_markets(chain_id=999)

        assert success is False
        assert "API Error: Connection timeout" in data

    @pytest.mark.asyncio
    async def test_get_stable_markets_http_error(self, adapter, mock_hyperlend_client):
        """Test stable markets retrieval with HTTP error"""
        mock_hyperlend_client.get_stable_markets = AsyncMock(
            side_effect=Exception("HTTP 404 Not Found")
        )

        success, data = await adapter.get_stable_markets(chain_id=999)

        assert success is False
        assert "404" in data or "Not Found" in data

    @pytest.mark.asyncio
    async def test_get_stable_markets_empty_response(
        self, adapter, mock_hyperlend_client
    ):
        """Test stable markets retrieval with empty response"""
        mock_response = {"markets": []}
        mock_hyperlend_client.get_stable_markets = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_stable_markets(chain_id=999)

        assert success is True
        assert data == mock_response
        assert len(data.get("markets", [])) == 0

    def test_adapter_type(self, adapter):
        """Test adapter has adapter_type"""
        assert adapter.adapter_type == "HYPERLEND"

    @pytest.mark.asyncio
    async def test_health_check(self, adapter):
        """Test adapter health check"""
        health = await adapter.health_check()
        assert isinstance(health, dict)
        assert health.get("status") in {"healthy", "unhealthy", "error"}
        assert health.get("adapter") == "HYPERLEND"

    @pytest.mark.asyncio
    async def test_connect(self, adapter):
        """Test adapter connection"""
        ok = await adapter.connect()
        assert isinstance(ok, bool)
        assert ok is True

    @pytest.mark.asyncio
    async def test_get_stable_markets_with_is_stable_symbol(
        self, adapter, mock_hyperlend_client
    ):
        """Test stable markets retrieval with is_stable_symbol parameter"""
        mock_response = {
            "markets": [
                {
                    "chain_id": 999,
                    "underlying_token": "0x1234...",
                    "symbol": "USDT",
                    "apy": 0.05,
                }
            ]
        }
        mock_hyperlend_client.get_stable_markets = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_stable_markets(
            chain_id=999, is_stable_symbol=True
        )

        assert success is True
        assert data == mock_response
        mock_hyperlend_client.get_stable_markets.assert_called_once_with(
            chain_id=999,
            required_underlying_tokens=None,
            buffer_bps=None,
            min_buffer_tokens=None,
            is_stable_symbol=True,
        )

    @pytest.mark.asyncio
    async def test_get_assets_view_success(self, adapter, mock_hyperlend_client):
        """Test successful assets view retrieval"""
        mock_response = {
            "assets": [
                {
                    "token_address": "0x1234...",
                    "symbol": "USDT",
                    "balance": "1000.0",
                    "supplied": "500.0",
                    "borrowed": "0.0",
                }
            ],
            "total_value": 1000.0,
        }
        mock_hyperlend_client.get_assets_view = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_assets_view(
            chain_id=999,
            user_address="0x0c737cB5934afCb5B01965141F865F795B324080",
        )

        assert success is True
        assert data == mock_response
        mock_hyperlend_client.get_assets_view.assert_called_once_with(
            chain_id=999,
            user_address="0x0c737cB5934afCb5B01965141F865F795B324080",
        )

    @pytest.mark.asyncio
    async def test_get_assets_view_failure(self, adapter, mock_hyperlend_client):
        """Test assets view retrieval failure"""
        mock_hyperlend_client.get_assets_view = AsyncMock(
            side_effect=Exception("API Error: Invalid address")
        )

        success, data = await adapter.get_assets_view(
            chain_id=999,
            user_address="0x0c737cB5934afCb5B01965141F865F795B324080",
        )

        assert success is False
        assert "API Error: Invalid address" in data

    @pytest.mark.asyncio
    async def test_get_assets_view_empty_response(self, adapter, mock_hyperlend_client):
        """Test assets view retrieval with empty response"""
        mock_response = {"assets": [], "total_value": 0.0}
        mock_hyperlend_client.get_assets_view = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_assets_view(
            chain_id=999,
            user_address="0x0c737cB5934afCb5B01965141F865F795B324080",
        )

        assert success is True
        assert data == mock_response
        assert len(data.get("assets", [])) == 0
        assert data.get("total_value") == 0.0
