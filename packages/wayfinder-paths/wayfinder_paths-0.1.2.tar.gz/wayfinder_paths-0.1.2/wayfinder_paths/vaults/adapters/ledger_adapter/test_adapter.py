from unittest.mock import AsyncMock, patch

import pytest

from wayfinder_paths.vaults.adapters.ledger_adapter.adapter import LedgerAdapter


class TestLedgerAdapter:
    """Test cases for LedgerAdapter"""

    @pytest.fixture
    def mock_ledger_client(self):
        """Mock LedgerClient for testing"""
        mock_client = AsyncMock()
        return mock_client

    @pytest.fixture
    def adapter(self, mock_ledger_client):
        """Create a LedgerAdapter instance with mocked client for testing"""
        with patch(
            "vaults.adapters.ledger_adapter.adapter.LedgerClient",
            return_value=mock_ledger_client,
        ):
            return LedgerAdapter()

    @pytest.mark.asyncio
    async def test_get_vault_transactions_success(self, adapter, mock_ledger_client):
        """Test successful vault transaction retrieval"""
        mock_response = {
            "transactions": [
                {
                    "id": "tx_123",
                    "operation": "DEPOSIT",
                    "amount": "1000000000000000000",
                    "usd_value": "1000.00",
                }
            ],
            "total": 1,
        }
        mock_ledger_client.get_vault_transactions = AsyncMock(
            return_value=mock_response
        )

        success, data = await adapter.get_vault_transactions(
            wallet_address="0x1234567890123456789012345678901234567890",
            limit=10,
            offset=0,
        )

        assert success is True
        assert data == mock_response
        mock_ledger_client.get_vault_transactions.assert_called_once_with(
            wallet_address="0x1234567890123456789012345678901234567890",
            limit=10,
            offset=0,
        )

    @pytest.mark.asyncio
    async def test_get_vault_transactions_failure(self, adapter, mock_ledger_client):
        """Test vault transaction retrieval failure"""
        mock_ledger_client.get_vault_transactions = AsyncMock(
            side_effect=Exception("API Error")
        )

        success, data = await adapter.get_vault_transactions(
            wallet_address="0x1234567890123456789012345678901234567890"
        )

        assert success is False
        assert "API Error" in data

    @pytest.mark.asyncio
    async def test_get_vault_net_deposit_success(self, adapter, mock_ledger_client):
        """Test successful vault net deposit retrieval"""
        mock_response = {
            "net_deposit": "1000.00",
            "total_deposits": "1500.00",
            "total_withdrawals": "500.00",
        }
        mock_ledger_client.get_vault_net_deposit = AsyncMock(return_value=mock_response)

        # Test
        success, data = await adapter.get_vault_net_deposit(
            wallet_address="0x1234567890123456789012345678901234567890"
        )

        assert success is True
        assert data == mock_response
        mock_ledger_client.get_vault_net_deposit.assert_called_once_with(
            wallet_address="0x1234567890123456789012345678901234567890"
        )

    @pytest.mark.asyncio
    async def test_record_deposit_success(self, adapter, mock_ledger_client):
        """Test successful deposit recording"""
        mock_response = {
            "transaction_id": "tx_456",
            "status": "recorded",
            "timestamp": "2024-01-15T10:30:00Z",
        }
        mock_ledger_client.add_vault_deposit.return_value = mock_response

        # Test
        success, data = await adapter.record_deposit(
            wallet_address="0x1234567890123456789012345678901234567890",
            chain_id=8453,
            token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
            token_amount="1000000000000000000",
            usd_value="1000.00",
            strategy_name="TestStrategy",
        )

        assert success is True
        assert data == mock_response
        mock_ledger_client.add_vault_deposit.assert_called_once_with(
            wallet_address="0x1234567890123456789012345678901234567890",
            chain_id=8453,
            token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
            token_amount="1000000000000000000",
            usd_value="1000.00",
            data=None,
            strategy_name="TestStrategy",
        )

    @pytest.mark.asyncio
    async def test_record_withdrawal_success(self, adapter, mock_ledger_client):
        """Test successful withdrawal recording"""
        mock_response = {
            "transaction_id": "tx_789",
            "status": "recorded",
            "timestamp": "2024-01-15T11:00:00Z",
        }
        mock_ledger_client.add_vault_withdraw.return_value = mock_response

        # Test
        success, data = await adapter.record_withdrawal(
            wallet_address="0x1234567890123456789012345678901234567890",
            chain_id=8453,
            token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
            token_amount="500000000000000000",
            usd_value="500.00",
            strategy_name="TestStrategy",
        )

        assert success is True
        assert data == mock_response

    @pytest.mark.asyncio
    async def test_record_operation_success(self, adapter, mock_ledger_client):
        """Test successful operation recording"""
        mock_response = {
            "operation_id": "op_123",
            "status": "recorded",
            "timestamp": "2024-01-15T10:45:00Z",
        }
        mock_ledger_client.add_vault_operation.return_value = mock_response

        # Test
        operation_data = {
            "type": "SWAP",
            "from_token": "0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
            "to_token": "0xB1c97a44F7552d9Dd5e5e5e5e5e5e5e5e5e5e5e5e5e",
            "amount_in": "1000000000000000000",
            "amount_out": "995000000000000000",
        }

        success, data = await adapter.record_operation(
            wallet_address="0x1234567890123456789012345678901234567890",
            operation_data=operation_data,
            usd_value="1000.00",
            strategy_name="TestStrategy",
        )

        assert success is True
        assert data == mock_response

    @pytest.mark.asyncio
    async def test_get_transaction_summary_success(self, adapter, mock_ledger_client):
        """Test successful transaction summary generation"""
        mock_transactions = {
            "transactions": [
                {"operation": "DEPOSIT", "amount": "1000000000000000000"},
                {"operation": "WITHDRAW", "amount": "500000000000000000"},
                {"operation": "SWAP", "amount": "200000000000000000"},
            ]
        }
        mock_ledger_client.get_vault_transactions.return_value = mock_transactions

        # Test
        success, data = await adapter.get_transaction_summary(
            wallet_address="0x1234567890123456789012345678901234567890", limit=10
        )

        assert success is True
        assert data["total_transactions"] == 3
        assert data["operations"]["deposits"] == 1
        assert data["operations"]["withdrawals"] == 1
        assert data["operations"]["operations"] == 1

    def test_adapter_type(self, adapter):
        """Test adapter has adapter_type"""
        assert adapter.adapter_type == "LEDGER"
