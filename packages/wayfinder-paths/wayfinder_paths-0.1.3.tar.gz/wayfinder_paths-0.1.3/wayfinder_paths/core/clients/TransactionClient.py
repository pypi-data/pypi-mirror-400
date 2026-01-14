"""
Transaction Client
Handles transaction building, gas estimation, and monitoring
"""

from typing import Any

from wayfinder_paths.core.clients.AuthClient import AuthClient
from wayfinder_paths.core.clients.WayfinderClient import WayfinderClient
from wayfinder_paths.core.settings import settings


class TransactionClient(WayfinderClient):
    """Client for transaction operations"""

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)
        self.api_base_url = f"{self.api_base_url}/transactions"
        self._auth_client: AuthClient | None = AuthClient(api_key=api_key)

    # ============== Protected (Auth Required) Endpoints ==============

    async def build_send(
        self,
        from_address: str,
        to_address: str,
        token_address: str,
        amount: float,
        chain_id: int,
    ) -> dict[str, Any]:
        """
        Build a send transaction payload for EVM tokens/native transfers.

        GET /api/v1/public/transactions/build-send/?from_address=...&to_address=...&token_address=...&amount=...&chain_id=...
        """
        url = f"{settings.WAYFINDER_API_URL}/public/transactions/build-send/"
        params = {
            "from_address": from_address,
            "to_address": to_address,
            "token_address": token_address,
            "amount": str(amount),
            "chain_id": str(chain_id),
        }
        response = await self._authed_request("GET", url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", data)
