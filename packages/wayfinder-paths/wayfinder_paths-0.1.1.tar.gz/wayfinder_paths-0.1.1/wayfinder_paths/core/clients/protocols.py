"""
Protocol definitions for API clients.

These protocols define the interface that all client implementations must satisfy.
When used as an SDK, users can provide custom implementations that match these protocols.

Note: AuthClient is excluded as SDK users handle their own authentication.
"""

from typing import Any, Protocol


class TokenClientProtocol(Protocol):
    """Protocol for token-related operations"""

    async def get_token_details(
        self, token_id: str, force_refresh: bool = False
    ) -> dict[str, Any]:
        """Get token data including price from the token-details endpoint"""
        ...

    async def get_gas_token(self, chain_code: str) -> dict[str, Any]:
        """Fetch the native gas token for a given chain code"""
        ...

    async def is_native_token(
        self, token_address: str, chain_id: int
    ) -> dict[str, Any]:
        """Determine if a token address corresponds to the native gas token on a chain"""
        ...


class HyperlendClientProtocol(Protocol):
    """Protocol for Hyperlend-related operations"""

    async def get_stable_markets(
        self,
        *,
        chain_id: int,
        required_underlying_tokens: float | None = None,
        buffer_bps: int | None = None,
        min_buffer_tokens: float | None = None,
        is_stable_symbol: bool | None = None,
    ) -> dict[str, Any]:
        """Fetch stable markets from Hyperlend"""
        ...

    async def get_assets_view(
        self,
        *,
        chain_id: int,
        user_address: str,
    ) -> dict[str, Any]:
        """Fetch assets view for a user address from Hyperlend"""
        ...

    async def get_market_entry(
        self,
        *,
        chain_id: int,
        token_address: str,
    ) -> dict[str, Any]:
        """Fetch market entry from Hyperlend"""
        ...

    async def get_lend_rate_history(
        self,
        *,
        chain_id: int,
        token_address: str,
        lookback_hours: int,
    ) -> dict[str, Any]:
        """Fetch lend rate history from Hyperlend"""
        ...


class LedgerClientProtocol(Protocol):
    """Protocol for vault transaction history and bookkeeping operations"""

    async def get_vault_transactions(
        self,
        *,
        wallet_address: str,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Fetch a paginated list of transactions for a given vault wallet"""
        ...

    async def get_vault_net_deposit(self, *, wallet_address: str) -> dict[str, Any]:
        """Fetch the net deposit (deposits - withdrawals) for a vault"""
        ...

    async def get_vault_latest_transactions(
        self, *, wallet_address: str
    ) -> dict[str, Any]:
        """Fetch the latest transactions for a vault"""
        ...

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
        """Record a deposit for a vault"""
        ...

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
        """Record a withdrawal for a vault"""
        ...

    async def add_vault_operation(
        self,
        *,
        wallet_address: str,
        operation_data: dict[str, Any],
        usd_value: str | float,
        strategy_name: str | None = None,
    ) -> dict[str, Any]:
        """Record a vault operation (e.g., swaps, rebalances)"""
        ...

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
        """Record a cashflow for a vault (interest, funding, reward, or fee)"""
        ...


class WalletClientProtocol(Protocol):
    """Protocol for wallet-related operations"""

    async def get_token_balance_for_wallet(
        self,
        *,
        token_id: str,
        wallet_address: str,
        human_readable: bool = True,
    ) -> dict[str, Any]:
        """Fetch a single token balance for an explicit wallet address"""
        ...

    async def get_pool_balance_for_wallet(
        self,
        *,
        pool_address: str,
        chain_id: int,
        user_address: str,
        human_readable: bool = True,
    ) -> dict[str, Any]:
        """Fetch a wallet's LP/share balance for a given pool address and chain"""
        ...

    async def get_all_enriched_token_balances_for_wallet(
        self,
        *,
        wallet_address: str,
        enrich: bool = True,
        from_cache: bool = False,
        add_llama: bool = True,
    ) -> dict[str, Any]:
        """Fetch all token balances for a wallet with enrichment"""
        ...


class TransactionClientProtocol(Protocol):
    """Protocol for transaction operations"""

    async def build_send(
        self,
        from_address: str,
        to_address: str,
        token_address: str,
        amount: float,
        chain_id: int,
    ) -> dict[str, Any]:
        """Build a send transaction payload for EVM tokens/native transfers"""
        ...


class PoolClientProtocol(Protocol):
    """Protocol for pool-related read operations"""

    async def get_pools_by_ids(
        self,
        *,
        pool_ids: str,
        merge_external: bool | None = None,
    ) -> dict[str, Any]:
        """Fetch pools by comma-separated pool ids"""
        ...

    async def get_all_pools(
        self, *, merge_external: bool | None = None
    ) -> dict[str, Any]:
        """Fetch all pools"""
        ...

    async def get_combined_pool_reports(self) -> dict[str, Any]:
        """Fetch combined pool reports"""
        ...

    async def get_llama_matches(self) -> dict[str, Any]:
        """Fetch Llama matches for pools"""
        ...

    async def get_llama_reports(self, *, identifiers: str) -> dict[str, Any]:
        """Fetch Llama reports using identifiers"""
        ...


class BRAPClientProtocol(Protocol):
    """Protocol for BRAP (Bridge/Router/Adapter Protocol) quote operations"""

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
        """Get a quote for a bridge/swap operation"""
        ...


class SimulationClientProtocol(Protocol):
    """Protocol for blockchain transaction simulations"""

    async def simulate_send(
        self,
        from_address: str,
        to_address: str,
        token_address: str,
        amount: str,
        chain_id: int,
        initial_balances: dict[str, str],
    ) -> dict[str, Any]:
        """Simulate sending native ETH or ERC20 tokens"""
        ...

    async def simulate_approve(
        self,
        from_address: str,
        to_address: str,
        token_address: str,
        amount: str,
        chain_id: int,
        initial_balances: dict[str, str],
        clear_approval_first: bool = False,
    ) -> dict[str, Any]:
        """Simulate ERC20 token approval"""
        ...

    async def simulate_swap(
        self,
        from_token_address: str,
        to_token_address: str,
        from_chain_id: int,
        to_chain_id: int,
        amount: str,
        from_address: str,
        slippage: float,
        initial_balances: dict[str, str],
    ) -> dict[str, Any]:
        """Simulate token swap operation"""
        ...
