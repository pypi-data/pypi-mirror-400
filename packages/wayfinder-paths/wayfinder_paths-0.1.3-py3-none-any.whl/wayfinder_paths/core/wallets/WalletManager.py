"""
Wallet Manager

Factory class for resolving and instantiating wallet providers based on configuration.
Provides convenience methods for config-based wallet provider resolution.
"""

from typing import Any

from loguru import logger

from wayfinder_paths.core.services.base import EvmTxn
from wayfinder_paths.core.services.local_evm_txn import LocalEvmTxn


class WalletManager:
    """
    Factory class for wallet providers.

    Resolves appropriate wallet provider based on config, defaulting to LocalWalletProvider.
    This is a convenience helper - adapters support direct injection, making this optional.
    """

    @staticmethod
    def get_provider(config: dict[str, Any] | None = None) -> EvmTxn:
        """
        Get wallet provider based on configuration.

        Args:
            config: Configuration dictionary. May contain wallet_type in wallet configs.

        Returns:
            WalletProvider instance. Defaults to LocalWalletProvider if no type specified.
        """
        config = config or {}
        wallet_type = config.get("wallet_type")

        if not wallet_type:
            main_wallet = config.get("main_wallet")
            if isinstance(main_wallet, dict):
                wallet_type = main_wallet.get("wallet_type")

        if not wallet_type:
            vault_wallet = config.get("vault_wallet")
            if isinstance(vault_wallet, dict):
                wallet_type = vault_wallet.get("wallet_type")

        if not wallet_type or wallet_type == "local":
            logger.debug("Using LocalWalletProvider (default)")
            return LocalEvmTxn(config)

        logger.warning(
            f"Unknown wallet_type '{wallet_type}', defaulting to LocalWalletProvider. "
            "To use custom wallet providers, inject them directly into adapters."
        )
        return LocalEvmTxn(config)
