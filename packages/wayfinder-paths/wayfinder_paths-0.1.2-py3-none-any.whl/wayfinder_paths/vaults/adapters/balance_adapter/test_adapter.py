from unittest.mock import AsyncMock, patch

import pytest

from wayfinder_paths.vaults.adapters.balance_adapter.adapter import BalanceAdapter


class TestBalanceAdapter:
    """Test cases for BalanceAdapter"""

    @pytest.fixture
    def mock_wallet_client(self):
        """Mock WalletClient for testing"""
        mock_client = AsyncMock()
        return mock_client

    @pytest.fixture
    def mock_token_client(self):
        """Mock TokenClient for testing"""
        mock_client = AsyncMock()
        return mock_client

    @pytest.fixture
    def adapter(self, mock_wallet_client, mock_token_client):
        """Create a BalanceAdapter instance with mocked clients for testing"""
        with (
            patch(
                "wayfinder_paths.vaults.adapters.balance_adapter.adapter.WalletClient",
                return_value=mock_wallet_client,
            ),
            patch(
                "wayfinder_paths.vaults.adapters.balance_adapter.adapter.TokenClient",
                return_value=mock_token_client,
            ),
        ):
            return BalanceAdapter(config={})

    @pytest.mark.asyncio
    async def test_health_check(self, adapter):
        """Test adapter health check"""
        health = await adapter.health_check()
        assert isinstance(health, dict)
        assert health.get("status") in {"healthy", "unhealthy", "error"}

    @pytest.mark.asyncio
    async def test_connect(self, adapter):
        """Test adapter connection"""
        ok = await adapter.connect()
        assert isinstance(ok, bool)

    @pytest.mark.asyncio
    async def test_get_all_enriched_token_balances_for_wallet_success(
        self, adapter, mock_wallet_client
    ):
        """Test successful retrieval of enriched token balances"""
        mock_response = {
            "balances": [
                {
                    "token_id": "usd-coin-base",
                    "symbol": "USDC",
                    "balance": "1000000000",
                    "usd_value": 1000.0,
                }
            ],
            "total_usd_value": 1000.0,
        }
        mock_wallet_client.get_all_enriched_token_balances_for_wallet = AsyncMock(
            return_value=(True, mock_response)
        )

        success, data = await adapter.get_all_enriched_token_balances_for_wallet(
            wallet_address="0x1234567890123456789012345678901234567890",
            enrich=True,
        )

        assert success is True
        assert isinstance(data, (dict, tuple))
        if isinstance(data, dict):
            assert "balances" in data

    def test_adapter_type(self, adapter):
        """Test adapter has adapter_type"""
        assert adapter.adapter_type == "BALANCE"
