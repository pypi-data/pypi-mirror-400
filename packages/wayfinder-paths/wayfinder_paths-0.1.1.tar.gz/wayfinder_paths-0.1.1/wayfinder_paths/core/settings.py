import json
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreSettings(BaseSettings):
    """
    Core settings for Wayfinder Vaults Engine
    These are minimal settings required by the core engine
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables (e.g., from Django)
    )

    # Core API Configuration
    API_ENV: str = Field("development", env="API_ENV")

    def _compute_default_api_url() -> str:
        """
        Determine default API base URL from config.json if present, otherwise fallback.
        Do not mutate the value (consistent with rpc_urls resolution).
        """
        cfg_path = os.getenv("WAYFINDER_CONFIG_PATH", "config.json")
        base = None
        try:
            with open(cfg_path) as f:
                cfg = json.load(f)
            system = cfg.get("system", {}) if isinstance(cfg, dict) else {}
            candidate = system.get("api_base_url")
            if isinstance(candidate, str) and candidate.strip():
                base = candidate.strip()
        except Exception:
            # Config is optional; ignore errors and use fallback
            pass

        if not base:
            # Provide a sensible default that includes the full API root
            base = "https://wayfinder.ai/api/v1"
        return base

    WAYFINDER_API_URL: str = Field(_compute_default_api_url(), env="WAYFINDER_API_URL")

    # Network Configuration
    NETWORK: str = Field("testnet", env="NETWORK")  # mainnet, testnet, devnet

    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field("logs/vault.log", env="LOG_FILE")

    # Safety
    DRY_RUN: bool = Field(False, env="DRY_RUN")


# Core settings instance
settings = CoreSettings()
