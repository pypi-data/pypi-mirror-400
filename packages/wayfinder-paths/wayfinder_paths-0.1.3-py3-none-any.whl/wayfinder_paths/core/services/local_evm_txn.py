import asyncio
from typing import Any

from eth_account import Account
from eth_utils import to_checksum_address
from loguru import logger
from web3 import AsyncHTTPProvider, AsyncWeb3, Web3

from wayfinder_paths.core.constants import (
    DEFAULT_GAS_ESTIMATE_FALLBACK,
    ONE_GWEI,
    ZERO_ADDRESS,
)
from wayfinder_paths.core.constants.erc20_abi import (
    ERC20_APPROVAL_ABI,
    ERC20_MINIMAL_ABI,
)
from wayfinder_paths.core.services.base import EvmTxn
from wayfinder_paths.core.utils.evm_helpers import (
    resolve_private_key_for_from_address,
    resolve_rpc_url,
)

# Gas management constants for ERC20 approval transactions
ERC20_APPROVAL_GAS_LIMIT = 120_000
MAX_FEE_PER_GAS_RATE = 1.2


class NonceManager:
    """
    Thread-safe nonce manager to track and increment nonces per address/chain.
    Prevents nonce conflicts when multiple transactions are sent in quick succession.
    """

    def __init__(self):
        # Dictionary: (address, chain_id) -> current_nonce
        self._nonces: dict[tuple[str, int], int] = {}
        self._lock: asyncio.Lock | None = None

    def _get_lock(self) -> asyncio.Lock:
        """Get or create the async lock."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def get_next_nonce(self, address: str, chain_id: int, w3: AsyncWeb3) -> int:
        """
        Get the next nonce for an address on a chain.
        Tracks nonces locally and syncs with chain when needed.
        """
        async with self._get_lock():
            key = (address.lower(), chain_id)

            # If we don't have a tracked nonce, fetch from chain
            if key not in self._nonces:
                chain_nonce = await w3.eth.get_transaction_count(address, "pending")
                self._nonces[key] = chain_nonce
                return chain_nonce

            # Return the tracked nonce and increment for next time
            current_nonce = self._nonces[key]
            self._nonces[key] = current_nonce + 1
            return current_nonce

    async def sync_nonce(self, address: str, chain_id: int, chain_nonce: int) -> None:
        """
        Sync the tracked nonce with the chain nonce.
        Used when we detect a mismatch or after a transaction fails.
        """
        async with self._get_lock():
            key = (address.lower(), chain_id)
            # Use the higher of the two to avoid going backwards
            if key in self._nonces:
                self._nonces[key] = max(self._nonces[key], chain_nonce)
            else:
                self._nonces[key] = chain_nonce


class LocalEvmTxn(EvmTxn):
    """
    Local wallet provider using private keys stored in config or environment variables.

    This provider implements the current default behavior:
    - Resolves private keys from config or environment
    - Signs transactions using eth_account
    - Broadcasts transactions via RPC
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize local wallet provider.

        Args:
            config: Configuration dictionary containing wallet information
        """
        self.config = config or {}
        self.logger = logger.bind(provider="LocalWalletProvider")
        self._nonce_manager = NonceManager()

    def get_web3(self, chain_id: int) -> AsyncWeb3:
        """
        Return an AsyncWeb3 configured for the requested chain.

        Callers are responsible for closing the provider session when finished.
        """
        rpc_url = self._resolve_rpc_url(chain_id)
        return AsyncWeb3(AsyncHTTPProvider(rpc_url))

    async def get_balance(
        self,
        address: str,
        token_address: str | None,
        chain_id: int,
    ) -> tuple[bool, Any]:
        """
        Get balance for an address (native or ERC20 token).
        """
        w3 = self.get_web3(chain_id)
        try:
            checksum_addr = to_checksum_address(address)

            if not token_address or token_address.lower() == ZERO_ADDRESS:
                balance = await w3.eth.get_balance(checksum_addr)
                return (True, int(balance))

            token_checksum = to_checksum_address(token_address)
            contract = w3.eth.contract(address=token_checksum, abi=ERC20_MINIMAL_ABI)
            balance = await contract.functions.balanceOf(checksum_addr).call()
            return (True, int(balance))

        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"Failed to get balance: {exc}")
            return (False, f"Balance query failed: {exc}")
        finally:
            await self._close_web3(w3)

    async def approve_token(
        self,
        token_address: str,
        spender: str,
        amount: int,
        from_address: str,
        chain_id: int,
        wait_for_receipt: bool = True,
        timeout: int = 120,
    ) -> tuple[bool, Any]:
        """
        Approve a spender to spend tokens on behalf of from_address.
        """
        try:
            token_checksum = to_checksum_address(token_address)
            spender_checksum = to_checksum_address(spender)
            from_checksum = to_checksum_address(from_address)
            amount_int = int(amount)

            w3_sync = Web3()
            contract = w3_sync.eth.contract(
                address=token_checksum, abi=ERC20_APPROVAL_ABI
            )
            transaction_data = contract.encodeABI(
                fn_name="approve",
                args=[spender_checksum, amount_int],
            )

            approve_txn = {
                "from": from_checksum,
                "chainId": int(chain_id),
                "to": token_checksum,
                "data": transaction_data,
                "value": 0,
                "gas": ERC20_APPROVAL_GAS_LIMIT,
            }

            return await self.broadcast_transaction(
                approve_txn,
                wait_for_receipt=wait_for_receipt,
                timeout=timeout,
            )
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"ERC20 approval failed: {exc}")
            return (False, f"ERC20 approval failed: {exc}")

    async def broadcast_transaction(
        self,
        transaction: dict[str, Any],
        *,
        wait_for_receipt: bool = True,
        timeout: int = 120,
    ) -> tuple[bool, Any]:
        """
        Sign and broadcast a transaction dict.
        """
        try:
            tx = dict(transaction)
            from_address = tx.get("from")
            if not from_address:
                return (False, "Transaction missing 'from' address")
            checksum_from = to_checksum_address(from_address)
            tx["from"] = checksum_from

            chain_id = tx.get("chainId") or tx.get("chain_id")
            if chain_id is None:
                return (False, "Transaction missing chainId")
            tx["chainId"] = int(chain_id)

            w3 = self.get_web3(tx["chainId"])
            try:
                if "value" in tx:
                    tx["value"] = self._normalize_int(tx["value"])
                else:
                    tx["value"] = 0

                if "nonce" in tx:
                    tx["nonce"] = self._normalize_int(tx["nonce"])
                    # Sync our tracked nonce with the provided nonce
                    await self._nonce_manager.sync_nonce(
                        checksum_from, tx["chainId"], tx["nonce"]
                    )
                else:
                    # Use nonce manager to get and track the next nonce
                    tx["nonce"] = await self._nonce_manager.get_next_nonce(
                        checksum_from, tx["chainId"], w3
                    )

                if "data" in tx and isinstance(tx["data"], str):
                    calldata = tx["data"]
                    tx["data"] = (
                        calldata if calldata.startswith("0x") else f"0x{calldata}"
                    )

                if "gas" in tx:
                    tx["gas"] = self._normalize_int(tx["gas"])
                else:
                    estimate_request = {
                        "to": tx.get("to"),
                        "from": tx["from"],
                        "value": tx.get("value", 0),
                        "data": tx.get("data", "0x"),
                    }
                    try:
                        tx["gas"] = await w3.eth.estimate_gas(estimate_request)
                    except Exception as exc:  # noqa: BLE001
                        self.logger.warning(
                            "Gas estimation failed; using fallback %s. Reason: %s",
                            DEFAULT_GAS_ESTIMATE_FALLBACK,
                            exc,
                        )
                        tx["gas"] = DEFAULT_GAS_ESTIMATE_FALLBACK

                if "maxFeePerGas" in tx or "maxPriorityFeePerGas" in tx:
                    if "maxFeePerGas" in tx:
                        tx["maxFeePerGas"] = self._normalize_int(tx["maxFeePerGas"])
                    else:
                        base = await w3.eth.gas_price
                        tx["maxFeePerGas"] = int(base * 2)

                    if "maxPriorityFeePerGas" in tx:
                        tx["maxPriorityFeePerGas"] = self._normalize_int(
                            tx["maxPriorityFeePerGas"]
                        )
                    else:
                        tx["maxPriorityFeePerGas"] = int(ONE_GWEI)
                    tx["type"] = 2
                else:
                    if "gasPrice" in tx:
                        tx["gasPrice"] = self._normalize_int(tx["gasPrice"])
                    else:
                        gas_price = await w3.eth.gas_price
                        tx["gasPrice"] = int(gas_price)

                signed_tx = self._sign_transaction(tx, checksum_from)
                try:
                    tx_hash = await w3.eth.send_raw_transaction(signed_tx)
                    tx_hash_hex = tx_hash.hex() if hasattr(tx_hash, "hex") else tx_hash

                    result: dict[str, Any] = {"tx_hash": tx_hash_hex}
                    if wait_for_receipt:
                        receipt = await w3.eth.wait_for_transaction_receipt(
                            tx_hash, timeout=timeout
                        )
                        result["receipt"] = self._format_receipt(receipt)
                        # After successful receipt, sync nonce from chain to ensure accuracy
                        chain_nonce = await w3.eth.get_transaction_count(
                            checksum_from, "latest"
                        )
                        await self._nonce_manager.sync_nonce(
                            checksum_from, tx["chainId"], chain_nonce
                        )

                    return (True, result)
                except Exception as send_exc:
                    # If transaction fails due to nonce error, sync with chain and retry once
                    # Handle both string errors and dict errors (like {'code': -32000, 'message': '...'})
                    error_msg = str(send_exc)
                    if isinstance(send_exc, dict):
                        error_msg = send_exc.get("message", str(send_exc))
                    elif hasattr(send_exc, "message"):
                        error_msg = str(send_exc.message)

                    if "nonce" in error_msg.lower() and "too low" in error_msg.lower():
                        self.logger.warning(
                            f"Nonce error detected, syncing with chain: {error_msg}"
                        )
                        # Sync with chain nonce
                        chain_nonce = await w3.eth.get_transaction_count(
                            checksum_from, "pending"
                        )
                        await self._nonce_manager.sync_nonce(
                            checksum_from, tx["chainId"], chain_nonce
                        )
                        # Update tx nonce and retry
                        tx["nonce"] = await self._nonce_manager.get_next_nonce(
                            checksum_from, tx["chainId"], w3
                        )
                        signed_tx = self._sign_transaction(tx, checksum_from)
                        tx_hash = await w3.eth.send_raw_transaction(signed_tx)
                        tx_hash_hex = (
                            tx_hash.hex() if hasattr(tx_hash, "hex") else tx_hash
                        )

                        result: dict[str, Any] = {"tx_hash": tx_hash_hex}
                        if wait_for_receipt:
                            receipt = await w3.eth.wait_for_transaction_receipt(
                                tx_hash, timeout=timeout
                            )
                            result["receipt"] = self._format_receipt(receipt)
                            # Sync again after successful receipt
                            chain_nonce = await w3.eth.get_transaction_count(
                                checksum_from, "latest"
                            )
                            await self._nonce_manager.sync_nonce(
                                checksum_from, tx["chainId"], chain_nonce
                            )

                        return (True, result)
                    # Re-raise if it's not a nonce error
                    raise
            finally:
                await self._close_web3(w3)
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"Transaction broadcast failed: {exc}")
            return (False, f"Transaction broadcast failed: {exc}")

    async def transaction_succeeded(
        self, tx_hash: str, chain_id: int, timeout: int = 120
    ) -> bool:
        """Return True if the transaction hash completed successfully on-chain."""
        w3 = self.get_web3(chain_id)
        try:
            receipt = await w3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=timeout
            )
            status = getattr(receipt, "status", None)
            if status is None and isinstance(receipt, dict):
                status = receipt.get("status")
            return status == 1
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(
                f"Failed to confirm transaction {tx_hash} on chain {chain_id}: {exc}"
            )
            return False
        finally:
            await self._close_web3(w3)

    def _sign_transaction(
        self, transaction: dict[str, Any], from_address: str
    ) -> bytes:
        private_key = resolve_private_key_for_from_address(from_address, self.config)
        if not private_key:
            raise ValueError(f"No private key available for address {from_address}")
        signed = Account.sign_transaction(transaction, private_key)
        return signed.raw_transaction

    def _resolve_rpc_url(self, chain_id: int) -> str:
        return resolve_rpc_url(chain_id, self.config or {}, None)

    async def _close_web3(self, w3: AsyncWeb3) -> None:
        try:
            await w3.provider.session.close()
        except Exception:  # noqa: BLE001
            pass

    def _format_receipt(self, receipt: Any) -> dict[str, Any]:
        tx_hash = getattr(receipt, "transactionHash", None)
        if hasattr(tx_hash, "hex"):
            tx_hash = tx_hash.hex()

        return {
            "transactionHash": tx_hash,
            "status": (
                getattr(receipt, "status", None)
                if not isinstance(receipt, dict)
                else receipt.get("status")
            ),
            "blockNumber": (
                getattr(receipt, "blockNumber", None)
                if not isinstance(receipt, dict)
                else receipt.get("blockNumber")
            ),
            "gasUsed": (
                getattr(receipt, "gasUsed", None)
                if not isinstance(receipt, dict)
                else receipt.get("gasUsed")
            ),
            "logs": (
                [
                    dict(log_entry) if not isinstance(log_entry, dict) else log_entry
                    for log_entry in getattr(receipt, "logs", [])
                ]
                if hasattr(receipt, "logs")
                else receipt.get("logs")
                if isinstance(receipt, dict)
                else []
            ),
        }

    def _normalize_int(self, value: Any) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            if value.startswith("0x"):
                return int(value, 16)
            try:
                return int(value)
            except ValueError:
                return int(float(value))
        raise ValueError(f"Unable to convert value '{value}' to int")
