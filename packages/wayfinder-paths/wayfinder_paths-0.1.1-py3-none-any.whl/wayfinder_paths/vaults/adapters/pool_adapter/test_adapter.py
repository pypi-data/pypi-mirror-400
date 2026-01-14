from unittest.mock import AsyncMock, patch

import pytest

from wayfinder_paths.vaults.adapters.pool_adapter.adapter import PoolAdapter


class TestPoolAdapter:
    """Test cases for PoolAdapter"""

    @pytest.fixture
    def mock_pool_client(self):
        """Mock PoolClient for testing"""
        mock_client = AsyncMock()
        return mock_client

    @pytest.fixture
    def adapter(self, mock_pool_client):
        """Create a PoolAdapter instance with mocked client for testing"""
        with patch(
            "vaults.adapters.pool_adapter.adapter.PoolClient",
            return_value=mock_pool_client,
        ):
            return PoolAdapter()

    @pytest.mark.asyncio
    async def test_get_pools_by_ids_success(self, adapter, mock_pool_client):
        """Test successful pool retrieval by IDs"""
        mock_response = {
            "pools": [
                {
                    "id": "pool-123",
                    "name": "USDC/USDT Pool",
                    "symbol": "USDC-USDT",
                    "apy": 0.05,
                    "tvl": 1000000,
                }
            ]
        }
        mock_pool_client.get_pools_by_ids = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_pools_by_ids(
            pool_ids=["pool-123", "pool-456"], merge_external=True
        )

        assert success is True
        assert data == mock_response
        mock_pool_client.get_pools_by_ids.assert_called_once_with(
            pool_ids="pool-123,pool-456", merge_external=True
        )

    @pytest.mark.asyncio
    async def test_get_all_pools_success(self, adapter, mock_pool_client):
        """Test successful retrieval of all pools"""
        # Mock response
        mock_response = {
            "pools": [
                {"id": "pool-123", "name": "Pool 1"},
                {"id": "pool-456", "name": "Pool 2"},
            ],
            "total": 2,
        }
        mock_pool_client.get_all_pools = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_all_pools(merge_external=False)

        assert success is True
        assert data == mock_response
        mock_pool_client.get_all_pools.assert_called_once_with(merge_external=False)

    @pytest.mark.asyncio
    async def test_get_llama_matches_success(self, adapter, mock_pool_client):
        """Test successful Llama matches retrieval"""
        # Mock response
        mock_response = {
            "matches": [
                {
                    "id": "pool-123",
                    "llama_apy_pct": 5.2,
                    "llama_tvl_usd": 1000000,
                    "llama_stablecoin": True,
                    "network": "base",
                }
            ]
        }
        mock_pool_client.get_llama_matches = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_llama_matches()

        assert success is True
        assert data == mock_response

    @pytest.mark.asyncio
    async def test_find_high_yield_pools_success(self, adapter, mock_pool_client):
        """Test successful high yield pool discovery"""
        mock_llama_response = {
            "matches": [
                {
                    "pool_id": "pool-123",
                    "llama_apy_pct": 5.2,
                    "llama_tvl_usd": 1000000,
                    "llama_stablecoin": True,
                    "network": "base",
                },
                {
                    "pool_id": "pool-456",
                    "llama_apy_pct": 2.0,
                    "llama_tvl_usd": 500000,
                    "llama_stablecoin": True,
                    "network": "ethereum",
                },
                {
                    "pool_id": "pool-789",
                    "llama_apy_pct": 6.0,
                    "llama_tvl_usd": 2000000,
                    "llama_stablecoin": False,
                    "network": "base",
                },
            ]
        }
        mock_pool_client.get_llama_matches = AsyncMock(return_value=mock_llama_response)

        success, data = await adapter.find_high_yield_pools(
            min_apy=0.03, min_tvl=500000, stablecoin_only=True, network_codes=["base"]
        )

        assert success is True
        assert len(data["pools"]) == 1  # Only pool-123 meets criteria
        assert (
            data["pools"][0].get("pool_id") == "pool-123"
            or data["pools"][0].get("id") == "pool-123"
        )
        assert data["total_found"] == 1
        assert data["filters_applied"]["min_apy"] == 0.03
        assert data["filters_applied"]["stablecoin_only"] is True

    @pytest.mark.asyncio
    async def test_get_pool_analytics_success(self, adapter, mock_pool_client):
        """Test successful pool analytics generation"""
        mock_pool_data = {
            "pools": [
                {"id": "pool-123", "name": "USDC/USDT Pool", "symbol": "USDC-USDT"}
            ]
        }
        mock_pool_client.get_pools_by_ids = AsyncMock(return_value=mock_pool_data)

        mock_llama_data = {
            "pool-123": {
                "llama_apy_pct": 5.2,
                "llama_combined_apy_pct": 5.2,
                "llama_tvl_usd": 1000000,
            }
        }
        mock_pool_client.get_llama_reports = AsyncMock(return_value=mock_llama_data)

        success, data = await adapter.get_pool_analytics(["pool-123"])

        assert success is True
        assert len(data["analytics"]) == 1
        assert data["analytics"][0]["pool"]["id"] == "pool-123"
        assert round(data["analytics"][0]["combined_apy"], 6) == round(0.052, 6)
        assert data["analytics"][0]["tvl_usd"] == 1000000

    @pytest.mark.asyncio
    async def test_search_pools_success(self, adapter, mock_pool_client):
        """Test successful pool search"""
        mock_all_pools = {
            "pools": [
                {
                    "id": "pool-123",
                    "name": "USDC/USDT Pool",
                    "symbol": "USDC-USDT",
                    "description": "Stablecoin pool on Base",
                },
                {
                    "id": "pool-456",
                    "name": "ETH/WETH Pool",
                    "symbol": "ETH-WETH",
                    "description": "Ethereum pool",
                },
            ]
        }
        mock_pool_client.get_all_pools = AsyncMock(return_value=mock_all_pools)

        success, data = await adapter.search_pools("USDC", limit=5)

        assert success is True
        assert len(data["pools"]) == 1
        assert data["pools"][0]["id"] == "pool-123"
        assert data["total_found"] == 1
        assert data["query"] == "USDC"

    @pytest.mark.asyncio
    async def test_get_pools_by_ids_failure(self, adapter, mock_pool_client):
        """Test pool retrieval failure"""
        mock_pool_client.get_pools_by_ids = AsyncMock(
            side_effect=Exception("API Error")
        )

        success, data = await adapter.get_pools_by_ids(["pool-123"])

        assert success is False
        assert "API Error" in data

    @pytest.mark.asyncio
    async def test_find_high_yield_pools_no_matches(self, adapter, mock_pool_client):
        """Test high yield pool discovery with no matches"""
        mock_llama_response = {"matches": []}
        mock_pool_client.get_llama_matches.return_value = mock_llama_response

        success, data = await adapter.find_high_yield_pools(
            min_apy=0.10,
            min_tvl=10000000,
        )

        assert success is True
        assert len(data["pools"]) == 0
        assert data["total_found"] == 0

    def test_adapter_type(self, adapter):
        """Test adapter has adapter_type"""
        assert adapter.adapter_type == "POOL"
