"""
Pool Client
Provides read-only access to pool metadata and analytics via public endpoints.
"""

from typing import Any

from wayfinder_paths.core.clients.AuthClient import AuthClient
from wayfinder_paths.core.clients.WayfinderClient import WayfinderClient
from wayfinder_paths.core.settings import settings


class PoolClient(WayfinderClient):
    """Client for pool-related read operations"""

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)
        self.api_base_url = f"{settings.WAYFINDER_API_URL}"
        self._auth_client: AuthClient | None = AuthClient(api_key=api_key)

    async def get_pools_by_ids(
        self,
        *,
        pool_ids: str,
        merge_external: bool | None = None,
    ) -> dict[str, Any]:
        """
        Fetch pools by comma-separated pool ids.

        Example:
        GET /api/v1/public/pools/?pool_ids=a,b&merge_external=false
        """
        url = f"{self.api_base_url}/public/pools/"
        params: dict[str, Any] = {"pool_ids": pool_ids}
        if merge_external is not None:
            params["merge_external"] = "true" if merge_external else "false"
        response = await self._request("GET", url, params=params, headers={})
        response.raise_for_status()
        data = response.json()
        return data.get("data", data)

    async def get_all_pools(
        self, *, merge_external: bool | None = None
    ) -> dict[str, Any]:
        """
        Fetch all pools.

        Example:
        GET /api/v1/public/pools/?merge_external=false
        """
        url = f"{self.api_base_url}/public/pools/"
        params: dict[str, Any] = {}
        if merge_external is not None:
            params["merge_external"] = "true" if merge_external else "false"
        response = await self._request("GET", url, params=params, headers={})
        response.raise_for_status()
        data = response.json()
        return data.get("data", data)

    async def get_combined_pool_reports(self) -> dict[str, Any]:
        """
        Fetch combined pool reports.

        GET /api/v1/public/pools/combined/
        """
        url = f"{self.api_base_url}/public/pools/combined/"
        response = await self._request("GET", url, headers={})
        response.raise_for_status()
        data = response.json()
        return data.get("data", data)

    async def get_llama_matches(self) -> dict[str, Any]:
        """
        Fetch Llama matches for pools.

        GET /api/v1/public/pools/llama/matches/
        """
        url = f"{self.api_base_url}/public/pools/llama/matches/"
        response = await self._request("GET", url, headers={})
        response.raise_for_status()
        data = response.json()
        return data.get("data", data)

    async def get_llama_reports(self, *, identifiers: str) -> dict[str, Any]:
        """
        Fetch Llama reports using identifiers (token ids, address_network, or pool ids).

        Example:
        GET /api/v1/public/pools/llama/reports/?identifiers=pool-1,usd-coin
        """
        url = f"{self.api_base_url}/public/pools/llama/reports/"
        params = {"identifiers": identifiers}
        response = await self._request("GET", url, params=params, headers={})
        response.raise_for_status()
        data = response.json()
        return data.get("data", data)
