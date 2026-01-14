from __future__ import annotations

from wayfinder_paths.core.services.base import EvmTxn, TokenTxn, Web3Service
from wayfinder_paths.core.services.local_evm_txn import LocalEvmTxn
from wayfinder_paths.core.services.local_token_txn import (
    LocalTokenTxnService,
)


class DefaultWeb3Service(Web3Service):
    """Default implementation that simply wires the provided dependencies together."""

    def __init__(
        self,
        config: dict | None = None,
        *,
        wallet_provider: EvmTxn | None = None,
        evm_transactions: TokenTxn | None = None,
        simulation: bool = False,
    ) -> None:
        """
        Initialize the service with optional dependency injection.

        Strategies that already constructed wallet providers or transaction helpers
        can pass them in directly. Otherwise we fall back to the legacy behavior of
        building a LocalWalletProvider + DefaultEvmTransactionService from config.
        """
        cfg = config or {}
        self._wallet_provider = wallet_provider or LocalEvmTxn(cfg)
        if evm_transactions is not None:
            self._evm_transactions = evm_transactions
        else:
            self._evm_transactions = LocalTokenTxnService(
                config=cfg,
                wallet_provider=self._wallet_provider,
                simulation=simulation,
            )

    @property
    def evm_transactions(self) -> EvmTxn:
        return self._wallet_provider

    @property
    def token_transactions(self) -> TokenTxn:
        return self._evm_transactions
