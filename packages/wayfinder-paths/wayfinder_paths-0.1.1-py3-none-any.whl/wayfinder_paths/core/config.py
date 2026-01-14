"""
Core Configuration System
Separates user-provided configuration from system configuration
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class UserConfig:
    """
    User-provided configuration
    These are values that users MUST provide to run strategies
    """

    # Credential-based auth (JWT)
    username: str | None = None
    password: str | None = None
    refresh_token: str | None = None

    # Wallet configuration
    main_wallet_address: str | None = None  # User's main wallet address
    vault_wallet_address: str | None = None  # Dedicated vault wallet address

    # Optional user preferences
    default_slippage: float = 0.005  # Default slippage tolerance (0.5%)
    gas_multiplier: float = 1.2  # Gas limit multiplier for safety

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserConfig":
        """Create UserConfig from dictionary"""
        return cls(
            username=data.get("username"),
            password=data.get("password"),
            refresh_token=data.get("refresh_token"),
            main_wallet_address=data.get("main_wallet_address"),
            vault_wallet_address=data.get("vault_wallet_address"),
            default_slippage=data.get("default_slippage", 0.005),
            gas_multiplier=data.get("gas_multiplier", 1.2),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "username": self.username,
            "password": self.password,
            "refresh_token": self.refresh_token,
            "main_wallet_address": self.main_wallet_address,
            "vault_wallet_address": self.vault_wallet_address,
            "default_slippage": self.default_slippage,
            "gas_multiplier": self.gas_multiplier,
        }


@dataclass
class SystemConfig:
    """
    System-level configuration
    These are values managed by the Wayfinder system
    """

    # API endpoints (populated from environment or defaults)
    api_base_url: str = field(
        default_factory=lambda: os.getenv(
            "WAYFINDER_API_URL", "https://api.wayfinder.ai"
        )
    )

    # Job configuration
    job_id: str | None = None
    job_type: str = "vault"

    # Execution settings
    update_interval: int = 60  # Default update interval in seconds
    max_retries: int = 3  # Maximum retries for failed operations
    retry_delay: int = 5  # Delay between retries in seconds

    # System paths
    log_path: str | None = None
    data_path: str | None = None

    # Local wallets.json path used to auto-populate wallet addresses when not provided
    wallets_path: str | None = "wallets.json"

    # Optional wallet_id for policy rendering
    wallet_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SystemConfig":
        """Create SystemConfig from dictionary"""
        return cls(
            api_base_url=data.get(
                "api_base_url",
                os.getenv("WAYFINDER_API_URL", "https://api.wayfinder.ai"),
            ),
            job_id=data.get("job_id"),
            job_type=data.get("job_type", "vault"),
            update_interval=data.get("update_interval", 60),
            max_retries=data.get("max_retries", 3),
            retry_delay=data.get("retry_delay", 5),
            log_path=data.get("log_path"),
            data_path=data.get("data_path"),
            wallets_path=data.get(
                "wallets_path", os.getenv("WALLETS_PATH", "wallets.json")
            ),
            wallet_id=data.get("wallet_id") or os.getenv("WALLET_ID"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "api_base_url": self.api_base_url,
            "job_id": self.job_id,
            "job_type": self.job_type,
            "update_interval": self.update_interval,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "log_path": self.log_path,
            "data_path": self.data_path,
            "wallets_path": self.wallets_path,
            "wallet_id": self.wallet_id,
        }


@dataclass
class VaultConfig:
    """
    Complete configuration for a vault job
    Combines user and system configurations
    """

    user: UserConfig
    system: SystemConfig
    strategy_config: dict[str, Any] = field(
        default_factory=dict
    )  # Strategy-specific configuration

    def __post_init__(self) -> None:
        """
        Enrich strategy_config with wallet addresses and private keys from wallets.json.

        This method automatically loads wallet information from wallets.json to populate
        main_wallet and vault_wallet addresses in strategy_config. Only uses wallets
        with exact label matches (no fallbacks).

        Wallet enrichment is conditional and can be skipped:
        - Skipped if wallet_type is explicitly set to a non-"local" value
        - Only performed if wallet_type is None, "local", or not specified
        - Allows custom wallet providers (Privy/Turnkey) to opt out of file-based enrichment

        Note:
            This method never raises exceptions - all errors are silently caught to
            prevent config construction failures.
        """
        try:
            if not isinstance(self.strategy_config, dict):
                self.strategy_config = {}

            # Check wallet_type early - skip enrichment if using non-local wallet provider
            wallet_type = self.strategy_config.get("wallet_type")
            # Also check in main_wallet and vault_wallet configs
            if not wallet_type:
                main_wallet = self.strategy_config.get("main_wallet")
                if isinstance(main_wallet, dict):
                    wallet_type = main_wallet.get("wallet_type")
            if not wallet_type:
                vault_wallet = self.strategy_config.get("vault_wallet")
                if isinstance(vault_wallet, dict):
                    wallet_type = vault_wallet.get("wallet_type")

            # Skip wallets.json enrichment if explicitly using non-local wallet provider
            if wallet_type and wallet_type != "local":
                return

            # Get strategy name if available (for per-strategy wallet lookup)
            strategy_name = self.strategy_config.get("_strategy_name")

            # Load wallets from file for enrichment (only for local wallet types)
            entries = _read_wallets_file(self.system.wallets_path)
            by_label = {}
            by_addr = {}
            if entries and isinstance(entries, list):
                for e in entries:
                    if isinstance(e, dict):
                        # Index by label
                        label = e.get("label")
                        if isinstance(label, str):
                            by_label[label] = e
                        # Index by address
                        addr = e.get("address")
                        if isinstance(addr, str):
                            by_addr[addr.lower()] = e

            # Load main wallet by exact label match only
            if "main_wallet" not in self.strategy_config:
                main_wallet = by_label.get("main")
                if main_wallet:
                    self.strategy_config["main_wallet"] = {
                        "address": main_wallet["address"]
                    }

            # Load vault wallet by strategy name label match only
            if strategy_name and isinstance(strategy_name, str):
                strategy_wallet = by_label.get(strategy_name)
                if strategy_wallet:
                    # Use strategy-specific wallet as vault_wallet
                    if "vault_wallet" not in self.strategy_config:
                        self.strategy_config["vault_wallet"] = {
                            "address": strategy_wallet["address"]
                        }
                    elif isinstance(self.strategy_config.get("vault_wallet"), dict):
                        # Ensure address is set if not already
                        if not self.strategy_config["vault_wallet"].get("address"):
                            self.strategy_config["vault_wallet"]["address"] = (
                                strategy_wallet["address"]
                            )

            # Enrich wallet configs with private keys from wallets.json
            # Only enrich private keys if using local wallet type (or defaulting to local)
            # This ensures custom wallet providers don't get private keys from files
            if wallet_type in (None, "local"):
                try:
                    for key in ("main_wallet", "vault_wallet"):
                        wallet_obj = self.strategy_config.get(key)
                        if isinstance(wallet_obj, dict):
                            addr = (wallet_obj.get("address") or "").lower()
                            entry = by_addr.get(addr)
                            if entry:
                                pk = entry.get("private_key") or entry.get(
                                    "private_key_hex"
                                )
                                if (
                                    pk
                                    and not wallet_obj.get("private_key")
                                    and not wallet_obj.get("private_key_hex")
                                ):
                                    wallet_obj["private_key_hex"] = pk
                except Exception:
                    pass
        except Exception:
            # Defensive: never allow config construction to fail on enrichment
            pass

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], strategy_name: str | None = None
    ) -> "VaultConfig":
        """Create VaultConfig from dictionary

        Args:
            data: Configuration dictionary
            strategy_name: Optional strategy name for per-strategy wallet lookup
        """
        user_cfg = UserConfig.from_dict(data.get("user", {}))
        sys_cfg = SystemConfig.from_dict(data.get("system", {}))
        # No auto-population - wallets must be explicitly set in config or matched by label
        strategy_config = data.get("strategy", {})
        # Store strategy name in config for wallet lookup
        if strategy_name:
            strategy_config["_strategy_name"] = strategy_name
        return cls(
            user=user_cfg,
            system=sys_cfg,
            strategy_config=strategy_config,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user": self.user.to_dict(),
            "system": self.system.to_dict(),
            "strategy": self.strategy_config,
        }

    def get_adapter_config(self, adapter_name: str) -> dict[str, Any]:
        """
        Get configuration for a specific adapter
        Combines relevant user and system settings
        """
        config = {
            "api_base_url": self.system.api_base_url,
        }

        # Add wallet configuration if needed
        # Only use wallets from strategy_config (matched by label) - no fallbacks
        if adapter_name in ["balance", "brap", "moonwell", "hyperliquid"]:
            vault_wallet = self.strategy_config.get("vault_wallet")
            main_wallet = self.strategy_config.get("main_wallet")
            config["vault_wallet"] = (
                {"address": vault_wallet["address"]}
                if vault_wallet
                and isinstance(vault_wallet, dict)
                and vault_wallet.get("address")
                else {}
            )
            config["main_wallet"] = (
                {"address": main_wallet["address"]}
                if main_wallet
                and isinstance(main_wallet, dict)
                and main_wallet.get("address")
                else {}
            )
            # user_wallet uses vault_wallet if available, otherwise main_wallet
            config["user_wallet"] = (
                config.get("vault_wallet") or config.get("main_wallet") or {}
            )

        # Add specific settings
        if adapter_name == "brap":
            config["default_slippage"] = self.user.default_slippage
            config["gas_multiplier"] = self.user.gas_multiplier

        # Add any strategy-specific adapter config
        if adapter_name in self.strategy_config.get("adapters", {}):
            config.update(self.strategy_config["adapters"][adapter_name])

        return config


def load_config_from_env() -> VaultConfig:
    """
    Load configuration from environment variables
    This is the simplest way for users to provide configuration
    """
    user_config = UserConfig(
        username=os.getenv("WAYFINDER_USERNAME"),
        password=os.getenv("WAYFINDER_PASSWORD"),
        refresh_token=os.getenv("WAYFINDER_REFRESH_TOKEN"),
        main_wallet_address=os.getenv("MAIN_WALLET_ADDRESS"),
        vault_wallet_address=os.getenv("VAULT_WALLET_ADDRESS"),
        default_slippage=float(os.getenv("DEFAULT_SLIPPAGE", "0.005")),
        gas_multiplier=float(os.getenv("GAS_MULTIPLIER", "1.2")),
    )

    system_config = SystemConfig(
        api_base_url=os.getenv("WAYFINDER_API_URL", "https://api.wayfinder.ai"),
        job_id=os.getenv("JOB_ID"),
        update_interval=int(os.getenv("UPDATE_INTERVAL", "60")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        retry_delay=int(os.getenv("RETRY_DELAY", "5")),
        wallets_path=os.getenv("WALLETS_PATH", "wallets.json"),
        wallet_id=os.getenv("WALLET_ID"),
    )

    # No auto-population - wallets must be explicitly set in environment or matched by label

    return VaultConfig(user=user_config, system=system_config)


# --- Internal helpers -------------------------------------------------------


def _read_wallets_file(wallets_path: str | None) -> list[dict[str, Any]]:
    if not wallets_path:
        return []
    path = Path(wallets_path)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []
