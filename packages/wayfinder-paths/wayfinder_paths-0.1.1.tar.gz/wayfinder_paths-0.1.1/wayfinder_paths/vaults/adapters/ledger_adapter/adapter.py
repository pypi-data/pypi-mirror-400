from typing import Any

from wayfinder_paths.core.adapters.BaseAdapter import BaseAdapter
from wayfinder_paths.core.clients.LedgerClient import LedgerClient


class LedgerAdapter(BaseAdapter):
    """
    Ledger adapter for vault transaction history and bookkeeping operations.

    Provides high-level operations for:
    - Fetching vault transaction history
    - Getting net deposit amounts
    - Getting last rotation time
    - Recording deposits, withdrawals, operations, and cashflows
    """

    adapter_type: str = "LEDGER"

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        ledger_client: LedgerClient | None = None,
    ):
        super().__init__("ledger_adapter", config)
        self.ledger_client = ledger_client or LedgerClient()

    async def get_vault_transactions(
        self, wallet_address: str, limit: int = 50, offset: int = 0
    ) -> tuple[bool, Any]:
        """
        Get paginated vault transaction history.

        Args:
            wallet_address: Vault wallet address
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip

        Returns:
            Tuple of (success, data) where data is transaction list or error message
        """
        try:
            data = await self.ledger_client.get_vault_transactions(
                wallet_address=wallet_address, limit=limit, offset=offset
            )
            return (True, data)
        except Exception as e:
            self.logger.error(f"Error fetching vault transactions: {e}")
            return (False, str(e))

    async def get_vault_net_deposit(self, wallet_address: str) -> tuple[bool, Any]:
        """
        Get net deposit amount (deposits - withdrawals) for a vault.

        Args:
            wallet_address: Vault wallet address

        Returns:
            Tuple of (success, data) where data contains net_deposit or error message
        """
        try:
            data = await self.ledger_client.get_vault_net_deposit(
                wallet_address=wallet_address
            )
            return (True, data)
        except Exception as e:
            self.logger.error(f"Error fetching vault net deposit: {e}")
            return (False, str(e))

    async def get_vault_latest_transactions(
        self, wallet_address: str
    ) -> tuple[bool, Any]:
        """
        Get the latest transactions for a vault.

        Args:
            wallet_address: Vault wallet address

        Returns:
            Tuple of (success, data) where data contains latest transactions or error message
        """
        try:
            data = await self.ledger_client.get_vault_latest_transactions(
                wallet_address=wallet_address
            )
            return (True, data)
        except Exception as e:
            self.logger.error(f"Error fetching vault last transactions: {e}")
            return (False, str(e))

    async def record_deposit(
        self,
        wallet_address: str,
        chain_id: int,
        token_address: str,
        token_amount: str | float,
        usd_value: str | float,
        data: dict[str, Any] | None = None,
        strategy_name: str | None = None,
    ) -> tuple[bool, Any]:
        """
        Record a vault deposit transaction.

        Args:
            wallet_address: Vault wallet address
            chain_id: Blockchain chain ID
            token_address: Token contract address
            token_amount: Amount deposited (in token units)
            usd_value: USD value of the deposit
            data: Additional transaction data
            strategy_name: Name of the strategy making the deposit

        Returns:
            Tuple of (success, data) where data is transaction record or error message
        """
        try:
            result = await self.ledger_client.add_vault_deposit(
                wallet_address=wallet_address,
                chain_id=chain_id,
                token_address=token_address,
                token_amount=token_amount,
                usd_value=usd_value,
                data=data,
                strategy_name=strategy_name,
            )
            return (True, result)
        except Exception as e:
            self.logger.error(f"Error recording deposit: {e}")
            return (False, str(e))

    async def record_withdrawal(
        self,
        wallet_address: str,
        chain_id: int,
        token_address: str,
        token_amount: str | float,
        usd_value: str | float,
        data: dict[str, Any] | None = None,
        strategy_name: str | None = None,
    ) -> tuple[bool, Any]:
        """
        Record a vault withdrawal transaction.

        Args:
            wallet_address: Vault wallet address
            chain_id: Blockchain chain ID
            token_address: Token contract address
            token_amount: Amount withdrawn (in token units)
            usd_value: USD value of the withdrawal
            data: Additional transaction data
            strategy_name: Name of the strategy making the withdrawal

        Returns:
            Tuple of (success, data) where data is transaction record or error message
        """
        try:
            result = await self.ledger_client.add_vault_withdraw(
                wallet_address=wallet_address,
                chain_id=chain_id,
                token_address=token_address,
                token_amount=token_amount,
                usd_value=usd_value,
                data=data,
                strategy_name=strategy_name,
            )
            return (True, result)
        except Exception as e:
            self.logger.error(f"Error recording withdrawal: {e}")
            return (False, str(e))

    async def record_operation(
        self,
        wallet_address: str,
        operation_data: dict[str, Any],
        usd_value: str | float,
        strategy_name: str | None = None,
    ) -> tuple[bool, Any]:
        """
        Record a vault operation (e.g., swaps, rebalances) for bookkeeping.

        Args:
            wallet_address: Vault wallet address
            operation_data: Details of the operation performed
            usd_value: USD value of the operation
            strategy_name: Name of the strategy performing the operation

        Returns:
            Tuple of (success, data) where data is operation record or error message
        """
        try:
            result = await self.ledger_client.add_vault_operation(
                wallet_address=wallet_address,
                operation_data=operation_data,
                usd_value=usd_value,
                strategy_name=strategy_name,
            )
            return (True, result)
        except Exception as e:
            self.logger.error(f"Error recording operation: {e}")
            return (False, str(e))

    async def record_cashflow(
        self,
        wallet_address: str,
        block_timestamp: int,
        token_addr: str,
        amount: str | int | float,
        description: str,
        strategy_name: str | None = None,
    ) -> tuple[bool, Any]:
        """
        Record a vault cashflow (interest, funding, reward, or fee).

        Args:
            wallet_address: Vault wallet address
            block_timestamp: Block timestamp (Unix timestamp)
            token_addr: Token contract address
            amount: Cashflow amount (in token units)
            description: Cashflow type - must be one of: "interest", "funding", "reward", "fee"
            strategy_name: Optional strategy name

        Returns:
            Tuple of (success, data) where data is cashflow record or error message
        """
        try:
            result = await self.ledger_client.add_vault_cashflow(
                wallet_address=wallet_address,
                block_timestamp=block_timestamp,
                token_addr=token_addr,
                amount=amount,
                description=description,
                strategy_name=strategy_name,
            )
            return (True, result)
        except Exception as e:
            self.logger.error(f"Error recording cashflow: {e}")
            return (False, str(e))

    async def get_transaction_summary(
        self, wallet_address: str, limit: int = 10
    ) -> tuple[bool, Any]:
        """
        Get a summary of recent vault transactions.

        Args:
            wallet_address: Vault wallet address
            limit: Number of recent transactions to include

        Returns:
            Tuple of (success, data) where data is transaction summary or error message
        """
        try:
            success, transactions_data = await self.get_vault_transactions(
                wallet_address=wallet_address, limit=limit
            )

            if not success:
                return (False, transactions_data)

            transactions = transactions_data.get("transactions", [])

            # Create summary
            summary = {
                "total_transactions": len(transactions),
                "recent_transactions": transactions[:limit],
                "operations": {
                    "deposits": len(
                        [t for t in transactions if t.get("operation") == "DEPOSIT"]
                    ),
                    "withdrawals": len(
                        [t for t in transactions if t.get("operation") == "WITHDRAW"]
                    ),
                    "operations": len(
                        [
                            t
                            for t in transactions
                            if t.get("operation") not in ["DEPOSIT", "WITHDRAW"]
                        ]
                    ),
                },
            }

            return (True, summary)
        except Exception as e:
            self.logger.error(f"Error creating transaction summary: {e}")
            return (False, str(e))
