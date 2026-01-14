from typing import Any

from wayfinder_paths.core.adapters.BaseAdapter import BaseAdapter
from wayfinder_paths.core.clients.TokenClient import TokenClient


class TokenAdapter(BaseAdapter):
    """
    Token adapter that wraps the _get_token_via_api method for fetching token data
    via HeadlessAPIViewSet endpoints. Supports both address and token_id lookups.
    """

    adapter_type: str = "TOKEN"

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        token_client: TokenClient | None = None,
    ):
        super().__init__("token_adapter", config)
        self.token_client = token_client or TokenClient()

    async def get_token(self, query: str) -> tuple[bool, Any]:
        """
        Get token data by address using the token-details endpoint.

        Args:
            address: Token contract address

        Returns:
            Tuple of (success, data) where data is the token information or error message
        """
        try:
            data = await self.token_client.get_token_details(query)
            if not data:
                return (False, f"No token found for: {query}")
            return (True, data)
        except Exception as e:
            self.logger.error(f"Error getting token by query {query}: {e}")
            return (False, str(e))

    async def get_token_price(self, token_id: str) -> tuple[bool, Any]:
        """
        Get token price by token ID or address using the token-details endpoint.

        Args:
            token_id: Token identifier or address

        Returns:
            Tuple of (success, data) where data is the price information or error message
        """
        try:
            data = await self.token_client.get_token_details(token_id)
            if not data:
                return (False, f"No token found for: {token_id}")

            # Extract just the price information
            price_data = {
                "current_price": data.get("current_price", 0.0),
                "price_change_24h": data.get("price_change_24h", 0.0),
                "price_change_percentage_24h": data.get(
                    "price_change_percentage_24h", 0.0
                ),
                "market_cap": data.get("market_cap", 0),
                "total_volume": data.get("total_volume", 0),
                "symbol": data.get("symbol", ""),
                "name": data.get("name", ""),
                "address": data.get("address", ""),
            }
            return (True, price_data)
        except Exception as e:
            self.logger.error(f"Error getting token price for {token_id}: {e}")
            return (False, str(e))

    async def get_gas_token(self, chain_code: str) -> tuple[bool, Any]:
        """
        Get gas token for a given chain code.

        Args:
            chain_code: Chain code (e.g., "base", "ethereum")

        Returns:
            Tuple of (success, data) where data is the gas token information or error message
        """
        try:
            data = await self.token_client.get_gas_token(chain_code)
            if not data:
                return (False, f"No gas token found for chain: {chain_code}")
            return (True, data)
        except Exception as e:
            self.logger.error(f"Error getting gas token for chain {chain_code}: {e}")
            return (False, str(e))
