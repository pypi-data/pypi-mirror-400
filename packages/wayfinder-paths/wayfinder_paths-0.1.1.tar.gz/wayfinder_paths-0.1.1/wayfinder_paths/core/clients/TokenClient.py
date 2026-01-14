"""
Token Adapter
Handles token information, prices, and parsing
"""

from typing import Any

from wayfinder_paths.core.clients.AuthClient import AuthClient
from wayfinder_paths.core.clients.WayfinderClient import WayfinderClient
from wayfinder_paths.core.settings import settings


class TokenClient(WayfinderClient):
    """Adapter for token-related operations"""

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)
        self.api_base_url = f"{self.api_base_url}/tokens"
        self._auth_client: AuthClient | None = AuthClient(api_key=api_key)

    # ============== Public (No-Auth) Endpoints ==============

    async def get_token_details(
        self, token_id: str, force_refresh: bool = False
    ) -> dict[str, Any]:
        """
        Get token data including price from the token-details endpoint

        Args:
            token_id: Token identifier or address

        Returns:
            Full token data including price information
        """
        url = f"{settings.WAYFINDER_API_URL}/public/tokens/detail/"
        params = {
            "query": token_id,
            "get_chart": "false",
            "force_refresh": str(force_refresh),
        }
        # Public endpoint: do not pass auth headers
        response = await self._request("GET", url, params=params, headers={})
        response.raise_for_status()
        data = response.json()
        return data.get("data", data)

    async def get_gas_token(self, chain_code: str) -> dict[str, Any]:
        """
        Fetch the native gas token for a given chain code via public endpoint.
        Example: GET /api/v1/public/tokens/gas/?chain_code=base
        """
        url = f"{settings.WAYFINDER_API_URL}/public/tokens/gas/"
        params = {"chain_code": chain_code}
        # Public endpoint: do not pass auth headers
        response = await self._request("GET", url, params=params, headers={})
        response.raise_for_status()
        data = response.json()
        return data.get("data", data)

    async def is_native_token(
        self, token_address: str, chain_id: int
    ) -> dict[str, Any]:
        """
        Determine if a token address corresponds to the native gas token on a chain.
        Returns the API payload (usually includes an `is_native` boolean).
        """
        url = f"{settings.WAYFINDER_API_URL}/public/tokens/is-native/"
        params = {"token_address": token_address, "chain_id": str(chain_id)}
        # Public endpoint: do not pass auth headers
        response = await self._request("GET", url, params=params, headers={})
        response.raise_for_status()
        data = response.json()
        return data.get("data", data)
