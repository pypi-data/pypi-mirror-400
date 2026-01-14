from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from wayfinder_paths.vaults.adapters.brap_adapter.adapter import BRAPAdapter


class TestBRAPAdapter:
    """Test cases for BRAPAdapter"""

    @pytest.fixture
    def mock_brap_client(self):
        """Mock BRAPClient for testing"""
        mock_client = AsyncMock()
        return mock_client

    @pytest.fixture
    def mock_web3_service(self):
        """Minimal Web3Service stub for adapter construction."""
        wallet_provider = SimpleNamespace(
            broadcast_transaction=AsyncMock(return_value=(True, {}))
        )
        token_txn = SimpleNamespace(
            build_send=AsyncMock(return_value=(True, {})),
            build_erc20_approve=AsyncMock(return_value=(True, {})),
            read_erc20_allowance=AsyncMock(return_value={"allowance": 0}),
        )
        return SimpleNamespace(
            evm_transactions=wallet_provider, token_transactions=token_txn
        )

    @pytest.fixture
    def adapter(self, mock_brap_client, mock_web3_service):
        """Create a BRAPAdapter instance with mocked client for testing"""
        with patch(
            "vaults.adapters.brap_adapter.adapter.BRAPClient",
            return_value=mock_brap_client,
        ):
            return BRAPAdapter(web3_service=mock_web3_service)

    @pytest.mark.asyncio
    async def test_get_swap_quote_success(self, adapter, mock_brap_client):
        """Test successful swap quote retrieval"""
        mock_response = {
            "quotes": {
                "best_quote": {
                    "input_amount": "1000000000000000000",
                    "output_amount": "995000000000000000",
                    "gas_fee": "5000000000000000",
                    "total_fee": "8000000000000000",
                }
            }
        }
        mock_brap_client.get_quote = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_swap_quote(
            from_token_address="0x" + "a" * 40,
            to_token_address="0x" + "b" * 40,
            from_chain_id=8453,
            to_chain_id=1,
            from_address="0x1234567890123456789012345678901234567890",
            to_address="0x1234567890123456789012345678901234567890",
            amount="1000000000000000000",
            slippage=0.01,
        )

        assert success is True
        assert data == mock_response
        mock_brap_client.get_quote.assert_called_once_with(
            from_token_address="0x" + "a" * 40,
            to_token_address="0x" + "b" * 40,
            from_chain_id=8453,
            to_chain_id=1,
            from_address="0x1234567890123456789012345678901234567890",
            to_address="0x1234567890123456789012345678901234567890",
            amount1="1000000000000000000",
            slippage=0.01,
            wayfinder_fee=None,
        )

    @pytest.mark.asyncio
    async def test_get_best_quote_success(self, adapter, mock_brap_client):
        """Test successful best quote retrieval"""
        mock_response = {
            "quotes": {
                "best_quote": {
                    "input_amount": "1000000000000000000",
                    "output_amount": "995000000000000000",
                    "total_fee": "8000000000000000",
                }
            }
        }
        mock_brap_client.get_quote = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_best_quote(
            from_token_address="0x" + "a" * 40,
            to_token_address="0x" + "b" * 40,
            from_chain_id=8453,
            to_chain_id=1,
            from_address="0x1234567890123456789012345678901234567890",
            to_address="0x1234567890123456789012345678901234567890",
            amount="1000000000000000000",
        )

        assert success is True
        assert data["input_amount"] == "1000000000000000000"
        assert data["output_amount"] == "995000000000000000"

    @pytest.mark.asyncio
    async def test_get_best_quote_no_quotes(self, adapter, mock_brap_client):
        """Test best quote retrieval when no quotes available"""
        mock_response = {"quotes": {}}
        mock_brap_client.get_quote = AsyncMock(return_value=mock_response)

        success, data = await adapter.get_best_quote(
            from_token_address="0x" + "a" * 40,
            to_token_address="0x" + "b" * 40,
            from_chain_id=8453,
            to_chain_id=1,
            from_address="0x1234567890123456789012345678901234567890",
            to_address="0x1234567890123456789012345678901234567890",
            amount="1000000000000000000",
        )

        assert success is False
        assert "No quotes available" in data

    @pytest.mark.asyncio
    async def test_calculate_swap_fees_success(self, adapter, mock_brap_client):
        """Test successful swap fee calculation"""
        mock_quote_response = {
            "quotes": {
                "best_quote": {
                    "input_amount": "1000000000000000000",
                    "output_amount": "995000000000000000",
                    "gas_fee": "5000000000000000",
                    "bridge_fee": "2000000000000000",
                    "protocol_fee": "1000000000000000",
                    "total_fee": "8000000000000000",
                    "slippage": 0.01,
                    "price_impact": 0.005,
                }
            }
        }
        mock_brap_client.get_quote = AsyncMock(return_value=mock_quote_response)

        success, data = await adapter.calculate_swap_fees(
            from_token_address="0x" + "a" * 40,
            to_token_address="0x" + "b" * 40,
            from_chain_id=8453,
            to_chain_id=1,
            amount="1000000000000000000",
            slippage=0.01,
        )

        assert success is True
        assert data["input_amount"] == "1000000000000000000"
        assert data["output_amount"] == "995000000000000000"
        assert data["gas_fee"] == "5000000000000000"
        assert data["total_fee"] == "8000000000000000"

    @pytest.mark.asyncio
    async def test_compare_routes_success(self, adapter, mock_brap_client):
        """Test successful route comparison"""
        mock_response = {
            "quotes": {
                "quotes": [
                    {
                        "route": "Route 1",
                        "output_amount": "995000000000000000",
                        "total_fee": "8000000000000000",
                        "estimated_time": 300,
                    },
                    {
                        "route": "Route 2",
                        "output_amount": "992000000000000000",
                        "total_fee": "12000000000000000",
                        "estimated_time": 180,
                    },
                ],
                "best_quote": {
                    "output_amount": "995000000000000000",
                    "total_fee": "8000000000000000",
                },
            }
        }
        mock_brap_client.get_quote = AsyncMock(return_value=mock_response)

        success, data = await adapter.compare_routes(
            from_token_address="0x" + "a" * 40,
            to_token_address="0x" + "b" * 40,
            from_chain_id=8453,
            to_chain_id=1,
            amount="1000000000000000000",
        )

        assert success is True
        assert data["total_routes"] == 2
        assert len(data["all_routes"]) == 2
        assert data["best_route"]["output_amount"] == "995000000000000000"

    @pytest.mark.asyncio
    async def test_estimate_gas_cost_success(self, adapter):
        """Test successful gas cost estimation"""
        success, data = await adapter.estimate_gas_cost(
            from_chain_id=8453, to_chain_id=1, operation_type="swap"
        )

        assert success is True
        assert data["from_chain"] == "base"
        assert data["to_chain"] == "ethereum"
        assert data["from_gas_estimate"] == 100000
        assert data["to_gas_estimate"] == 150000
        assert data["total_operations"] == 2

    @pytest.mark.asyncio
    async def test_validate_swap_parameters_success(self, adapter, mock_brap_client):
        """Test successful swap parameter validation"""
        mock_quote_response = {
            "quotes": {"best_quote": {"output_amount": "995000000000000000"}}
        }
        mock_brap_client.get_quote = AsyncMock(return_value=mock_quote_response)

        success, data = await adapter.validate_swap_parameters(
            from_token_address="0x" + "a" * 40,
            to_token_address="0x" + "b" * 40,
            from_chain_id=8453,
            to_chain_id=1,
            amount="1000000000000000000",
        )

        assert success is True
        assert data["valid"] is True
        assert data["quote_available"] is True
        assert data["estimated_output"] == "995000000000000000"

    @pytest.mark.asyncio
    async def test_validate_swap_parameters_invalid_address(self, adapter):
        """Test swap parameter validation with invalid address"""
        success, data = await adapter.validate_swap_parameters(
            from_token_address="invalid_address",
            to_token_address="0xB1c97a44F7552d9Dd5e5e5e5e5e5e5e5e5e5e5e5e5e",
            from_chain_id=8453,
            to_chain_id=1,
            amount="1000000000000000000",
        )

        assert success is False
        assert data["valid"] is False
        assert "Invalid from_token_address" in data["errors"]

    @pytest.mark.asyncio
    async def test_validate_swap_parameters_invalid_amount(self, adapter):
        """Test swap parameter validation with invalid amount"""
        success, data = await adapter.validate_swap_parameters(
            from_token_address="0x" + "a" * 40,
            to_token_address="0x" + "b" * 40,
            from_chain_id=8453,
            to_chain_id=1,
            amount="invalid_amount",
        )

        assert success is False
        assert data["valid"] is False
        assert "Invalid amount format" in data["errors"]

    @pytest.mark.asyncio
    async def test_get_swap_quote_failure(self, adapter, mock_brap_client):
        """Test swap quote retrieval failure"""
        mock_brap_client.get_quote = AsyncMock(side_effect=Exception("API Error"))

        success, data = await adapter.get_swap_quote(
            from_token_address="0x" + "a" * 40,
            to_token_address="0x" + "b" * 40,
            from_chain_id=8453,
            to_chain_id=1,
            from_address="0x1234567890123456789012345678901234567890",
            to_address="0x1234567890123456789012345678901234567890",
            amount="1000000000000000000",
        )

        assert success is False
        assert "API Error" in data

    def test_adapter_type(self, adapter):
        """Test adapter has adapter_type"""
        assert adapter.adapter_type == "BRAP"
