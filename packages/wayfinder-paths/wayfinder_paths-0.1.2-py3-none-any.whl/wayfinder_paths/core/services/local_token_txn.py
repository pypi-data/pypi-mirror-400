from __future__ import annotations

from typing import Any

from eth_utils import to_checksum_address
from loguru import logger
from web3 import AsyncWeb3

from wayfinder_paths.core.clients.TokenClient import TokenClient
from wayfinder_paths.core.clients.TransactionClient import TransactionClient
from wayfinder_paths.core.constants import ZERO_ADDRESS
from wayfinder_paths.core.constants.erc20_abi import ERC20_APPROVAL_ABI
from wayfinder_paths.core.services.base import EvmTxn, TokenTxn
from wayfinder_paths.core.utils.evm_helpers import resolve_chain_id


class LocalTokenTxnService(TokenTxn):
    """Default transaction builder used by adapters."""

    def __init__(
        self,
        config: dict[str, Any] | None,
        *,
        wallet_provider: EvmTxn,
        simulation: bool = False,
    ) -> None:
        del config, simulation
        self.wallet_provider = wallet_provider
        self.logger = logger.bind(service="DefaultEvmTransactionService")
        self.token_client = TokenClient()
        self.builder = _EvmTransactionBuilder()

    async def build_send(
        self,
        *,
        token_id: str,
        amount: float,
        from_address: str,
        to_address: str,
        token_info: dict[str, Any] | None = None,
    ) -> tuple[bool, dict[str, Any] | str]:
        """Build the transaction dict for sending tokens between wallets."""
        token_meta = token_info
        if token_meta is None:
            token_meta = await self.token_client.get_token_details(token_id)
            if not token_meta:
                return False, f"Token not found: {token_id}"

        chain_id = resolve_chain_id(token_meta, self.logger)
        if chain_id is None:
            return False, f"Token {token_id} is missing a chain id"

        token_address = (token_meta or {}).get("address") or ZERO_ADDRESS

        try:
            tx = await self.builder.build_send_transaction(
                from_address=from_address,
                to_address=to_address,
                token_address=token_address,
                amount=amount,
                chain_id=int(chain_id),
            )
        except Exception as exc:  # noqa: BLE001
            return False, f"Failed to build send transaction: {exc}"

        return True, tx

    def build_erc20_approve(
        self,
        *,
        chain_id: int,
        token_address: str,
        from_address: str,
        spender: str,
        amount: int,
    ) -> tuple[bool, dict[str, Any] | str]:
        """Build the transaction dictionary for an ERC20 approval."""
        try:
            web3 = self.wallet_provider.get_web3(chain_id)
            token_checksum = to_checksum_address(token_address)
            from_checksum = to_checksum_address(from_address)
            spender_checksum = to_checksum_address(spender)
            amount_int = int(amount)
        except (TypeError, ValueError) as exc:
            return False, str(exc)

        approve_tx = self.builder.build_erc20_approval_transaction(
            chain_id=chain_id,
            token_address=token_checksum,
            from_address=from_checksum,
            spender=spender_checksum,
            amount=amount_int,
            web3=web3,
        )
        return True, approve_tx

    async def read_erc20_allowance(
        self, chain: Any, token_address: str, from_address: str, spender_address: str
    ) -> dict[str, Any]:
        try:
            chain_id = self._chain_id(chain)
        except (TypeError, ValueError) as exc:
            return {"error": str(exc), "allowance": 0}

        w3 = self.get_web3(chain_id)
        try:
            contract = w3.eth.contract(
                address=to_checksum_address(token_address), abi=ERC20_APPROVAL_ABI
            )
            allowance = await contract.functions.allowance(
                to_checksum_address(from_address),
                to_checksum_address(spender_address),
            ).call()
            return (True, {"allowance": int(allowance)})
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"Failed to read allowance: {exc}")
            return {"error": f"Allowance query failed: {exc}", "allowance": 0}
        finally:
            await self._close_web3(w3)

    def _chain_id(self, chain: Any) -> int:
        if isinstance(chain, dict):
            chain_id = chain.get("id") or chain.get("chain_id")
        else:
            chain_id = getattr(chain, "id", None)
        if chain_id is None:
            raise ValueError("Chain ID is required")
        return int(chain_id)


class _EvmTransactionBuilder:
    """Helpers that only build transaction dictionaries for sends and approvals."""

    def __init__(self) -> None:
        self.transaction_client = TransactionClient()

    async def build_send_transaction(
        self,
        *,
        from_address: str,
        to_address: str,
        token_address: str | None,
        amount: float,
        chain_id: int,
    ) -> dict[str, Any]:
        """Build the transaction dict for sending native or ERC20 tokens."""
        payload = await self.transaction_client.build_send(
            from_address=from_address,
            to_address=to_address,
            token_address=token_address or "",
            amount=float(amount),
            chain_id=int(chain_id),
        )
        return self._payload_to_tx(
            payload=payload,
            from_address=from_address,
            is_native=not token_address or token_address.lower() == ZERO_ADDRESS,
        )

    def build_erc20_approval_transaction(
        self,
        *,
        chain_id: int,
        token_address: str,
        from_address: str,
        spender: str,
        amount: int,
        web3: AsyncWeb3,
    ) -> dict[str, Any]:
        """Build an ERC20 approval transaction dict."""
        token_checksum = to_checksum_address(token_address)
        spender_checksum = to_checksum_address(spender)
        from_checksum = to_checksum_address(from_address)
        amount_int = int(amount)

        contract = web3.eth.contract(address=token_checksum, abi=ERC20_APPROVAL_ABI)
        data = contract.encodeABI(
            fn_name="approve", args=[spender_checksum, amount_int]
        )

        return {
            "chainId": int(chain_id),
            "from": from_checksum,
            "to": token_checksum,
            "data": data,
            "value": 0,
        }

    def _payload_to_tx(
        self, payload: dict[str, Any], from_address: str, is_native: bool
    ) -> dict[str, Any]:
        data_root = payload.get("data", payload)
        tx_src = data_root.get("transaction") or data_root

        chain_id = tx_src.get("chainId") or data_root.get("chain_id")
        if chain_id is None:
            raise ValueError("Transaction payload missing chainId")

        tx: dict[str, Any] = {"chainId": int(chain_id)}
        tx["from"] = to_checksum_address(from_address)

        if tx_src.get("to"):
            tx["to"] = to_checksum_address(tx_src["to"])
        if tx_src.get("data"):
            data = tx_src["data"]
            tx["data"] = data if str(data).startswith("0x") else f"0x{data}"

        val = tx_src.get("value", 0)
        tx["value"] = self._normalize_value(val) if is_native else 0

        if tx_src.get("gas"):
            tx["gas"] = int(tx_src["gas"])
        if tx_src.get("maxFeePerGas"):
            tx["maxFeePerGas"] = int(tx_src["maxFeePerGas"])
        if tx_src.get("maxPriorityFeePerGas"):
            tx["maxPriorityFeePerGas"] = int(tx_src["maxPriorityFeePerGas"])
        if tx_src.get("gasPrice"):
            tx["gasPrice"] = int(tx_src["gasPrice"])
        if tx_src.get("nonce") is not None:
            tx["nonce"] = int(tx_src["nonce"])

        return tx

    def _normalize_value(self, value: Any) -> int:
        if isinstance(value, str):
            if value.startswith("0x"):
                return int(value, 16)
            return int(float(value))
        if isinstance(value, (int, float)):
            return int(value)
        return 0
