"""
Client Manager
Consolidated client management for all API interactions
"""

from typing import Any

from wayfinder_paths.core.clients.AuthClient import AuthClient
from wayfinder_paths.core.clients.BRAPClient import BRAPClient
from wayfinder_paths.core.clients.HyperlendClient import HyperlendClient
from wayfinder_paths.core.clients.LedgerClient import LedgerClient
from wayfinder_paths.core.clients.PoolClient import PoolClient
from wayfinder_paths.core.clients.protocols import (
    BRAPClientProtocol,
    HyperlendClientProtocol,
    LedgerClientProtocol,
    PoolClientProtocol,
    SimulationClientProtocol,
    TokenClientProtocol,
    TransactionClientProtocol,
    WalletClientProtocol,
)
from wayfinder_paths.core.clients.SimulationClient import SimulationClient
from wayfinder_paths.core.clients.TokenClient import TokenClient
from wayfinder_paths.core.clients.TransactionClient import TransactionClient
from wayfinder_paths.core.clients.WalletClient import WalletClient


class ClientManager:
    """
    Manages all API client instances for a vault job.

    Args:
        clients: Optional dict of pre-instantiated clients to inject directly.
            Keys: 'token', 'hyperlend', 'ledger', 'wallet', 'transaction', 'pool', 'brap', 'simulation'.
            If not provided, defaults to HTTP-based clients.
        skip_auth: If True, skips authentication (for SDK usage).
    """

    def __init__(
        self,
        clients: dict[str, Any] | None = None,
        skip_auth: bool = False,
        api_key: str | None = None,
    ):
        """
        Initialize ClientManager.

        Args:
            clients: Optional dict of pre-instantiated clients to inject directly.
            skip_auth: If True, skips authentication (for SDK usage).
            api_key: Optional API key for service account authentication.
        """
        self._injected_clients = clients or {}
        self._skip_auth = skip_auth
        self._api_key = api_key
        self._access_token: str | None = None

        self._auth_client: AuthClient | None = None
        self._token_client: TokenClientProtocol | None = None
        self._wallet_client: WalletClientProtocol | None = None
        self._transaction_client: TransactionClientProtocol | None = None
        self._ledger_client: LedgerClientProtocol | None = None
        self._pool_client: PoolClientProtocol | None = None
        self._hyperlend_client: HyperlendClientProtocol | None = None
        self._brap_client: BRAPClientProtocol | None = None
        self._simulation_client: SimulationClientProtocol | None = None

    @property
    def auth(self) -> AuthClient | None:
        """Get or create auth client. Returns None if skip_auth=True."""
        if self._skip_auth:
            return None
        if not self._auth_client:
            self._auth_client = AuthClient(api_key=self._api_key)
            if self._access_token:
                self._auth_client.set_bearer_token(self._access_token)
        return self._auth_client

    @property
    def token(self) -> TokenClientProtocol:
        """Get or create token client"""
        if not self._token_client:
            self._token_client = self._injected_clients.get("token") or TokenClient(
                api_key=self._api_key
            )
            if self._access_token and hasattr(self._token_client, "set_bearer_token"):
                self._token_client.set_bearer_token(self._access_token)
        return self._token_client

    @property
    def transaction(self) -> TransactionClientProtocol:
        """Get or create transaction client"""
        if not self._transaction_client:
            self._transaction_client = self._injected_clients.get(
                "transaction"
            ) or TransactionClient(api_key=self._api_key)
            if self._access_token and hasattr(
                self._transaction_client, "set_bearer_token"
            ):
                self._transaction_client.set_bearer_token(self._access_token)
        return self._transaction_client

    @property
    def ledger(self) -> LedgerClientProtocol:
        """Get or create ledger client"""
        if not self._ledger_client:
            self._ledger_client = self._injected_clients.get("ledger") or LedgerClient(
                api_key=self._api_key
            )
            if self._access_token and hasattr(self._ledger_client, "set_bearer_token"):
                self._ledger_client.set_bearer_token(self._access_token)
        return self._ledger_client

    @property
    def pool(self) -> PoolClientProtocol:
        """Get or create pool client"""
        if not self._pool_client:
            self._pool_client = self._injected_clients.get("pool") or PoolClient(
                api_key=self._api_key
            )
            if self._access_token and hasattr(self._pool_client, "set_bearer_token"):
                self._pool_client.set_bearer_token(self._access_token)
        return self._pool_client

    @property
    def hyperlend(self) -> HyperlendClientProtocol:
        """Get or create hyperlend client"""
        if not self._hyperlend_client:
            self._hyperlend_client = self._injected_clients.get(
                "hyperlend"
            ) or HyperlendClient(api_key=self._api_key)
            if self._access_token and hasattr(
                self._hyperlend_client, "set_bearer_token"
            ):
                self._hyperlend_client.set_bearer_token(self._access_token)
        return self._hyperlend_client

    @property
    def wallet(self) -> WalletClientProtocol:
        """Get or create wallet client"""
        if not self._wallet_client:
            self._wallet_client = self._injected_clients.get("wallet") or WalletClient(
                api_key=self._api_key
            )
            if self._access_token and hasattr(self._wallet_client, "set_bearer_token"):
                self._wallet_client.set_bearer_token(self._access_token)
        return self._wallet_client

    @property
    def brap(self) -> BRAPClientProtocol:
        """Get or create BRAP client"""
        if not self._brap_client:
            self._brap_client = self._injected_clients.get("brap") or BRAPClient(
                api_key=self._api_key
            )
            if self._access_token and hasattr(self._brap_client, "set_bearer_token"):
                self._brap_client.set_bearer_token(self._access_token)
        return self._brap_client

    @property
    def simulation(self) -> SimulationClientProtocol:
        """Get or create simulation client"""
        if not self._simulation_client:
            self._simulation_client = self._injected_clients.get(
                "simulation"
            ) or SimulationClient(api_key=self._api_key)
            if self._access_token and hasattr(
                self._simulation_client, "set_bearer_token"
            ):
                self._simulation_client.set_bearer_token(self._access_token)
        return self._simulation_client

    async def authenticate(
        self,
        username: str | None = None,
        password: str | None = None,
        *,
        refresh_token: str | None = None,
    ) -> dict[str, Any]:
        """Authenticate with the API. Raises ValueError if skip_auth=True."""
        if self._skip_auth:
            raise ValueError(
                "Authentication is disabled in SDK mode. SDK users handle their own authentication."
            )
        auth_client = self.auth
        if auth_client is None:
            raise ValueError("Auth client is not available")
        data = await auth_client.authenticate(
            username, password, refresh_token=refresh_token
        )
        access = data.get("access") or data.get("access_token")
        if access:
            self.set_access_token(access)
        return data

    def set_access_token(self, access_token: str) -> None:
        """Set and propagate access token to all initialized clients."""
        self._access_token = access_token
        if self._auth_client:
            self._auth_client.set_bearer_token(access_token)
        if self._token_client and hasattr(self._token_client, "set_bearer_token"):
            self._token_client.set_bearer_token(access_token)
        if self._transaction_client and hasattr(
            self._transaction_client, "set_bearer_token"
        ):
            self._transaction_client.set_bearer_token(access_token)
        if self._ledger_client and hasattr(self._ledger_client, "set_bearer_token"):
            self._ledger_client.set_bearer_token(access_token)
        if self._pool_client and hasattr(self._pool_client, "set_bearer_token"):
            self._pool_client.set_bearer_token(access_token)
        if self._hyperlend_client and hasattr(
            self._hyperlend_client, "set_bearer_token"
        ):
            self._hyperlend_client.set_bearer_token(access_token)
        if self._wallet_client and hasattr(self._wallet_client, "set_bearer_token"):
            self._wallet_client.set_bearer_token(access_token)

    def get_all_clients(self) -> dict[str, Any]:
        """Get all initialized clients for direct access"""
        return {
            "auth": self._auth_client,
            "token": self._token_client,
            "transaction": self._transaction_client,
            "ledger": self._ledger_client,
            "pool": self._pool_client,
            "wallet": self._wallet_client,
            "hyperlend": self._hyperlend_client,
            "brap": self._brap_client,
            "simulation": self._simulation_client,
        }
