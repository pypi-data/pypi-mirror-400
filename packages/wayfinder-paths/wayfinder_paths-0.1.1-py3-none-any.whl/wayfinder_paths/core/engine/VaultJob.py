import asyncio
import os
from typing import Any

from loguru import logger

from wayfinder_paths.core.clients.ClientManager import ClientManager
from wayfinder_paths.core.config import VaultConfig
from wayfinder_paths.core.strategies.Strategy import Strategy


class VaultJob:
    def __init__(
        self,
        strategy: Strategy,
        config: VaultConfig,
        clients: dict[str, Any] | None = None,
        skip_auth: bool = False,
        api_key: str | None = None,
    ):
        """
        Initialize a VaultJob.

        Args:
            strategy: The strategy to execute.
            config: Vault configuration.
            clients: Optional dict of pre-instantiated clients to inject directly.
            skip_auth: If True, skips authentication (for SDK usage).
            api_key: Optional API key for service account authentication.
                If provided, will be passed to ClientManager and strategy.
        """
        self.strategy = strategy
        self.config = config

        self.job_id = strategy.name or "unknown"
        self.clients = ClientManager(
            clients=clients, skip_auth=skip_auth, api_key=api_key
        )

    def _setup_strategy(self):
        """Setup the strategy instance"""
        if not self.strategy:
            raise ValueError("No strategy provided to VaultJob")

        self.strategy.log = self.log

    def _is_using_api_key(self) -> bool:
        """Check if API key authentication is being used."""
        if self.clients._api_key:
            return True

        if self.clients.auth:
            try:
                creds = self.clients.auth._load_config_credentials()
                if creds.get("api_key"):
                    return True
                if os.getenv("WAYFINDER_API_KEY"):
                    return True
            except Exception:
                pass

        return False

    async def setup(self):
        """
        Initialize the vault job and strategy.

        Sets up authentication and initializes the strategy with merged configuration.
        """
        self._setup_strategy()

        # Ensure auth token is set for API calls
        if not self.clients._skip_auth:
            is_api_key_auth = self._is_using_api_key()

            if is_api_key_auth:
                logger.debug("Using API key authentication")
                if self.clients.auth:
                    await self.clients.auth._ensure_bearer_token()
            else:
                # Try to ensure bearer token is set, authenticate if needed
                try:
                    if self.clients.auth:
                        await self.clients.auth._ensure_bearer_token()
                except (PermissionError, Exception) as e:
                    if not isinstance(e, PermissionError):
                        logger.warning(
                            f"Authentication failed: {e}, trying OAuth fallback"
                        )
                    username = self.config.user.username
                    password = self.config.user.password
                    refresh_token = self.config.user.refresh_token
                    if refresh_token or (username and password):
                        await self.clients.authenticate(
                            username=username,
                            password=password,
                            refresh_token=refresh_token,
                        )
                    else:
                        raise ValueError(
                            "Authentication required: provide api_key parameter for service account auth, "
                            "or username+password/refresh_token in config.json for personal access"
                        ) from e

        existing_cfg = dict(getattr(self.strategy, "config", {}) or {})
        vault_cfg = dict(self.config.strategy_config or {})
        merged_cfg = {**vault_cfg, **existing_cfg}
        self.strategy.config = merged_cfg
        self.strategy.clients = self.clients
        await self.strategy.setup()

    async def execute_strategy(self, action: str, **kwargs) -> dict[str, Any]:
        """Execute a strategy action (deposit, withdraw, update, status, partial_liquidate)"""
        try:
            if action == "deposit":
                result = await self.strategy.deposit(**kwargs)
            elif action == "withdraw":
                result = await self.strategy.withdraw(**kwargs)
            elif action == "update":
                result = await self.strategy.update()
            elif action == "status":
                result = await self.strategy.status()
            elif action == "partial_liquidate":
                usd_value = kwargs.get("usd_value")
                if usd_value is None:
                    result = (
                        False,
                        "usd_value parameter is required for partial_liquidate",
                    )
                else:
                    result = await self.strategy.partial_liquidate(usd_value)
            else:
                result = {"success": False, "message": f"Unknown action: {action}"}

            await self.log(f"Strategy action '{action}' completed: {result}")
            return result

        except Exception as e:
            error_msg = f"Strategy action '{action}' failed: {str(e)}"
            await self.log(error_msg)
            await self.handle_error({"error": str(e), "action": action})
            return {"success": False, "error": str(e)}

    async def run_continuous(self, interval_seconds: int | None = None):
        """Run the strategy continuously at specified intervals"""
        interval = interval_seconds or self.config.system.update_interval
        logger.info(
            f"Starting continuous execution for strategy: {self.strategy.name} with interval {interval}s"
        )

        while True:
            try:
                await self.execute_strategy("update")
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                logger.info("Continuous execution cancelled")
                break
            except Exception as e:
                logger.error(f"Error in continuous execution: {str(e)}")
                await asyncio.sleep(interval)

    async def message_user(self, msg):
        if msg is not None:
            logger.info(f"notifying user: {msg}")
            await self.clients.chat.send_msg_to_owner(
                msg, "agent", self.clients.chat.session_id
            )

    async def log(self, msg: str):
        """Log messages for the job"""
        logger.info(f"Job {self.job_id}: {msg}")

    async def handle_error(self, error_data):
        pass

    async def stop(self):
        """Stop the vault job and cleanup"""
        if hasattr(self.strategy, "stop"):
            await self.strategy.stop()

        logger.info(f"Vault job {self.job_id} stopped")
