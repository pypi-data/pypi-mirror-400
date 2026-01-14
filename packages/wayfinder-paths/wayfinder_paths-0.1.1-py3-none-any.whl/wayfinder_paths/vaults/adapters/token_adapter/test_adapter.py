from unittest.mock import patch

import pytest

from wayfinder_paths.vaults.adapters.token_adapter.adapter import TokenAdapter


class TestTokenAdapter:
    """Test cases for TokenAdapter"""

    @pytest.fixture
    def adapter(self):
        return TokenAdapter()

    def test_init_with_default_config(self):
        """Test adapter initialization with default config"""
        adapter = TokenAdapter()
        assert adapter.adapter_type == "TOKEN"
        assert adapter.token_client is not None

    @pytest.mark.asyncio
    async def test_get_token_success(self, adapter):
        """Test successful token retrieval by address"""
        mock_token_data = {
            "address": "0x1234...",
            "symbol": "TEST",
            "name": "Test Token",
            "decimals": 18,
        }

        with patch.object(
            adapter.token_client, "get_token_details", return_value=mock_token_data
        ):
            success, data = await adapter.get_token("0x1234...")

            assert success is True
            assert data == mock_token_data

    @pytest.mark.asyncio
    async def test_get_token_not_found(self, adapter):
        """Test token not found by address"""
        with patch.object(adapter.token_client, "get_token_details", return_value=None):
            success, data = await adapter.get_token("0x1234...")

            assert success is False
            assert "No token found for address" in data

    @pytest.mark.asyncio
    async def test_get_token_flexible_success(self, adapter):
        """Test flexible token retrieval with both address and token_id"""
        mock_token_data = {"address": "0x1234...", "symbol": "TEST"}

        with patch.object(
            adapter.token_client, "get_token_details", return_value=mock_token_data
        ):
            success, data = await adapter.get_token(
                address="0x1234...", token_id="token-123"
            )

            assert success is True
            assert data == mock_token_data

    @pytest.mark.asyncio
    async def test_get_token_no_parameters(self, adapter):
        """Test get_token with no parameters raises error"""
        success, data = await adapter.get_token()

        assert success is False
        assert "Either address or token_id must be provided" in data

    def test_adapter_type(self, adapter):
        """Test adapter has adapter_type"""
        assert adapter.adapter_type == "TOKEN"

    @pytest.mark.asyncio
    async def test_get_token_price_success(self, adapter):
        """Test successful token price retrieval"""
        mock_token_data = {
            "current_price": 1.50,
            "price_change_24h": 0.05,
            "price_change_percentage_24h": 3.45,
            "market_cap": 1000000,
            "total_volume": 50000,
            "symbol": "TEST",
            "name": "Test Token",
            "address": "0x1234...",
        }

        with patch.object(
            adapter.token_client, "get_token_details", return_value=mock_token_data
        ):
            success, data = await adapter.get_token_price("test-token")

            assert success is True
            assert data["current_price"] == 1.50
            assert data["symbol"] == "TEST"
            assert data["name"] == "Test Token"

    @pytest.mark.asyncio
    async def test_get_token_price_not_found(self, adapter):
        """Test token price not found"""
        with patch.object(adapter.token_client, "get_token_details", return_value=None):
            success, data = await adapter.get_token_price("invalid-token")

            assert success is False
            assert "No token found for" in data

    @pytest.mark.asyncio
    async def test_get_gas_token_success(self, adapter):
        """Test successful gas token retrieval"""
        mock_gas_token_data = {
            "id": "ethereum-base",
            "symbol": "ETH",
            "name": "Ethereum",
            "address": "0x0000000000000000000000000000000000000000",
            "decimals": 18,
        }

        with patch.object(
            adapter.token_client, "get_gas_token", return_value=mock_gas_token_data
        ):
            success, data = await adapter.get_gas_token("base")

            assert success is True
            assert data["symbol"] == "ETH"
            assert data["name"] == "Ethereum"

    @pytest.mark.asyncio
    async def test_get_gas_token_not_found(self, adapter):
        """Test gas token not found"""
        with patch.object(adapter.token_client, "get_gas_token", return_value=None):
            success, data = await adapter.get_gas_token("invalid-chain")

            assert success is False
            assert "No gas token found for chain" in data
