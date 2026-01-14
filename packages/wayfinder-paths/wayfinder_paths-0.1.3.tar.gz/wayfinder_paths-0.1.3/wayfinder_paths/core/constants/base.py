"""Base constants for adapters and strategies.

This module contains fundamental constants used across the wayfinder-paths system,
including address constants, chain mappings, and gas-related defaults.
"""

# Address constants
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# Chain code to EVM chain id mapping
CHAIN_CODE_TO_ID = {
    "base": 8453,
    "arbitrum": 42161,
    "arbitrum-one": 42161,
    "ethereum": 1,
    "mainnet": 1,
    "hyperevm": 999,
}

# Gas/defaults
DEFAULT_NATIVE_GAS_UNITS = 21000
DEFAULT_GAS_ESTIMATE_FALLBACK = 100000
GAS_BUFFER_MULTIPLIER = 1.1  # 10% buffer for native sends
ONE_GWEI = 1_000_000_000
DEFAULT_SLIPPAGE = 0.005
