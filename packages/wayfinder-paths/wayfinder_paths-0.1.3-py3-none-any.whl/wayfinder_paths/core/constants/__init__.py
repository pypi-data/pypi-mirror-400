"""Constants package for wayfinder-paths.

This package contains all constants used across the system, organized by category:
- base: Fundamental constants (addresses, chain mappings, gas defaults)
- erc20_abi: ERC20 token ABI definitions for smart contract interactions
"""

from .base import (
    CHAIN_CODE_TO_ID,
    DEFAULT_GAS_ESTIMATE_FALLBACK,
    DEFAULT_NATIVE_GAS_UNITS,
    DEFAULT_SLIPPAGE,
    GAS_BUFFER_MULTIPLIER,
    ONE_GWEI,
    ZERO_ADDRESS,
)

__all__ = [
    "ZERO_ADDRESS",
    "CHAIN_CODE_TO_ID",
    "DEFAULT_NATIVE_GAS_UNITS",
    "DEFAULT_GAS_ESTIMATE_FALLBACK",
    "GAS_BUFFER_MULTIPLIER",
    "ONE_GWEI",
    "DEFAULT_SLIPPAGE",
]
