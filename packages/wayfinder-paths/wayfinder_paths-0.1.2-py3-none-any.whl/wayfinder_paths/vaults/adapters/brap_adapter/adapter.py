from typing import Any

from eth_utils import to_checksum_address

from wayfinder_paths.core.adapters.BaseAdapter import BaseAdapter
from wayfinder_paths.core.clients.BRAPClient import BRAPClient
from wayfinder_paths.core.clients.SimulationClient import SimulationClient
from wayfinder_paths.core.clients.TokenClient import TokenClient
from wayfinder_paths.core.constants import DEFAULT_SLIPPAGE
from wayfinder_paths.core.services.base import Web3Service
from wayfinder_paths.core.settings import settings
from wayfinder_paths.vaults.adapters.ledger_adapter.adapter import LedgerAdapter
from wayfinder_paths.vaults.adapters.token_adapter.adapter import TokenAdapter

_NEEDS_CLEAR_APPROVAL = {
    (1, "0xdac17f958d2ee523a2206206994597c13d831ec7"),
    (137, "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"),
    (56, "0x55d398326f99059ff775485246999027b3197955"),
}


class BRAPAdapter(BaseAdapter):
    """
    BRAP (Bridge/Router/Adapter Protocol) adapter for cross-chain swaps and quotes.

    Provides high-level operations for:
    - Getting swap quotes across chains
    - Executing cross-chain transactions
    - Route optimization and fee calculation
    - Bridge operations
    """

    adapter_type: str = "BRAP"

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        *,
        web3_service: Web3Service,
        simulation: bool = False,
    ):
        super().__init__("brap_adapter", config)
        self.brap_client = BRAPClient()
        self.token_client = TokenClient()
        self.token_adapter = TokenAdapter()
        self.ledger_adapter = LedgerAdapter()
        self.web3_service = web3_service
        self.wallet_provider = web3_service.evm_transactions
        self.token_transactions = web3_service.token_transactions
        self.simulation = simulation
        self.simulation_client = SimulationClient() if simulation else None

    async def get_swap_quote(
        self,
        from_token_address: str,
        to_token_address: str,
        from_chain_id: int,
        to_chain_id: int,
        from_address: str,
        to_address: str,
        amount: str,
        slippage: float | None = None,
        wayfinder_fee: float | None = None,
    ) -> tuple[bool, Any]:
        """
        Get a quote for a cross-chain swap operation.

        Args:
            from_token_address: Source token contract address
            to_token_address: Destination token contract address
            from_chain_id: Source chain ID
            to_chain_id: Destination chain ID
            from_address: Source wallet address
            to_address: Destination wallet address
            amount: Amount to swap (in smallest units)
            slippage: Maximum slippage tolerance (optional)
            wayfinder_fee: Wayfinder fee (optional)

        Returns:
            Tuple of (success, data) where data is quote information or error message
        """
        try:
            data = await self.brap_client.get_quote(
                from_token_address=from_token_address,
                to_token_address=to_token_address,
                from_chain_id=from_chain_id,
                to_chain_id=to_chain_id,
                from_address=from_address,
                to_address=to_address,
                amount1=amount,
                slippage=slippage,
                wayfinder_fee=wayfinder_fee,
            )
            return (True, data)
        except Exception as e:
            self.logger.error(f"Error getting swap quote: {e}")
            return (False, str(e))

    async def get_best_quote(
        self,
        from_token_address: str,
        to_token_address: str,
        from_chain_id: int,
        to_chain_id: int,
        from_address: str,
        to_address: str,
        amount: str,
        slippage: float | None = None,
        wayfinder_fee: float | None = None,
    ) -> tuple[bool, Any]:
        """
        Get the best available quote for a swap operation.

        Args:
            from_token_address: Source token contract address
            to_token_address: Destination token contract address
            from_chain_id: Source chain ID
            to_chain_id: Destination chain ID
            from_address: Source wallet address
            to_address: Destination wallet address
            amount: Amount to swap (in smallest units)
            slippage: Maximum slippage tolerance (optional)
            wayfinder_fee: Wayfinder fee (optional)

        Returns:
            Tuple of (success, data) where data is best quote or error message
        """
        try:
            data = await self.brap_client.get_quote(
                from_token_address=from_token_address,
                to_token_address=to_token_address,
                from_chain_id=from_chain_id,
                to_chain_id=to_chain_id,
                from_address=from_address,
                to_address=to_address,
                amount1=amount,
                slippage=slippage,
                wayfinder_fee=wayfinder_fee,
            )

            # Extract best quote from response
            quotes = data.get("quotes", {})
            best_quote = quotes.get("best_quote")

            if not best_quote:
                return (False, "No quotes available")

            return (True, best_quote)
        except Exception as e:
            self.logger.error(f"Error getting best quote: {e}")
            return (False, str(e))

    async def calculate_swap_fees(
        self,
        from_token_address: str,
        to_token_address: str,
        from_chain_id: int,
        to_chain_id: int,
        amount: str,
        slippage: float | None = None,
    ) -> tuple[bool, Any]:
        """
        Calculate fees for a swap operation.

        Args:
            from_token_address: Source token contract address
            to_token_address: Destination token contract address
            from_chain_id: Source chain ID
            to_chain_id: Destination chain ID
            amount: Amount to swap (in smallest units)
            slippage: Maximum slippage tolerance (optional)

        Returns:
            Tuple of (success, data) where data is fee breakdown or error message
        """
        try:
            # Get quote to extract fee information
            success, quote_data = await self.get_swap_quote(
                from_token_address=from_token_address,
                to_token_address=to_token_address,
                from_chain_id=from_chain_id,
                to_chain_id=to_chain_id,
                from_address="0x0000000000000000000000000000000000000000",  # Dummy address
                to_address="0x0000000000000000000000000000000000000000",  # Dummy address
                amount=amount,
                slippage=slippage,
            )

            if not success:
                return (False, quote_data)

            quotes = quote_data.get("quotes", {})
            best_quote = quotes.get("best_quote")

            if not best_quote:
                return (False, "No quote available for fee calculation")

            # Extract fee information
            fees = {
                "input_amount": best_quote.get("input_amount", 0),
                "output_amount": best_quote.get("output_amount", 0),
                "gas_fee": best_quote.get("gas_fee", 0),
                "bridge_fee": best_quote.get("bridge_fee", 0),
                "protocol_fee": best_quote.get("protocol_fee", 0),
                "total_fee": best_quote.get("total_fee", 0),
                "slippage": best_quote.get("slippage", 0),
                "price_impact": best_quote.get("price_impact", 0),
            }

            return (True, fees)
        except Exception as e:
            self.logger.error(f"Error calculating swap fees: {e}")
            return (False, str(e))

    async def compare_routes(
        self,
        from_token_address: str,
        to_token_address: str,
        from_chain_id: int,
        to_chain_id: int,
        amount: str,
        slippage: float | None = None,
    ) -> tuple[bool, Any]:
        """
        Compare multiple routes for a swap operation.

        Args:
            from_token_address: Source token contract address
            to_token_address: Destination token contract address
            from_chain_id: Source chain ID
            to_chain_id: Destination chain ID
            amount: Amount to swap (in smallest units)
            slippage: Maximum slippage tolerance (optional)

        Returns:
            Tuple of (success, data) where data is route comparison or error message
        """
        try:
            data = await self.brap_client.get_quote(
                from_token_address=from_token_address,
                to_token_address=to_token_address,
                from_chain_id=from_chain_id,
                to_chain_id=to_chain_id,
                from_address="0x0000000000000000000000000000000000000000",  # Dummy address
                to_address="0x0000000000000000000000000000000000000000",  # Dummy address
                amount1=amount,
                slippage=slippage,
            )

            quotes = data.get("quotes", {})
            all_quotes = quotes.get("quotes", [])
            best_quote = quotes.get("best_quote")

            if not all_quotes:
                return (False, "No routes available")

            # Sort quotes by output amount (descending)
            sorted_quotes = sorted(
                all_quotes, key=lambda x: int(x.get("output_amount", 0)), reverse=True
            )

            comparison = {
                "total_routes": len(all_quotes),
                "best_route": best_quote,
                "all_routes": sorted_quotes,
                "route_analysis": {
                    "highest_output": sorted_quotes[0] if sorted_quotes else None,
                    "lowest_fees": min(
                        all_quotes, key=lambda x: int(x.get("total_fee", 0))
                    )
                    if all_quotes
                    else None,
                    "fastest": min(
                        all_quotes, key=lambda x: int(x.get("estimated_time", 0))
                    )
                    if all_quotes
                    else None,
                },
            }

            return (True, comparison)
        except Exception as e:
            self.logger.error(f"Error comparing routes: {e}")
            return (False, str(e))

    async def swap_from_token_ids(
        self,
        from_token_id: str,
        to_token_id: str,
        from_address: str,
        amount: str,
        slippage: float = DEFAULT_SLIPPAGE,
        strategy_name: str | None = None,
    ) -> tuple[bool, Any]:
        """
        Execute a swap by looking up token metadata via token IDs.
        """
        from_token = await self.token_client.get_token_details(from_token_id)
        if not from_token:
            return (False, f"From token not found: {from_token_id}")
        to_token = await self.token_client.get_token_details(to_token_id)
        if not to_token:
            return (False, f"To token not found: {to_token_id}")

        success, best_quote = await self.get_best_quote(
            from_token_address=from_token.get("address"),
            to_token_address=to_token.get("address"),
            from_chain_id=(from_token.get("chain") or {}).get("id"),
            to_chain_id=(to_token.get("chain") or {}).get("id"),
            from_address=from_address,
            to_address=from_address,
            amount=amount,
            slippage=slippage,
        )
        if not success:
            return (False, best_quote)

        return await self.swap_from_quote(
            from_token=from_token,
            to_token=to_token,
            from_address=from_address,
            quote=best_quote,
            strategy_name=strategy_name,
        )

    async def swap_from_quote(
        self,
        from_token: dict[str, Any],
        to_token: dict[str, Any],
        from_address: str,
        quote: dict[str, Any],
        strategy_name: str | None = None,
    ) -> tuple[bool, Any]:
        """
        Execute a swap using a previously retrieved BRAP quote.
        """
        chain = from_token.get("chain") or {}
        chain_id = self._chain_id(chain)

        transaction = dict(quote.get("calldata") or {})
        if not transaction:
            return (False, "Quote missing calldata")
        transaction["chainId"] = chain_id
        transaction["from"] = to_checksum_address(from_address)

        spender = transaction.get("to")
        approve_amount = (
            quote.get("input_amount")
            or quote.get("inputAmount")
            or transaction.get("value")
        )
        if from_token.get("address") and spender and approve_amount:
            approve_success, approve_response = await self._handle_token_approval(
                chain=chain,
                token_address=from_token.get("address"),
                owner_address=from_address,
                spender_address=spender,
                amount=int(approve_amount),
            )
            if not approve_success:
                return (False, approve_response)

        if self.simulation:
            simulation = await self._simulate_swap(
                from_token, to_token, from_address, chain_id, quote
            )
            return (True, {"quote": quote, "simulation": simulation})

        broadcast_success, broadcast_response = await self._broadcast_transaction(
            transaction
        )
        if not broadcast_success:
            return (False, broadcast_response)

        ledger_record = await self._record_swap_operation(
            from_token=from_token,
            to_token=to_token,
            wallet_address=from_address,
            quote=quote,
            broadcast_response=broadcast_response,
            strategy_name=strategy_name,
        )
        return (True, ledger_record)

    async def get_bridge_quote(
        self,
        from_token_address: str,
        to_token_address: str,
        from_chain_id: int,
        to_chain_id: int,
        amount: str,
        slippage: float | None = None,
    ) -> tuple[bool, Any]:
        """
        Get a quote for a bridge operation (same as swap for BRAP).

        Args:
            from_token_address: Source token contract address
            to_token_address: Destination token contract address
            from_chain_id: Source chain ID
            to_chain_id: Destination chain ID
            amount: Amount to bridge (in smallest units)
            slippage: Maximum slippage tolerance (optional)

        Returns:
            Tuple of (success, data) where data is bridge quote or error message
        """
        # For BRAP, bridge operations are the same as swap operations
        return await self.get_swap_quote(
            from_token_address=from_token_address,
            to_token_address=to_token_address,
            from_chain_id=from_chain_id,
            to_chain_id=to_chain_id,
            from_address="0x0000000000000000000000000000000000000000",  # Dummy address
            to_address="0x0000000000000000000000000000000000000000",  # Dummy address
            amount=amount,
            slippage=slippage,
        )

    async def estimate_gas_cost(
        self, from_chain_id: int, to_chain_id: int, operation_type: str = "swap"
    ) -> tuple[bool, Any]:
        """
        Estimate gas costs for a cross-chain operation.

        Args:
            from_chain_id: Source chain ID
            to_chain_id: Destination chain ID
            operation_type: Type of operation ("swap", "bridge")

        Returns:
            Tuple of (success, data) where data is gas cost estimate or error message
        """
        try:
            # This is a simplified estimation - in practice, you'd want to
            # query actual gas prices from the chains
            gas_estimates = {
                "ethereum": {"swap": 150000, "bridge": 200000},
                "base": {"swap": 100000, "bridge": 150000},
                "arbitrum": {"swap": 80000, "bridge": 120000},
                "polygon": {"swap": 60000, "bridge": 100000},
            }

            # Map chain IDs to names (simplified)
            chain_names = {
                1: "ethereum",
                8453: "base",
                42161: "arbitrum",
                137: "polygon",
            }

            from_chain = chain_names.get(from_chain_id, "unknown")
            to_chain = chain_names.get(to_chain_id, "unknown")

            from_gas = gas_estimates.get(from_chain, {}).get(operation_type, 100000)
            to_gas = gas_estimates.get(to_chain, {}).get(operation_type, 100000)

            return (
                True,
                {
                    "from_chain": from_chain,
                    "to_chain": to_chain,
                    "from_gas_estimate": from_gas,
                    "to_gas_estimate": to_gas,
                    "total_operations": 2 if from_chain_id != to_chain_id else 1,
                    "operation_type": operation_type,
                },
            )
        except Exception as e:
            self.logger.error(f"Error estimating gas cost: {e}")
            return (False, str(e))

    async def validate_swap_parameters(
        self,
        from_token_address: str,
        to_token_address: str,
        from_chain_id: int,
        to_chain_id: int,
        amount: str,
    ) -> tuple[bool, Any]:
        """
        Validate swap parameters before executing.

        Args:
            from_token_address: Source token contract address
            to_token_address: Destination token contract address
            from_chain_id: Source chain ID
            to_chain_id: Destination chain ID
            amount: Amount to swap (in smallest units)

        Returns:
            Tuple of (success, data) where data is validation result or error message
        """
        try:
            validation_errors = []

            # Basic validation
            if not from_token_address or len(from_token_address) != 42:
                validation_errors.append("Invalid from_token_address")

            if not to_token_address or len(to_token_address) != 42:
                validation_errors.append("Invalid to_token_address")

            if from_chain_id <= 0 or to_chain_id <= 0:
                validation_errors.append("Invalid chain IDs")

            try:
                amount_int = int(amount)
                if amount_int <= 0:
                    validation_errors.append("Amount must be positive")
            except (ValueError, TypeError):
                validation_errors.append("Invalid amount format")

            if validation_errors:
                return (False, {"valid": False, "errors": validation_errors})

            # Try to get a quote to validate the swap is possible
            success, quote_data = await self.get_swap_quote(
                from_token_address=from_token_address,
                to_token_address=to_token_address,
                from_chain_id=from_chain_id,
                to_chain_id=to_chain_id,
                from_address="0x0000000000000000000000000000000000000000",
                to_address="0x0000000000000000000000000000000000000000",
                amount=amount,
            )

            if not success:
                validation_errors.append(f"Swap not possible: {quote_data}")
                return (False, {"valid": False, "errors": validation_errors})

            return (
                True,
                {
                    "valid": True,
                    "quote_available": True,
                    "estimated_output": quote_data.get("quotes", {})
                    .get("best_quote", {})
                    .get("output_amount", "0"),
                },
            )
        except Exception as e:
            self.logger.error(f"Error validating swap parameters: {e}")
            return (False, str(e))

    async def _handle_token_approval(
        self,
        *,
        chain: dict[str, Any],
        token_address: str,
        owner_address: str,
        spender_address: str,
        amount: int,
    ) -> tuple[bool, Any]:
        chain_id = self._chain_id(chain)
        token_checksum = to_checksum_address(token_address)
        owner_checksum = to_checksum_address(owner_address)
        spender_checksum = to_checksum_address(spender_address)

        if (chain_id, token_checksum.lower()) in _NEEDS_CLEAR_APPROVAL:
            allowance = await self.token_transactions.read_erc20_allowance(
                {"id": chain_id},
                token_checksum,
                owner_checksum,
                spender_checksum,
            )
            if allowance.get("allowance", 0) > 0:
                clear_success, clear_tx = self.token_transactions.build_erc20_approve(
                    chain_id=chain_id,
                    token_address=token_checksum,
                    from_address=owner_checksum,
                    spender=spender_checksum,
                    amount=0,
                )
                if not clear_success:
                    return False, clear_tx
                clear_result = await self._broadcast_transaction(clear_tx)
                if not clear_result[0]:
                    return clear_result

        build_success, approve_tx = self.token_transactions.build_erc20_approve(
            chain_id=chain_id,
            token_address=token_checksum,
            from_address=owner_checksum,
            spender=spender_checksum,
            amount=int(amount),
        )
        if not build_success:
            return False, approve_tx
        return await self._broadcast_transaction(approve_tx)

    async def _broadcast_transaction(
        self, transaction: dict[str, Any]
    ) -> tuple[bool, Any]:
        if getattr(settings, "DRY_RUN", False):
            return True, {"dry_run": True, "transaction": transaction}
        return await self.wallet_provider.broadcast_transaction(
            transaction,
            wait_for_receipt=True,
            timeout=120,
        )

    async def _record_swap_operation(
        self,
        from_token: dict[str, Any],
        to_token: dict[str, Any],
        wallet_address: str,
        quote: dict[str, Any],
        broadcast_response: dict[str, Any] | Any,
        strategy_name: str | None = None,
    ) -> Any:
        from_amount_usd = quote.get("from_amount_usd")
        if from_amount_usd is None:
            from_amount_usd = await self._token_amount_usd(
                from_token, quote.get("input_amount")
            )

        to_amount_usd = quote.get("to_amount_usd")
        if to_amount_usd is None:
            to_amount_usd = await self._token_amount_usd(
                to_token, quote.get("output_amount")
            )

        response = broadcast_response if isinstance(broadcast_response, dict) else {}
        operation_payload = {
            "type": "SWAP",
            "from_token_id": from_token.get("id"),
            "to_token_id": to_token.get("id"),
            "from_amount": quote.get("input_amount"),
            "to_amount": quote.get("output_amount"),
            "from_amount_usd": from_amount_usd or 0,
            "to_amount_usd": to_amount_usd or 0,
            "transaction_hash": response.get("transaction_hash"),
            "transaction_status": response.get("transaction_status"),
            "transaction_receipt": response.get("transaction_receipt"),
        }

        try:
            success, ledger_response = await self.ledger_adapter.record_operation(
                wallet_address=wallet_address,
                operation_data=operation_payload,
                usd_value=from_amount_usd or 0,
                strategy_name=strategy_name,
            )
            if success:
                return ledger_response
            self.logger.warning(
                "Ledger swap record failed", error=ledger_response, quote=quote
            )
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(f"Ledger swap record raised: {exc}", quote=quote)

        return operation_payload

    async def _token_amount_usd(
        self, token_info: dict[str, Any], raw_amount: Any
    ) -> float | None:
        if raw_amount is None:
            return None
        success, price_data = await self.token_adapter.get_token_price(
            token_info.get("id")
        )
        if not success or not price_data:
            return None
        decimals = token_info.get("decimals") or 18
        return (
            price_data.get("current_price", 0.0)
            * float(raw_amount)
            / 10 ** int(decimals)
        )

    async def _simulate_swap(
        self,
        from_token: dict[str, Any],
        to_token: dict[str, Any],
        from_address: str,
        chain_id: int,
        quote: dict[str, Any],
    ) -> Any:
        client = await self._get_simulation_client()
        initial_balances = {"native": "5000000000000000000"}
        if from_token.get("address"):
            initial_balances[from_token.get("address")] = "1000000000000000000000000"

        slippage = quote.get("slippage") or quote.get("slippage_percent")
        if isinstance(slippage, str):
            try:
                slippage = float(slippage)
            except ValueError:
                slippage = DEFAULT_SLIPPAGE
        slippage = slippage or DEFAULT_SLIPPAGE

        amount = quote.get("input_amount") or quote.get("inputAmount") or "0"
        return await client.simulate_swap(
            from_token_address=from_token.get("address"),
            to_token_address=to_token.get("address"),
            from_chain_id=chain_id,
            to_chain_id=chain_id,
            amount=str(amount),
            from_address=from_address,
            slippage=float(slippage),
            initial_balances=initial_balances,
        )

    async def _get_simulation_client(self) -> SimulationClient:
        if not self.simulation_client:
            self.simulation_client = SimulationClient()
        return self.simulation_client

    def _chain_id(self, chain: Any) -> int:
        if isinstance(chain, dict):
            chain_id = chain.get("id") or chain.get("chain_id")
        else:
            chain_id = getattr(chain, "id", None)
        if chain_id is None:
            raise ValueError("Chain ID is required")
        return int(chain_id)
