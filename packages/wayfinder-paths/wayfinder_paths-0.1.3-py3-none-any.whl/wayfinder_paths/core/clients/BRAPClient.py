"""
BRAP (Bridge/Router/Adapter Protocol) Client
Provides access to quote operations via the public quote endpoint.
"""

import time
from typing import Any

from loguru import logger

from wayfinder_paths.core.clients.AuthClient import AuthClient
from wayfinder_paths.core.clients.WayfinderClient import WayfinderClient
from wayfinder_paths.core.settings import settings


class BRAPClient(WayfinderClient):
    """Client for BRAP quote operations"""

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)
        self.api_base_url = f"{settings.WAYFINDER_API_URL}"
        self._auth_client: AuthClient | None = AuthClient(api_key=api_key)

    async def get_quote(
        self,
        *,
        from_token_address: str,
        to_token_address: str,
        from_chain_id: int,
        to_chain_id: int,
        from_address: str,
        to_address: str,
        amount1: str,
        slippage: float | None = None,
        wayfinder_fee: float | None = None,
    ) -> dict[str, Any]:
        """
        Get a quote for a bridge/swap operation.

        Args:
            from_token_address: Source token contract address
            to_token_address: Destination token contract address
            from_chain_id: Source chain ID
            to_chain_id: Destination chain ID
            from_address: Source wallet address
            to_address: Destination wallet address
            amount1: Amount to swap (in smallest units)
            slippage: Maximum slippage tolerance (optional)
            wayfinder_fee: Wayfinder fee (optional)

        Returns:
            Quote data including routes, amounts, fees, etc.
        """
        logger.info(
            f"Getting BRAP quote: {from_token_address} -> {to_token_address} (chain {from_chain_id} -> {to_chain_id})"
        )
        logger.debug(
            f"Quote params: amount={amount1}, slippage={slippage}, wayfinder_fee={wayfinder_fee}"
        )
        start_time = time.time()

        url = f"{self.api_base_url}/public/quotes/"

        payload = {
            "from_token_address": from_token_address,
            "to_token_address": to_token_address,
            "from_chain_id": from_chain_id,
            "to_chain_id": to_chain_id,
            "from_address": from_address,
            "to_address": to_address,
            "amount1": amount1,
        }

        # Only add optional parameters if they're provided
        if slippage is not None:
            payload["slippage"] = slippage
        if wayfinder_fee is not None:
            payload["wayfinder_fee"] = wayfinder_fee

        try:
            response = await self._request("POST", url, json=payload, headers={})
            response.raise_for_status()
            data = response.json()
            elapsed = time.time() - start_time
            logger.info(f"BRAP quote request completed successfully in {elapsed:.2f}s")
            return data.get("data", data)
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"BRAP quote request failed after {elapsed:.2f}s: {e}")
            raise
