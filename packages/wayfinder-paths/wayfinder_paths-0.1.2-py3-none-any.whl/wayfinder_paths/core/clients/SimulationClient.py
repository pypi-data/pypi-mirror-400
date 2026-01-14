"""
Simulation Client
Handles blockchain transaction simulations via Gorlami/Tenderly
"""

import time
from typing import Any

from loguru import logger

from wayfinder_paths.core.clients.WayfinderClient import WayfinderClient


class SimulationClient(WayfinderClient):
    """Client for blockchain transaction simulations"""

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)

    async def simulate_send(
        self,
        from_address: str,
        to_address: str,
        token_address: str,
        amount: str,
        chain_id: int,
        initial_balances: dict[str, str],
    ) -> dict[str, Any]:
        """
        Simulate sending native ETH or ERC20 tokens.

        Args:
            from_address: Source wallet address
            to_address: Destination wallet address
            token_address: Token contract address (use 0x0 for native ETH)
            amount: Amount to send
            chain_id: Blockchain chain ID
            initial_balances: Initial token balances for simulation

        Returns:
            Simulation result data
        """
        logger.info(
            f"Simulating send: {amount} from {from_address} to {to_address} (chain {chain_id})"
        )
        start_time = time.time()

        url = f"{self.api_base_url}public/simulate/send/"

        payload = {
            "from_address": from_address,
            "to_address": to_address,
            "token_address": token_address,
            "amount": amount,
            "chain_id": chain_id,
            "initial_balances": initial_balances,
        }

        try:
            response = await self._request("POST", url, json=payload, headers={})
            response.raise_for_status()
            data = response.json()
            elapsed = time.time() - start_time
            logger.info(f"Simulation request completed successfully in {elapsed:.2f}s")
            return data.get("data", data)
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Simulation request failed after {elapsed:.2f}s: {e}")
            raise

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
        """
        Simulate ERC20 token approval.

        Args:
            from_address: Address approving the tokens
            to_address: Address being approved to spend tokens
            token_address: ERC20 token contract address
            amount: Amount to approve
            chain_id: Blockchain chain ID
            initial_balances: Initial token balances for simulation
            clear_approval_first: Whether to clear existing approval before setting new one

        Returns:
            Simulation result data
        """
        logger.info(
            f"Simulating approval: {amount} from {from_address} to {to_address} (chain {chain_id})"
        )
        start_time = time.time()

        url = f"{self.api_base_url}public/simulate/approve/"

        payload = {
            "from_address": from_address,
            "to_address": to_address,
            "token_address": token_address,
            "amount": amount,
            "chain_id": chain_id,
            "initial_balances": initial_balances,
            "clear_approval_first": clear_approval_first,
        }

        try:
            response = await self._request("POST", url, json=payload, headers={})
            response.raise_for_status()
            data = response.json()
            elapsed = time.time() - start_time
            logger.info(f"Simulation request completed successfully in {elapsed:.2f}s")
            return data.get("data", data)
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Simulation request failed after {elapsed:.2f}s: {e}")
            raise

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
        """
        Simulate token swap operation.

        Args:
            from_token_address: Source token contract address
            to_token_address: Destination token contract address
            from_chain_id: Source chain ID
            to_chain_id: Destination chain ID
            amount: Amount to swap
            from_address: Wallet address initiating swap
            slippage: Maximum slippage tolerance
            initial_balances: Initial token balances for simulation

        Returns:
            Simulation result data
        """
        logger.info(
            f"Simulating swap: {from_token_address} -> {to_token_address} (chain {from_chain_id} -> {to_chain_id})"
        )
        start_time = time.time()

        url = f"{self.api_base_url}public/simulate/swap/"

        payload = {
            "from_token_address": from_token_address,
            "to_token_address": to_token_address,
            "from_chain_id": from_chain_id,
            "to_chain_id": to_chain_id,
            "amount": amount,
            "from_address": from_address,
            "slippage": slippage,
            "initial_balances": initial_balances,
        }

        try:
            response = await self._request("POST", url, json=payload, headers={})
            response.raise_for_status()
            data = response.json()
            elapsed = time.time() - start_time
            logger.info(f"Simulation request completed successfully in {elapsed:.2f}s")
            return data.get("data", data)
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Simulation request failed after {elapsed:.2f}s: {e}")
            raise
