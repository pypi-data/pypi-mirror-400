"""
EVM helper utilities for common blockchain operations.

This module provides reusable functions for EVM-related operations that are shared
across multiple adapters, extracted from evm_transaction_adapter.
"""

import os
from typing import Any

from loguru import logger
from web3 import AsyncHTTPProvider, AsyncWeb3

from wayfinder_paths.core.constants.base import CHAIN_CODE_TO_ID


def chain_code_to_chain_id(chain_code: str | None) -> int | None:
    """
    Convert chain code to chain ID.

    Args:
        chain_code: Chain code string (e.g., "ethereum", "base")

    Returns:
        Chain ID as integer, or None if not found
    """
    if not chain_code:
        return None
    return CHAIN_CODE_TO_ID.get(chain_code.lower())


def resolve_chain_id(token_info: dict[str, Any], logger_instance=None) -> int | None:
    """
    Extract chain ID from token_info dictionary.

    Args:
        token_info: Dictionary containing token information with 'chain' key
        logger_instance: Optional logger instance for debug messages

    Returns:
        Chain ID as integer, or None if not found
    """
    log = logger_instance or logger
    chain_meta = token_info.get("chain") or {}
    chain_id = chain_meta.get("chain_id")
    try:
        if chain_id is not None:
            return int(chain_id)
    except (ValueError, TypeError):
        log.debug("Invalid chain_id in token_info.chain_id: %s", chain_id)
    return chain_code_to_chain_id(chain_meta.get("code"))


def resolve_rpc_url(
    chain_id: int | None,
    config: dict[str, Any],
    explicit_rpc_url: str | None = None,
) -> str:
    """
    Resolve RPC URL from config or environment variables.

    Args:
        chain_id: Chain ID to look up RPC URL for
        config: Configuration dictionary
        explicit_rpc_url: Explicitly provided RPC URL (takes precedence)

    Returns:
        RPC URL string

    Raises:
        ValueError: If RPC URL cannot be resolved
    """
    if explicit_rpc_url:
        return explicit_rpc_url
    strategy_cfg = config.get("strategy") or {}
    mapping = strategy_cfg.get("rpc_urls") if isinstance(strategy_cfg, dict) else None
    if chain_id is not None and isinstance(mapping, dict):
        by_int = mapping.get(chain_id)
        if by_int:
            return str(by_int)
        by_str = mapping.get(str(chain_id))
        if by_str:
            return str(by_str)
    env_rpc = os.getenv("RPC_URL")
    if env_rpc:
        return env_rpc
    raise ValueError("RPC URL not provided. Set strategy.rpc_urls or env RPC_URL.")


async def get_next_nonce(
    from_address: str, rpc_url: str, use_latest: bool = False
) -> int:
    """
    Get the next nonce for the given address.

    Args:
        from_address: Address to get nonce for
        rpc_url: RPC URL to connect to
        use_latest: If True, use 'latest' block instead of 'pending'

    Returns:
        Next nonce as integer
    """
    w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
    try:
        if use_latest:
            return await w3.eth.get_transaction_count(from_address, "latest")
        return await w3.eth.get_transaction_count(from_address)
    finally:
        try:
            await w3.provider.session.close()
        except Exception:
            pass


def resolve_private_key_for_from_address(
    from_address: str, config: dict[str, Any]
) -> str | None:
    """
    Resolve private key for the given address from config or environment.

    Args:
        from_address: Address to resolve private key for
        config: Configuration dictionary containing wallet information

    Returns:
        Private key string, or None if not found
    """
    from_addr_norm = (from_address or "").lower()
    main_wallet = config.get("main_wallet")
    vault_wallet = config.get("vault_wallet")

    main_pk = None
    vault_pk = None
    try:
        if isinstance(main_wallet, dict):
            main_pk = main_wallet.get("private_key") or main_wallet.get(
                "private_key_hex"
            )
        if isinstance(vault_wallet, dict):
            vault_pk = vault_wallet.get("private_key") or vault_wallet.get(
                "private_key_hex"
            )
    except (AttributeError, TypeError) as e:
        logger.debug("Error resolving private keys from wallet config: %s", e)

    main_addr = None
    vault_addr = None
    try:
        main_addr = (main_wallet or {}).get("address") or (
            (main_wallet or {}).get("evm") or {}
        ).get("address")
        vault_addr = (vault_wallet or {}).get("address") or (
            (vault_wallet or {}).get("evm") or {}
        ).get("address")
    except (AttributeError, TypeError) as e:
        logger.debug("Error resolving addresses from wallet config: %s", e)

    if main_addr and from_addr_norm == (main_addr or "").lower():
        return main_pk or os.getenv("PRIVATE_KEY")
    if vault_addr and from_addr_norm == (vault_addr or "").lower():
        return vault_pk or os.getenv("PRIVATE_KEY_VAULT") or os.getenv("PRIVATE_KEY")

    # Fallback to environment variables
    return os.getenv("PRIVATE_KEY_VAULT") or os.getenv("PRIVATE_KEY")
