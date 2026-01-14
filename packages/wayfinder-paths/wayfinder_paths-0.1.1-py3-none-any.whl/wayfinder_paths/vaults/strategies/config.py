"""
Configuration for community strategies
Each strategy can define its own configuration parameters
"""

from typing import Any

# Funding Rate Strategy Configuration
FUNDING_RATE_CONFIG = {
    "min_deposit": 30,  # USDC
    "lookback_days": 90,
    "confidence": 0.9999,
    "min_open_interest": 50_000,
    "min_daily_volume": 100_000,
    "max_leverage": 3,
    "liquidation_threshold": 0.75,
    "rebalance_threshold": 0.05,
    "hyperliquid_system_address": "0x2Df1c51E09aECF9cacB7bc98cB1742757f163dF7",
    "supported_chains": ["arbitrum"],
}


# Stablecoin Yield Strategy Configuration
STABLECOIN_YIELD_CONFIG = {
    "min_deposit": 50,  # USDC
    "min_tvl": 1_000_000,  # $1M minimum TVL for safety
    "min_apy": 0.01,  # 1% minimum APY
    "rebalance_days": 7,  # Days until rebalance is profitable
    "search_depth": 10,  # Number of pools to evaluate
    "gas_buffer": 0.001,  # ETH for gas
    "supported_chains": ["base", "arbitrum"],
    "supported_tokens": ["USDC", "DAI", "USDT"],
    "excluded_protocols": [],  # Protocols to avoid
}


# Moonwell wstETH Loop Strategy Configuration (example for advanced strategies)
MOONWELL_LOOP_CONFIG = {
    "min_deposit": 200,  # USDC
    "max_loops": 30,
    "leverage_limit": 10,
    "contracts": {
        "m_usdc": "0xedc817a28e8b93b03976fbd4a3ddbc9f7d176c22",
        "m_weth": "0x628ff693426583D9a7FB391E54366292F509D457",
        "m_wsteth": "0x627fe393bc6edda28e99ae648fd6ff362514304b",
        "reward_distributor": "0xe9005b078701e2a0948d2eac43010d35870ad9d2",
        "comptroller": "0xfbb21d0380bee3312b33c4353c8936a0f13ef26c",
    },
    "supported_chains": ["base"],
}


# Global adapter configurations
ADAPTER_CONFIGS = {
    "hyperliquid": {
        "api_url": "https://api.hyperliquid.xyz",
        "testnet_url": "https://api.hyperliquid-testnet.xyz",
        "rate_limit": 10,  # requests per second
        "timeout": 30,  # seconds
        "slippage": 0.05,  # 5% default slippage for market orders
    },
    "enso": {
        "router_address": "0xF75584eF6673aD213a685a1B58Cc0330B8eA22Cf",
        "supported_chains": ["ethereum", "base", "arbitrum", "polygon"],
    },
    "moonwell": {
        "supported_chains": ["base"],
        "protocol_fee": 0.001,  # 0.1%
    },
}


def get_strategy_config(strategy_name: str) -> dict[str, Any]:
    """Get configuration for a specific strategy"""
    configs = {
        "funding_rate": FUNDING_RATE_CONFIG,
        "stablecoin_yield": STABLECOIN_YIELD_CONFIG,
        "moonwell_loop": MOONWELL_LOOP_CONFIG,
    }
    return configs.get(strategy_name.lower(), {})


def get_adapter_config(adapter_name: str) -> dict[str, Any]:
    """Get configuration for a specific adapter"""
    return ADAPTER_CONFIGS.get(adapter_name.lower(), {})
