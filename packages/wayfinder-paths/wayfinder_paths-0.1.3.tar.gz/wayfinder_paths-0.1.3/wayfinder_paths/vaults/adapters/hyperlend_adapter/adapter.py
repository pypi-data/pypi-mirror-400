from __future__ import annotations

from typing import Any

from eth_utils import to_checksum_address

from wayfinder_paths.core.adapters.BaseAdapter import BaseAdapter
from wayfinder_paths.core.clients.HyperlendClient import HyperlendClient
from wayfinder_paths.core.clients.SimulationClient import SimulationClient
from wayfinder_paths.core.constants.hyperlend_abi import (
    POOL_ABI,
    WRAPPED_TOKEN_GATEWAY_ABI,
)
from wayfinder_paths.core.services.base import Web3Service
from wayfinder_paths.core.settings import settings

HYPERLEND_DEFAULTS = {
    "pool": "0x00A89d7a5A02160f20150EbEA7a2b5E4879A1A8b",
    "wrapped_token_gateway": "0x49558c794ea2aC8974C9F27886DDfAa951E99171",
    "wrapped_native_underlying": "0x5555555555555555555555555555555555555555",
}


class HyperlendAdapter(BaseAdapter):
    """Thin HyperLend adapter that only builds tx data and lets the provider send it."""

    adapter_type = "HYPERLEND"

    def __init__(
        self,
        config: dict[str, Any],
        web3_service: Web3Service,
        simulation: bool = False,
    ) -> None:
        super().__init__("hyperlend_adapter", config)
        cfg = config or {}
        adapter_cfg = cfg.get("hyperlend_adapter") or {}

        self.hyperlend_client = HyperlendClient()
        self.simulation = simulation
        self.simulation_client = SimulationClient() if simulation else None

        self.web3 = web3_service
        self.token_txn_service = web3_service.token_transactions

        self.vault_wallet = cfg.get("vault_wallet") or {}
        self.pool_address = self._checksum(
            adapter_cfg.get("pool_address") or HYPERLEND_DEFAULTS["pool"]
        )
        self.gateway_address = self._checksum(
            adapter_cfg.get("wrapped_token_gateway")
            or HYPERLEND_DEFAULTS["wrapped_token_gateway"]
        )
        self.wrapped_native = self._checksum(
            adapter_cfg.get("wrapped_native_underlying")
            or HYPERLEND_DEFAULTS["wrapped_native_underlying"]
        )
        self.gateway_deposit_takes_pool = adapter_cfg.get(
            "gateway_deposit_takes_pool", True
        )

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #

    async def get_stable_markets(
        self,
        chain_id: int,
        required_underlying_tokens: float | None = None,
        buffer_bps: int | None = None,
        min_buffer_tokens: float | None = None,
        is_stable_symbol: bool | None = None,
    ) -> tuple[bool, Any]:
        try:
            data = await self.hyperlend_client.get_stable_markets(
                chain_id=chain_id,
                required_underlying_tokens=required_underlying_tokens,
                buffer_bps=buffer_bps,
                min_buffer_tokens=min_buffer_tokens,
                is_stable_symbol=is_stable_symbol,
            )
            return True, data
        except Exception as exc:
            return False, str(exc)

    async def get_assets_view(
        self, chain_id: int, user_address: str
    ) -> tuple[bool, Any]:
        try:
            data = await self.hyperlend_client.get_assets_view(
                chain_id=chain_id, user_address=user_address
            )
            return True, data
        except Exception as exc:
            return False, str(exc)

    async def get_market_entry(
        self, chain_id: int, underlying: str
    ) -> tuple[bool, Any]:
        try:
            data = await self.hyperlend_client.get_market_entry(chain_id, underlying)
            return True, data
        except Exception as exc:
            return False, str(exc)

    async def get_lend_rate_history(
        self,
        chain_id: int,
        token_address: str,
        lookback_hours: int,
    ) -> tuple[bool, Any]:
        try:
            data = await self.hyperlend_client.get_lend_rate_history(
                chain_id=chain_id,
                token_address=token_address,
                lookback_hours=lookback_hours,
            )
            return True, data
        except Exception as exc:
            return False, str(exc)

    async def lend(
        self,
        *,
        underlying_token: str,
        qty: int,
        chain_id: int,
        native: bool = False,
    ) -> tuple[bool, Any]:
        vault = self._vault_address()
        qty = int(qty)
        if qty <= 0:
            return False, "qty must be positive"
        chain_id = int(chain_id)

        if native:
            tx = self._encode_call(
                target=self.gateway_address,
                abi=WRAPPED_TOKEN_GATEWAY_ABI,
                fn_name="depositETH",
                args=[self._gateway_first_arg(underlying_token), vault, 0],
                from_address=vault,
                chain_id=chain_id,
                value=qty,
            )
        else:
            token_addr = self._checksum(underlying_token)
            approved = await self._ensure_allowance(
                token_address=token_addr,
                owner=vault,
                spender=self.pool_address,
                amount=qty,
                chain_id=chain_id,
            )
            if not approved[0]:
                return approved
            tx = self._encode_call(
                target=self.pool_address,
                abi=POOL_ABI,
                fn_name="supply",
                args=[token_addr, qty, vault, 0],
                from_address=vault,
                chain_id=chain_id,
            )
        return await self._execute(tx)

    async def unlend(
        self,
        *,
        underlying_token: str,
        qty: int,
        chain_id: int,
        native: bool = False,
    ) -> tuple[bool, Any]:
        vault = self._vault_address()
        qty = int(qty)
        if qty <= 0:
            return False, "qty must be positive"
        chain_id = int(chain_id)

        if native:
            tx = self._encode_call(
                target=self.gateway_address,
                abi=WRAPPED_TOKEN_GATEWAY_ABI,
                fn_name="withdrawETH",
                args=[self._gateway_first_arg(underlying_token), qty, vault],
                from_address=vault,
                chain_id=chain_id,
            )
        else:
            token_addr = self._checksum(underlying_token)
            tx = self._encode_call(
                target=self.pool_address,
                abi=POOL_ABI,
                fn_name="withdraw",
                args=[token_addr, qty, vault],
                from_address=vault,
                chain_id=chain_id,
            )
        return await self._execute(tx)

    # ------------------------------------------------------------------ #
    # Helpers                                                            #
    # ------------------------------------------------------------------ #

    async def _ensure_allowance(
        self,
        *,
        token_address: str,
        owner: str,
        spender: str,
        amount: int,
        chain_id: int,
    ) -> tuple[bool, Any]:
        chain = {"id": chain_id}
        allowance = await self.token_txn_service.read_erc20_allowance(
            chain, token_address, owner, spender
        )
        if allowance.get("allowance", 0) >= amount:
            return True, {}
        build_success, approve_tx = self.token_txn_service.build_erc20_approve(
            chain_id=chain_id,
            token_address=token_address,
            from_address=owner,
            spender=spender,
            amount=amount,
        )
        if not build_success:
            return False, approve_tx
        return await self._broadcast_transaction(approve_tx)

    async def _execute(self, tx: dict[str, Any]) -> tuple[bool, Any]:
        if self.simulation:
            return True, {"simulation": tx}
        return await self.web3.broadcast_transaction(
            tx, wait_for_receipt=True, timeout=120
        )

    async def _broadcast_transaction(self, tx: dict[str, Any]) -> tuple[bool, Any]:
        if getattr(settings, "DRY_RUN", False):
            return True, {"dry_run": True, "transaction": tx}
        return await self.web3.evm_transactions.broadcast_transaction(
            tx, wait_for_receipt=True, timeout=120
        )

    def _encode_call(
        self,
        *,
        target: str,
        abi: list[dict[str, Any]],
        fn_name: str,
        args: list[Any],
        from_address: str,
        chain_id: int,
        value: int = 0,
    ) -> dict[str, Any]:
        """Encode calldata without touching network."""
        web3 = self.web3.get_web3(chain_id)
        contract = web3.eth.contract(address=target, abi=abi)
        try:
            data = getattr(contract.functions, fn_name)(*args).build_transaction(
                {"from": from_address}
            )["data"]
        except ValueError as exc:
            raise ValueError(f"Failed to encode {fn_name}: {exc}") from exc

        tx: dict[str, Any] = {
            "chainId": int(chain_id),
            "from": to_checksum_address(from_address),
            "to": to_checksum_address(target),
            "data": data,
            "value": int(value),
        }
        return tx

    def _vault_address(self) -> str:
        addr = None
        if isinstance(self.vault_wallet, dict):
            addr = self.vault_wallet.get("address") or (
                (self.vault_wallet.get("evm") or {}).get("address")
            )
        elif isinstance(self.vault_wallet, str):
            addr = self.vault_wallet
        if not addr:
            raise ValueError(
                "vault_wallet address is required for HyperLend operations"
            )
        return to_checksum_address(addr)

    def _gateway_first_arg(self, underlying_token: str) -> str:
        if self.gateway_deposit_takes_pool:
            return self.pool_address
        return self._checksum(underlying_token) or self.wrapped_native

    def _checksum(self, address: str | None) -> str:
        if not address:
            raise ValueError("Missing required contract address in HyperLend config")
        return to_checksum_address(address)
