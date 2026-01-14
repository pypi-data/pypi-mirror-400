"""
Wallet Client
Fetches wallet-related data such as aggregated balances for the authenticated user.
"""

from typing import Any

from wayfinder_paths.core.clients.AuthClient import AuthClient
from wayfinder_paths.core.clients.WayfinderClient import WayfinderClient
from wayfinder_paths.core.settings import settings


class WalletClient(WayfinderClient):
    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)
        self.api_base_url = f"{settings.WAYFINDER_API_URL}"
        self._auth_client = AuthClient(api_key=api_key)

    async def get_token_balance_for_wallet(
        self,
        *,
        token_id: str,
        wallet_address: str,
        human_readable: bool = True,
    ) -> dict[str, Any]:
        """
        Fetch a single token balance for an explicit wallet address.

        Mirrors POST /api/v1/public/balances/token/
        """
        url = f"{self.api_base_url}/public/balances/token/"
        payload = {
            "token_id": token_id,
            "wallet_address": wallet_address,
            "human_readable": human_readable,
        }
        response = await self._authed_request("POST", url, json=payload)
        data = response.json()
        return data.get("data", data)

    async def get_pool_balance_for_wallet(
        self,
        *,
        pool_address: str,
        chain_id: int,
        user_address: str,
        human_readable: bool = True,
    ) -> dict[str, Any]:
        """
        Fetch a wallet's LP/share balance for a given pool address and chain.

        Mirrors POST /api/v1/public/balances/pool/
        """
        url = f"{self.api_base_url}/public/balances/pool/"
        payload = {
            "pool_address": pool_address,
            "chain_id": chain_id,
            "user_address": user_address,
            "human_readable": human_readable,
        }
        response = await self._authed_request("POST", url, json=payload)
        data = response.json()
        return data.get("data", data)

    async def get_all_enriched_token_balances_for_wallet(
        self,
        *,
        wallet_address: str,
        enrich: bool = True,
        from_cache: bool = False,
        add_llama: bool = True,
    ) -> dict[str, Any]:
        """
        Fetch all token balances for a wallet with enrichment via the enriched endpoint.

        Mirrors POST /api/v1/public/balances/enriched/
        """
        url = f"{self.api_base_url}/public/balances/enriched/"
        payload = {
            "wallet_address": wallet_address,
            "enrich": enrich,
            "from_cache": from_cache,
            "add_llama": add_llama,
        }
        try:
            response = await self._authed_request("POST", url, json=payload)
            data = response.json()
            return data.get("data", data)
        except Exception:
            raise
