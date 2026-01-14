from typing import Any

from wayfinder_paths.core.adapters.BaseAdapter import BaseAdapter
from wayfinder_paths.core.clients.TokenClient import TokenClient
from wayfinder_paths.core.clients.WalletClient import WalletClient
from wayfinder_paths.core.services.base import Web3Service
from wayfinder_paths.core.settings import settings
from wayfinder_paths.core.utils.evm_helpers import resolve_chain_id
from wayfinder_paths.vaults.adapters.ledger_adapter.adapter import LedgerAdapter
from wayfinder_paths.vaults.adapters.token_adapter.adapter import TokenAdapter


class BalanceAdapter(BaseAdapter):
    adapter_type = "BALANCE"

    def __init__(
        self,
        config: dict[str, Any],
        web3_service: Web3Service,
    ):
        super().__init__("balance", config)
        self.wallet_client = WalletClient()
        self.token_client = TokenClient()
        self.token_adapter = TokenAdapter()
        self.ledger_adapter = LedgerAdapter()

        self.wallet_provider = web3_service.evm_transactions
        self.token_transactions = web3_service.token_transactions

    def _parse_balance(self, raw: Any) -> int:
        """Parse balance value to integer, handling various formats."""
        if raw is None:
            return 0
        try:
            return int(raw)
        except (ValueError, TypeError):
            try:
                return int(float(raw))
            except (ValueError, TypeError):
                return 0

    async def get_balance(
        self,
        *,
        token_id: str,
        wallet_address: str,
    ) -> tuple[bool, Any]:
        """Get token balance for a wallet."""
        try:
            data = await self.wallet_client.get_token_balance_for_wallet(
                token_id=token_id,
                wallet_address=wallet_address,
            )
            return (True, data.get("balance"))
        except Exception as e:
            return (False, str(e))

    async def move_from_main_wallet_to_vault_wallet(
        self,
        token_id: str,
        amount: float,
        strategy_name: str = "unknown",
        skip_ledger: bool = False,
    ) -> tuple[bool, Any]:
        """Move funds from the configured main wallet into the vault wallet."""
        return await self._move_between_wallets(
            token_id=token_id,
            amount=amount,
            from_wallet=self.config.get("main_wallet"),
            to_wallet=self.config.get("vault_wallet"),
            ledger_method=self.ledger_adapter.record_deposit,
            ledger_wallet="to",
            strategy_name=strategy_name,
            skip_ledger=skip_ledger,
        )

    async def move_from_vault_wallet_to_main_wallet(
        self,
        token_id: str,
        amount: float,
        strategy_name: str = "unknown",
        skip_ledger: bool = False,
    ) -> tuple[bool, Any]:
        """Move funds from the vault wallet back into the main wallet."""
        return await self._move_between_wallets(
            token_id=token_id,
            amount=amount,
            from_wallet=self.config.get("vault_wallet"),
            to_wallet=self.config.get("main_wallet"),
            ledger_method=self.ledger_adapter.record_withdrawal,
            ledger_wallet="from",
            strategy_name=strategy_name,
            skip_ledger=skip_ledger,
        )

    async def _move_between_wallets(
        self,
        *,
        token_id: str,
        amount: float,
        from_wallet: dict[str, Any] | None,
        to_wallet: dict[str, Any] | None,
        ledger_method,
        ledger_wallet: str,
        strategy_name: str,
        skip_ledger: bool,
    ) -> tuple[bool, Any]:
        if self.token_transactions is None:
            return False, "Token transaction service not configured"

        from_address = self._wallet_address(from_wallet)
        to_address = self._wallet_address(to_wallet)
        if not from_address or not to_address:
            return False, "main_wallet or vault_wallet missing"

        token_info = await self.token_client.get_token_details(token_id)
        if not token_info:
            return False, f"Token not found: {token_id}"

        build_success, tx_data = await self.token_transactions.build_send(
            token_id=token_id,
            amount=amount,
            from_address=from_address,
            to_address=to_address,
            token_info=token_info,
        )
        if not build_success:
            return False, tx_data

        tx = tx_data
        if getattr(settings, "DRY_RUN", False):
            broadcast_result = (True, {"dry_run": True, "transaction": tx})
        else:
            broadcast_result = await self.wallet_provider.broadcast_transaction(
                tx, wait_for_receipt=True, timeout=120
            )

        if broadcast_result[0] and not skip_ledger and ledger_method is not None:
            wallet_for_ledger = from_address if ledger_wallet == "from" else to_address
            await self._record_ledger_entry(
                ledger_method=ledger_method,
                wallet_address=wallet_for_ledger,
                token_info=token_info,
                amount=amount,
                strategy_name=strategy_name,
            )

        return broadcast_result

    async def _record_ledger_entry(
        self,
        *,
        ledger_method,
        wallet_address: str,
        token_info: dict[str, Any],
        amount: float,
        strategy_name: str,
    ) -> None:
        chain_id = resolve_chain_id(token_info, self.logger)
        if chain_id is None:
            return

        usd_value = await self._token_amount_usd(token_info, amount)
        try:
            success, response = await ledger_method(
                wallet_address=wallet_address,
                chain_id=chain_id,
                token_address=token_info.get("address"),
                token_amount=str(amount),
                usd_value=usd_value,
                data={
                    "token_id": token_info.get("id"),
                    "amount": str(amount),
                    "usd_value": usd_value,
                },
                strategy_name=strategy_name,
            )
            if not success:
                self.logger.warning(
                    "Ledger entry failed",
                    wallet=wallet_address,
                    token_id=token_info.get("id"),
                    amount=amount,
                    error=response,
                )
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(
                f"Ledger entry raised: {exc}",
                wallet=wallet_address,
                token_id=token_info.get("id"),
            )

    async def _token_amount_usd(
        self, token_info: dict[str, Any], amount: float
    ) -> float:
        token_id = token_info.get("id")
        if not token_id:
            return 0.0
        success, price_data = await self.token_adapter.get_token_price(token_id)
        if not success or not price_data:
            return 0.0
        return float(price_data.get("current_price", 0.0)) * float(amount)

    def _wallet_address(self, wallet: dict[str, Any] | None) -> str | None:
        if not wallet:
            return None
        address = wallet.get("address")
        if address:
            return str(address)
        evm_wallet = wallet.get("evm") if isinstance(wallet, dict) else None
        if isinstance(evm_wallet, dict):
            return evm_wallet.get("address")
        return None

    async def get_pool_balance(
        self,
        *,
        pool_address: str,
        chain_id: int,
        user_address: str,
    ) -> tuple[bool, Any]:
        """Get pool balance for a wallet."""
        try:
            data = await self.wallet_client.get_pool_balance_for_wallet(
                pool_address=pool_address,
                chain_id=chain_id,
                user_address=user_address,
                human_readable=False,
            )
            raw = (
                data.get("balance_raw") or data.get("balance")
                if isinstance(data, dict)
                else None
            )
            return (True, self._parse_balance(raw))
        except Exception as e:
            return (False, str(e))

    async def get_all_balances(
        self,
        *,
        wallet_address: str,
        enrich: bool = True,
        from_cache: bool = False,
        add_llama: bool = True,
    ) -> tuple[bool, Any]:
        """Get all enriched token balances for a wallet."""
        try:
            data = await self.wallet_client.get_all_enriched_token_balances_for_wallet(
                wallet_address=wallet_address,
                enrich=enrich,
                from_cache=from_cache,
                add_llama=add_llama,
            )
            return (True, data)
        except Exception as e:
            return (False, str(e))
