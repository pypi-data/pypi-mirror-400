"""
SDK Usage Examples

Demonstrates how to use the SDK with custom client implementations.
Use cases: mocks for testing, caching layers, alternative endpoints, rate limiting.
"""

from typing import Any

from wayfinder_paths.core.clients.ClientManager import ClientManager
from wayfinder_paths.core.clients.TokenClient import TokenClient


class CachedTokenClient:
    """Token client with in-memory caching"""

    def __init__(self):
        self._cache: dict[str, dict[str, Any]] = {}
        self._default_client = TokenClient()

    async def get_token_details(
        self, token_id: str, force_refresh: bool = False
    ) -> dict[str, Any]:
        cache_key = f"token_{token_id}"
        if not force_refresh and cache_key in self._cache:
            return self._cache[cache_key]
        data = await self._default_client.get_token_details(token_id, force_refresh)
        self._cache[cache_key] = data
        return data

    async def get_gas_token(self, chain_code: str) -> dict[str, Any]:
        return await self._default_client.get_gas_token(chain_code)

    async def is_native_token(
        self, token_address: str, chain_id: int
    ) -> dict[str, Any]:
        return await self._default_client.is_native_token(token_address, chain_id)


class MockHyperlendClient:
    """Mock client for testing"""

    async def get_stable_markets(
        self,
        *,
        chain_id: int,
        required_underlying_tokens: float | None = None,
        buffer_bps: int | None = None,
        min_buffer_tokens: float | None = None,
        is_stable_symbol: bool | None = None,
    ) -> dict[str, Any]:
        return {
            "markets": [
                {
                    "chain_id": chain_id,
                    "token_address": "0xMockToken",
                    "symbol": "USDC",
                    "lend_rate": 0.05,
                    "available_liquidity": 1000000.0,
                }
            ]
        }

    async def get_assets_view(
        self,
        *,
        chain_id: int,
        user_address: str,
    ) -> dict[str, Any]:
        return {
            "user_address": user_address,
            "chain_id": chain_id,
            "assets": [],
        }

    async def get_market_entry(
        self,
        *,
        chain_id: int,
        token_address: str,
    ) -> dict[str, Any]:
        return {
            "chain_id": chain_id,
            "token_address": token_address,
            "market_data": {},
        }

    async def get_lend_rate_history(
        self,
        *,
        chain_id: int,
        token_address: str,
        lookback_hours: int,
    ) -> dict[str, Any]:
        return {
            "chain_id": chain_id,
            "token_address": token_address,
            "rates": [],
        }


async def example_sdk_usage():
    """Direct client injection - inject only what you customize"""

    custom_token_client = CachedTokenClient()
    custom_hyperlend_client = MockHyperlendClient()

    ClientManager(
        clients={
            "token": custom_token_client,
            "hyperlend": custom_hyperlend_client,
        },
        skip_auth=True,
    )
    pass
