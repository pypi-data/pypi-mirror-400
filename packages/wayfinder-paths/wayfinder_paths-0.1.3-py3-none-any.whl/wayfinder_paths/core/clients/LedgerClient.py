from typing import Any

from wayfinder_paths.core.clients.AuthClient import AuthClient
from wayfinder_paths.core.clients.WayfinderClient import WayfinderClient
from wayfinder_paths.core.settings import settings


class LedgerClient(WayfinderClient):
    """
    Client for vault transaction history and bookkeeping operations.

    Supports:
    - GET vault transactions
    - GET vault net deposit
    - GET vault last rotation time
    - POST add deposit
    - POST add withdraw
    - POST add operation
    - POST add cashflow
    """

    def __init__(self, api_key: str | None = None) -> None:
        super().__init__(api_key=api_key)
        self.api_base_url = f"{settings.WAYFINDER_API_URL}"
        self._auth_client: AuthClient | None = AuthClient(api_key=api_key)

    # ===================== Read Endpoints =====================

    async def get_vault_transactions(
        self,
        *,
        wallet_address: str,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Fetch a paginated list of transactions for a given vault wallet and address.

        GET /api/v1/public/vaults/transactions/?wallet_address=...&limit=...&offset=...
        """
        url = f"{self.api_base_url}/public/vaults/transactions/"
        params = {
            "wallet_address": wallet_address,
            "limit": str(limit),
            "offset": str(offset),
        }
        response = await self._authed_request("GET", url, params=params)
        data = response.json()
        return data.get("data", data)

    async def get_vault_net_deposit(self, *, wallet_address: str) -> dict[str, Any]:
        """
        Fetch the net deposit (deposits - withdrawals) for a vault and address.

        GET /api/v1/public/vaults/net-deposit/?wallet_address=...
        """
        url = f"{self.api_base_url}/public/vaults/net-deposit/"
        params = {
            "wallet_address": wallet_address,
        }
        response = await self._authed_request("GET", url, params=params)
        data = response.json()
        return data.get("data", data)

    async def get_vault_latest_transactions(
        self, *, wallet_address: str
    ) -> dict[str, Any]:
        """
        Fetch the last rotation time for a vault and address.

        GET /api/v1/public/vaults/last-rotation-time/?wallet_address=...
        """
        url = f"{self.api_base_url}/public/vaults/latest-transactions/"
        params = {
            "wallet_address": wallet_address,
        }
        response = await self._authed_request("GET", url, params=params)
        data = response.json()
        return data.get("data", data)

    # ===================== Write Endpoints =====================

    async def add_vault_deposit(
        self,
        *,
        wallet_address: str,
        chain_id: int,
        token_address: str,
        token_amount: str | float,
        usd_value: str | float,
        data: dict[str, Any] | None = None,
        strategy_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Record a deposit for a vault.

        POST /api/v1/public/vaults/deposits/
        """
        url = f"{self.api_base_url}/public/vaults/deposits/"
        payload: dict[str, Any] = {
            "wallet_address": wallet_address,
            "chain_id": chain_id,
            "token_address": token_address,
            "token_amount": str(token_amount),
            "usd_value": str(usd_value),
            "data": data or {},
        }
        if strategy_name is not None:
            payload["strategy_name"] = strategy_name
        response = await self._authed_request("POST", url, json=payload)
        data_resp = response.json()
        return data_resp.get("data", data_resp)

    async def add_vault_withdraw(
        self,
        *,
        wallet_address: str,
        chain_id: int,
        token_address: str,
        token_amount: str | float,
        usd_value: str | float,
        data: dict[str, Any] | None = None,
        strategy_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Record a withdrawal for a vault.

        POST /api/v1/public/vaults/withdrawals/
        """
        url = f"{self.api_base_url}/public/vaults/withdrawals/"
        payload: dict[str, Any] = {
            "wallet_address": wallet_address,
            "chain_id": chain_id,
            "token_address": token_address,
            "token_amount": str(token_amount),
            "usd_value": str(usd_value),
            "data": data or {},
        }
        if strategy_name is not None:
            payload["strategy_name"] = strategy_name
        response = await self._authed_request("POST", url, json=payload)
        data_resp = response.json()
        return data_resp.get("data", data_resp)

    async def add_vault_operation(
        self,
        *,
        wallet_address: str,
        operation_data: dict[str, Any],
        usd_value: str | float,
        strategy_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Record a vault operation (e.g., swaps, rebalances) for bookkeeping.

        POST /api/v1/public/vaults/operations/
        """
        url = f"{self.api_base_url}/public/vaults/operations/"
        payload: dict[str, Any] = {
            "wallet_address": wallet_address,
            "operation_data": operation_data,
            "usd_value": str(usd_value),
        }
        if strategy_name is not None:
            payload["strategy_name"] = strategy_name
        response = await self._authed_request("POST", url, json=payload)
        data_resp = response.json()
        return data_resp.get("data", data_resp)

    async def add_vault_cashflow(
        self,
        *,
        wallet_address: str,
        block_timestamp: int,
        token_addr: str,
        amount: str | int | float,
        description: str,
        strategy_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Record a cashflow for a vault (interest, funding, reward, or fee).

        POST /api/v1/public/vaults/cashflows/

        Args:
            wallet_address: Vault wallet address
            block_timestamp: Block timestamp (Unix timestamp)
            token_addr: Token contract address
            amount: Cashflow amount (in token units)
            description: Cashflow type - must be one of: "interest", "funding", "reward", "fee", "lend", "unlend", "borrow"
            strategy_name: Optional strategy name

        Returns:
            Dict containing the cashflow record or error details
        """
        valid_descriptions = [
            "interest",
            "funding",
            "reward",
            "fee",
            "lend",
            "unlend",
            "borrow",
        ]
        if description not in valid_descriptions:
            raise ValueError(
                f"Invalid description '{description}'. Must be one of: {valid_descriptions}"
            )

        url = f"{self.api_base_url}/public/vaults/cashflows/"
        payload: dict[str, Any] = {
            "wallet_address": wallet_address,
            "block_timestamp": block_timestamp,
            "token_addr": token_addr,
            "amount": str(amount),
            "description": description,
        }
        if strategy_name is not None:
            payload["strategy_name"] = strategy_name
        response = await self._authed_request("POST", url, json=payload)
        data_resp = response.json()
        return data_resp.get("data", data_resp)
