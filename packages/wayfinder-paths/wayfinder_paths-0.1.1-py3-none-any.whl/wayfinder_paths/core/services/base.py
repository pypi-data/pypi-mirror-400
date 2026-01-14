from abc import ABC, abstractmethod
from typing import Any

from web3 import AsyncWeb3


class TokenTxn(ABC):
    """Interface describing high-level EVM transaction builders."""

    @abstractmethod
    async def build_send(
        self,
        *,
        token_id: str,
        amount: float,
        from_address: str,
        to_address: str,
        token_info: dict[str, Any] | None = None,
    ) -> tuple[bool, dict[str, Any] | str]:
        """Build raw transaction data for sending tokens."""

    @abstractmethod
    def build_erc20_approve(
        self,
        *,
        chain_id: int,
        token_address: str,
        from_address: str,
        spender: str,
        amount: int,
    ) -> tuple[bool, dict[str, Any] | str]:
        """Build raw ERC20 approve transaction data."""

    @abstractmethod
    async def read_erc20_allowance(
        self, chain: Any, token_address: str, from_address: str, spender_address: str
    ) -> dict[str, Any]:
        """Read allowance granted for a spender."""


class EvmTxn(ABC):
    """
    Abstract base class for wallet providers.

    This interface abstracts all blockchain interactions needed by adapters so the
    rest of the vaults codebase never touches raw web3 primitives. Implementations
    are responsible for RPC resolution, gas estimation, signing, broadcasting and
    transaction confirmations.
    """

    @abstractmethod
    async def get_balance(
        self,
        address: str,
        token_address: str | None,
        chain_id: int,
    ) -> tuple[bool, Any]:
        """
        Get balance for an address.

        Args:
            address: Address to query balance for
            token_address: ERC20 token address, or None for native token
            chain_id: Chain ID

        Returns:
            Tuple of (success, balance_integer_or_error_message)
        """
        pass

    @abstractmethod
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

        Args:
            token_address: ERC20 token contract address
            spender: Address being approved to spend tokens
            amount: Amount to approve (in token units, not human-readable)
            from_address: Address approving the tokens
            chain_id: Chain ID
            wait_for_receipt: Whether to wait for the transaction receipt
            timeout: Receipt timeout in seconds

        Returns:
            Tuple of (success, transaction_result_dict_or_error_message)
            Transaction result should include 'tx_hash' and optionally 'receipt'
        """
        pass

    @abstractmethod
    async def broadcast_transaction(
        self,
        transaction: dict[str, Any],
        *,
        wait_for_receipt: bool = True,
        timeout: int = 120,
    ) -> tuple[bool, Any]:
        """
        Sign and broadcast a transaction dict.

        Providers must handle gas estimation, gas pricing, nonce selection, signing
        and submission internally so callers can simply pass the transaction data.

        Args:
            transaction: Dictionary describing the transaction (to, data, value, etc.)
            wait_for_receipt: Whether to wait for the transaction receipt
            timeout: Receipt timeout in seconds
        """
        pass

    @abstractmethod
    async def transaction_succeeded(
        self, tx_hash: str, chain_id: int, timeout: int = 120
    ) -> bool:
        """
        Check if a transaction hash succeeded on-chain.

        Args:
            tx_hash: Transaction hash to inspect
            chain_id: Chain ID where the transaction was broadcast
            timeout: Maximum seconds to wait for a receipt

        Returns:
            Boolean indicating whether the transaction completed successfully.
        """
        pass

    @abstractmethod
    def get_web3(self, chain_id: int) -> AsyncWeb3:
        """
        Return an AsyncWeb3 instance configured for the given chain.

        Implementations may create new instances per call or pull from an internal
        cache, but they must document whether the caller is responsible for closing
        the underlying HTTP session.
        """
        pass


class Web3Service(ABC):
    """Facade that exposes low-level wallet access and higher-level EVM helpers."""

    @property
    @abstractmethod
    def evm_transactions(self) -> EvmTxn:
        """Return the wallet provider responsible for RPC, signing, and broadcasting."""

    @property
    @abstractmethod
    def token_transactions(self) -> TokenTxn:
        """Returns TokenTxn, for sends and swaps of any token"""

    async def broadcast_transaction(
        self,
        transaction: dict[str, Any],
        *,
        wait_for_receipt: bool = True,
        timeout: int = 120,
    ) -> tuple[bool, Any]:
        """Proxy convenience wrapper to underlying wallet provider."""
        return await self.evm_transactions.broadcast_transaction(
            transaction, wait_for_receipt=wait_for_receipt, timeout=timeout
        )

    def get_web3(self, chain_id: int):
        """Expose underlying web3 provider for ABI encoding helpers."""
        return self.evm_transactions.get_web3(chain_id)
