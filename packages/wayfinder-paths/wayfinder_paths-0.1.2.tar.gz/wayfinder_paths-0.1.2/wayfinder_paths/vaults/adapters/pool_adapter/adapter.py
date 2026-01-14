from typing import Any

from wayfinder_paths.core.adapters.BaseAdapter import BaseAdapter
from wayfinder_paths.core.clients.PoolClient import PoolClient


class PoolAdapter(BaseAdapter):
    """
    Pool adapter for DeFi pool data and analytics operations.

    Provides high-level operations for:
    - Fetching pool information and metadata
    - Getting pool analytics and reports
    - Accessing Llama protocol data
    - Pool discovery and filtering
    """

    adapter_type: str = "POOL"

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        pool_client: PoolClient | None = None,
    ):
        super().__init__("pool_adapter", config)
        self.pool_client = pool_client or PoolClient()

    async def get_pools_by_ids(
        self, pool_ids: list[str], merge_external: bool | None = None
    ) -> tuple[bool, Any]:
        """
        Get pool information by pool IDs.

        Args:
            pool_ids: List of pool identifiers
            merge_external: Whether to merge external data

        Returns:
            Tuple of (success, data) where data is pool information or error message
        """
        try:
            pool_ids_str = ",".join(pool_ids)
            data = await self.pool_client.get_pools_by_ids(
                pool_ids=pool_ids_str, merge_external=merge_external
            )
            return (True, data)
        except Exception as e:
            self.logger.error(f"Error fetching pools by IDs: {e}")
            return (False, str(e))

    async def get_all_pools(
        self, merge_external: bool | None = None
    ) -> tuple[bool, Any]:
        """
        Get all available pools.

        Args:
            merge_external: Whether to merge external data

        Returns:
            Tuple of (success, data) where data is all pools or error message
        """
        try:
            data = await self.pool_client.get_all_pools(merge_external=merge_external)
            return (True, data)
        except Exception as e:
            self.logger.error(f"Error fetching all pools: {e}")
            return (False, str(e))

    async def get_combined_pool_reports(self) -> tuple[bool, Any]:
        """
        Get combined pool reports with analytics.

        Returns:
            Tuple of (success, data) where data is combined reports or error message
        """
        try:
            data = await self.pool_client.get_combined_pool_reports()
            return (True, data)
        except Exception as e:
            self.logger.error(f"Error fetching combined pool reports: {e}")
            return (False, str(e))

    async def get_llama_matches(self) -> tuple[bool, Any]:
        """
        Get Llama protocol matches for pools.

        Returns:
            Tuple of (success, data) where data is Llama matches or error message
        """
        try:
            data = await self.pool_client.get_llama_matches()
            return (True, data)
        except Exception as e:
            self.logger.error(f"Error fetching Llama matches: {e}")
            return (False, str(e))

    async def get_llama_reports(self, identifiers: list[str]) -> tuple[bool, Any]:
        """
        Get Llama reports for specific identifiers.

        Args:
            identifiers: List of identifiers (token IDs, addresses, pool IDs)

        Returns:
            Tuple of (success, data) where data is Llama reports or error message
        """
        try:
            identifiers_str = ",".join(identifiers)
            data = await self.pool_client.get_llama_reports(identifiers=identifiers_str)
            return (True, data)
        except Exception as e:
            self.logger.error(f"Error fetching Llama reports: {e}")
            return (False, str(e))

    async def find_high_yield_pools(
        self,
        min_apy: float = 0.01,
        min_tvl: float = 1000000,
        stablecoin_only: bool = True,
        network_codes: list[str] | None = None,
    ) -> tuple[bool, Any]:
        """
        Find high-yield pools based on criteria.

        Args:
            min_apy: Minimum APY threshold (as decimal, e.g., 0.01 for 1%)
            min_tvl: Minimum TVL threshold in USD
            stablecoin_only: Whether to filter for stablecoin pools only
            network_codes: List of network codes to filter by

        Returns:
            Tuple of (success, data) where data is filtered pools or error message
        """
        try:
            # Get Llama matches for yield data
            success, llama_data = await self.get_llama_matches()
            if not success:
                return (False, f"Failed to fetch Llama data: {llama_data}")

            matches = llama_data.get("matches", [])
            filtered_pools = []

            for pool in matches:
                # Apply filters
                if stablecoin_only and not pool.get("llama_stablecoin", False):
                    continue

                if pool.get("llama_tvl_usd", 0) < min_tvl:
                    continue

                if (
                    pool.get("llama_apy_pct", 0) < min_apy * 100
                ):  # Convert to percentage
                    continue

                if network_codes and pool.get("network", "").lower() not in [
                    nc.lower() for nc in network_codes
                ]:
                    continue

                filtered_pools.append(pool)

            # Sort by APY descending
            filtered_pools.sort(key=lambda x: x.get("llama_apy_pct", 0), reverse=True)

            return (
                True,
                {
                    "pools": filtered_pools,
                    "total_found": len(filtered_pools),
                    "filters_applied": {
                        "min_apy": min_apy,
                        "min_tvl": min_tvl,
                        "stablecoin_only": stablecoin_only,
                        "network_codes": network_codes,
                    },
                },
            )
        except Exception as e:
            self.logger.error(f"Error finding high yield pools: {e}")
            return (False, str(e))

    async def get_pool_analytics(self, pool_ids: list[str]) -> tuple[bool, Any]:
        """
        Get comprehensive analytics for specific pools.

        Args:
            pool_ids: List of pool identifiers

        Returns:
            Tuple of (success, data) where data is pool analytics or error message
        """
        try:
            # Get pool data
            success, pool_data = await self.get_pools_by_ids(pool_ids)
            if not success:
                return (False, f"Failed to fetch pool data: {pool_data}")

            # Get Llama reports
            success, llama_data = await self.get_llama_reports(pool_ids)
            if not success:
                self.logger.warning(f"Failed to fetch Llama data: {llama_data}")
                llama_data = {}

            pools = pool_data.get("pools", [])
            llama_reports = llama_data

            # Combine data
            analytics = []
            for pool in pools:
                pool_id = pool.get("id")
                llama_report = llama_reports.get(pool_id.lower()) if pool_id else None

                analytics.append(
                    {
                        "pool": pool,
                        "llama_data": llama_report,
                        "combined_apy": (
                            llama_report.get("llama_combined_apy_pct", 0) / 100
                            if llama_report
                            and llama_report.get("llama_combined_apy_pct") is not None
                            else pool.get("apy", 0)
                        ),
                        "tvl_usd": (
                            llama_report.get("llama_tvl_usd", 0)
                            if llama_report and llama_report.get("llama_tvl_usd")
                            else pool.get("tvl", 0)
                        ),
                    }
                )

            return (True, {"analytics": analytics, "total_pools": len(analytics)})
        except Exception as e:
            self.logger.error(f"Error getting pool analytics: {e}")
            return (False, str(e))

    async def search_pools(self, query: str, limit: int = 10) -> tuple[bool, Any]:
        """
        Search pools by name, symbol, or other criteria.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            Tuple of (success, data) where data is search results or error message
        """
        try:
            success, all_pools_data = await self.get_all_pools()
            if not success:
                return (False, f"Failed to fetch pools: {all_pools_data}")

            pools = all_pools_data.get("pools", [])
            query_lower = query.lower()

            # Simple text search
            matching_pools = []
            for pool in pools:
                name = pool.get("name", "").lower()
                symbol = pool.get("symbol", "").lower()
                description = pool.get("description", "").lower()

                if (
                    query_lower in name
                    or query_lower in symbol
                    or query_lower in description
                ):
                    matching_pools.append(pool)

            # Sort by relevance (exact matches first)
            matching_pools.sort(
                key=lambda x: (
                    query_lower not in x.get("name", "").lower(),
                    query_lower not in x.get("symbol", "").lower(),
                )
            )

            return (
                True,
                {
                    "pools": matching_pools[:limit],
                    "total_found": len(matching_pools),
                    "query": query,
                },
            )
        except Exception as e:
            self.logger.error(f"Error searching pools: {e}")
            return (False, str(e))
