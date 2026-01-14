import asyncio
import math
import time
from datetime import UTC, datetime, timedelta
from typing import Any

from loguru import logger

from wayfinder_paths.core.constants.base import DEFAULT_SLIPPAGE
from wayfinder_paths.core.services.local_token_txn import (
    LocalTokenTxnService,
)
from wayfinder_paths.core.services.web3_service import DefaultWeb3Service
from wayfinder_paths.core.strategies.Strategy import StatusDict, StatusTuple, Strategy
from wayfinder_paths.core.wallets.WalletManager import WalletManager
from wayfinder_paths.vaults.adapters.balance_adapter.adapter import BalanceAdapter
from wayfinder_paths.vaults.adapters.brap_adapter.adapter import BRAPAdapter
from wayfinder_paths.vaults.adapters.ledger_adapter.adapter import LedgerAdapter
from wayfinder_paths.vaults.adapters.pool_adapter.adapter import PoolAdapter
from wayfinder_paths.vaults.adapters.token_adapter.adapter import TokenAdapter


class StablecoinYieldStrategy(Strategy):
    name = "Stablecoin Yield Strategy"

    # Strategy parameters
    MIN_AMOUNT_USDC = 2
    MINIMUM_DAYS_UNTIL_PROFIT = 7
    MIN_TVL = 1_000_000
    DUST_APY = 0.01
    MIN_GAS = 10e-4  # ethereum float
    SEARCH_DEPTH = 10
    SUPPORTED_NETWORK_CODES = {"base"}
    ROTATION_MIN_INTERVAL = timedelta(days=14)
    MINIMUM_APY_IMPROVEMENT = 0.01
    GAS_MAXIMUM = 0.02

    description = (
        "An automated yield optimization strategy that maximizes returns on USDC deposits on Base.\n\n"
        "What it does: Continuously scans and evaluates yield opportunities across Base-based DeFi protocols to find the "
        "highest-yielding, low-risk positions for USDC. Automatically rebalances positions when better opportunities "
        "emerge to maintain optimal yield generation.\n\n"
        "Exposure type: Stable USD-denominated exposure with minimal impermanent loss risk. Focuses exclusively on USDC "
        "and operations on the Base network to preserve capital and maximize yield.\n\n"
        "Chains: Operates solely on the Base network.\n\n"
        f"Deposit/Withdrawal: Accepts deposits only in USDC on Base with a minimum of {MIN_AMOUNT_USDC} USDC. Gas: Requires Base ETH "
        "for gas fees during position entry, rebalancing, and exit (~0.001-0.02 ETH per rebalance cycle). Strategy automatically "
        "deploys funds to an optimal yield farming position on Base. Withdrawals exit current positions and return USDC to the "
        "user wallet.\n\n"
        f"Risks: Primary risks include smart contract vulnerabilities in underlying Base DeFi protocols, temporary yield fluctuations, "
        f"gas costs during rebalancing, and potential brief capital lock-up during protocol transitions. Strategy filters for a minimum TVL of ${MIN_TVL:,}."
    )
    summary = (
        "Automated stablecoin yield farming across DeFi protocols on Base. "
        f"Continuously optimizes positions for maximum stable yield while avoiding impermanent loss. "
        f"Min: {MIN_AMOUNT_USDC} USDC + ETH gas. Filters for ${MIN_TVL:,}+ TVL protocols."
    )

    # config metadata for UIs/agents
    config = {
        "deposit": {
            "parameters": {
                "main_token_amount": {
                    "type": "float",
                    "description": "amount of Base USDC (token id: usd-coin-base) to deposit",
                },
                "gas_token_amount": {
                    "type": "float",
                    "description": "amount of Base ETH (token id: ethereum-base) to deposit for gas fees",
                    "minimum": 0,
                    "maximum": GAS_MAXIMUM,
                },
            },
            "process": "Deposits USDC on Base and searches for the highest yield opportunities among Base-based DeFi protocols",
            "requirements": [
                "Sufficient USDC balance on Base",
                "Base ETH available for gas",
            ],
            "result": "Funds deployed to a yield farming position on Base",
        },
        "withdraw": {
            "parameters": {},
            "process": "Exits yield positions on Base and returns USDC to the user wallet",
            "requirements": [
                "Active positions to exit",
                "Gas for transactions on Base",
            ],
            "result": "USDC returned to wallet and positions closed on Base",
        },
        "update": {
            "parameters": {},
            "process": "Scans for better yield opportunities on Base and rebalances positions automatically",
            "frequency": "Call daily or when significant yield changes occur",
            "requirements": [
                "Active strategy positions on Base",
                "Sufficient Base gas for rebalancing",
            ],
            "result": "Positions optimized for maximum yield on Base",
        },
        "technical_details": {
            "wallet_structure": "Uses strategy subwallet for isolation",
            "chains": ["Base"],
            "protocols": ["Various Base DeFi yield protocols"],
            "tokens": ["USDC"],
            "gas_requirements": "~0.001-0.02 ETH per rebalance on Base",
            "search_depth": SEARCH_DEPTH,
            "minimum_tvl": MIN_TVL,
            "dust_apy_threshold": DUST_APY,
            "minimum_apy_edge": MINIMUM_APY_IMPROVEMENT,
            "rotation_cooldown_days": ROTATION_MIN_INTERVAL.days,
            "profit_horizon_days": MINIMUM_DAYS_UNTIL_PROFIT,
        },
    }

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        *,
        main_wallet: dict[str, Any] | None = None,
        vault_wallet: dict[str, Any] | None = None,
        simulation: bool = False,
        web3_service=None,
        api_key: str | None = None,
    ):
        super().__init__(api_key=api_key)
        merged_config: dict[str, Any] = dict(config or {})
        if main_wallet is not None:
            merged_config["main_wallet"] = main_wallet
        if vault_wallet is not None:
            merged_config["vault_wallet"] = vault_wallet

        self.config = merged_config
        self.simulation = simulation
        self.deposited_amount = 0
        self.current_pool = None
        self.current_apy = 0
        self.balance_adapter = None
        self.tx_adapter = None
        self.web3_service = web3_service
        self.token_adapter = None
        self.ledger_adapter = None
        self.pool_adapter = None
        self.brap_adapter = None

        try:
            main_wallet_cfg = self.config.get("main_wallet")
            vault_wallet_cfg = self.config.get("vault_wallet")

            adapter_config = {
                "main_wallet": main_wallet_cfg or None,
                "vault_wallet": vault_wallet_cfg or None,
                "strategy": self.config,
            }

            if self.web3_service is None:
                wallet_provider = WalletManager.get_provider(adapter_config)
                tx_adapter = LocalTokenTxnService(
                    adapter_config,
                    wallet_provider=wallet_provider,
                    simulation=self.simulation,
                )
                web3_service = DefaultWeb3Service(
                    wallet_provider=wallet_provider, evm_transactions=tx_adapter
                )
            else:
                web3_service = self.web3_service
                tx_adapter = web3_service.token_transactions
            balance = BalanceAdapter(adapter_config, web3_service=web3_service)
            token_adapter = TokenAdapter()
            ledger_adapter = LedgerAdapter()
            pool_adapter = PoolAdapter()
            brap_adapter = BRAPAdapter(
                web3_service=web3_service, simulation=self.simulation
            )

            self.register_adapters(
                [
                    balance,
                    token_adapter,
                    ledger_adapter,
                    pool_adapter,
                    brap_adapter,
                    tx_adapter,
                ]
            )
            self.balance_adapter = balance
            self.tx_adapter = tx_adapter
            self.web3_service = web3_service
            self.token_adapter = token_adapter
            self.ledger_adapter = ledger_adapter
            self.pool_adapter = pool_adapter
            self.brap_adapter = brap_adapter

        except Exception:
            pass

    def _get_vault_wallet_address(self) -> str:
        """Get vault wallet address with validation."""
        vault_wallet = self.config.get("vault_wallet")
        if not vault_wallet or not isinstance(vault_wallet, dict):
            raise ValueError("vault_wallet not configured in strategy config")
        address = vault_wallet.get("address")
        if not address:
            raise ValueError("vault_wallet address not found in config")
        return str(address)

    def _get_main_wallet_address(self) -> str:
        """Get main wallet address with validation."""
        main_wallet = self.config.get("main_wallet")
        if not main_wallet or not isinstance(main_wallet, dict):
            raise ValueError("main_wallet not configured in strategy config")
        address = main_wallet.get("address")
        if not address:
            raise ValueError("main_wallet address not found in config")
        return str(address)

    async def setup(self):
        logger.info("Starting StablecoinYieldStrategy setup")
        start_time = time.time()

        await super().setup()
        self.current_combined_apy_pct = 0.0

        # Get vault net deposit
        try:
            logger.info("Fetching vault net deposit from ledger")
            vault_address = self._get_vault_wallet_address()
            success, deposit_data = await self.ledger_adapter.get_vault_net_deposit(
                wallet_address=vault_address,
            )
            if success:
                self.DEPOSIT_USDC = deposit_data.get("net_deposit", 0)
                logger.info(f"Vault net deposit: {self.DEPOSIT_USDC} USDC")
            else:
                logger.error(f"Failed to fetch vault net deposit: {deposit_data}")
                self.DEPOSIT_USDC = 0
        except Exception as e:
            logger.error(f"Failed to fetch vault net deposit: {e}")
            self.DEPOSIT_USDC = 0

        # Get USDC token info
        try:
            logger.info("Fetching USDC token information")
            success, self.usdc_token_info = await self.token_adapter.get_token(
                "usd-coin-base"
            )
            if not success:
                logger.warning("Failed to fetch USDC token info, using empty dict")
                self.usdc_token_info = {}
            else:
                logger.info(
                    f"USDC token info loaded: {self.usdc_token_info.get('symbol', 'Unknown')} on {self.usdc_token_info.get('chain', {}).get('name', 'Unknown')}"
                )
        except Exception as e:
            logger.error(f"Error fetching USDC token info: {e}")
            self.usdc_token_info = {}

        self.current_pool = {
            "token_id": self.usdc_token_info.get("token_id"),
            "name": self.usdc_token_info.get("name"),
            "symbol": self.usdc_token_info.get("symbol"),
            "decimals": self.usdc_token_info.get("decimals", 18),
            "address": self.usdc_token_info.get("address"),
            "chain": self.usdc_token_info.get("chain", {"code": "base", "id": 8453}),
        }

        self.current_pool_data = None

        chain_code = "base"  # Default to base
        if self.current_pool and self.current_pool.get("chain"):
            chain_code = self.current_pool.get("chain").get("code", "base")

        # Get gas token info
        try:
            logger.info(f"Fetching gas token for chain: {chain_code}")
            success, gas_token_data = await self.token_adapter.get_gas_token(chain_code)
            if success:
                self.gas_token = gas_token_data
                logger.info(
                    f"Gas token loaded: {gas_token_data.get('symbol', 'Unknown')}"
                )
            else:
                logger.warning("Failed to fetch gas token info, using empty dict")
                self.gas_token = {}
        except Exception as e:
            logger.error(f"Error fetching gas token info: {e}")
            self.gas_token = {}

        if not self.DEPOSIT_USDC:
            logger.info("No deposits found, setting current pool balance to 0")
            self.current_pool_balance = 0
            return

        # Get vault transactions to determine current position
        try:
            logger.info("Fetching vault transaction history")
            success, txns_data = await self.ledger_adapter.get_vault_transactions(
                wallet_address=self._get_vault_wallet_address(),
            )
            if success:
                txns = [
                    txn
                    for txn in txns_data.get("transactions", [])
                    if txn.get("operation") != "DEPOSIT"
                ]
                logger.info(f"Found {len(txns)} non-deposit transactions")
            else:
                logger.error(f"Failed to fetch vault transactions: {txns_data}")
                txns = []
        except Exception as e:
            logger.error(f"Failed to fetch vault transactions: {e}")
            txns = []

        if txns and txns[-1].get("operation") != "WITHDRAW":
            pos = txns[-1].get("data").get("op_data")
            success, token_info = await self.token_adapter.get_token(
                pos.get("to_token_id")
            )
            if not success:
                token_info = {}
            self.current_pool = {
                "token_id": token_info.get("token_id"),
                "name": token_info.get("name"),
                "symbol": token_info.get("symbol"),
                "decimals": token_info.get("decimals"),
                "address": token_info.get("address"),
                "chain": token_info.get("chain"),
            }

            success, reports = await self.pool_adapter.get_pools_by_ids(
                pool_ids=[self.current_pool.get("token_id")],
                merge_external=False,
            )
            if success and reports.get("pools"):
                self.current_pool_data = reports.get("pools", [])[0]

        identifiers = []
        pool_id = self.current_pool.get("token_id", None)
        if isinstance(pool_id, str):
            identifiers.append(pool_id)

        pool_address = self.current_pool.get("address", None)
        pool_chain = self.current_pool.get("chain", None)
        chain_code = ((pool_chain or {}).get("code")) or None
        if isinstance(pool_address, str) and isinstance(chain_code, str):
            identifiers.append(f"{chain_code.lower()}_{pool_address.lower()}")

        llama_report = None
        if identifiers:
            success, llama_reports = await self.pool_adapter.get_llama_reports(
                identifiers=identifiers
            )
            if success:
                for identifier in identifiers:
                    if not isinstance(identifier, str):
                        continue
                    report = llama_reports.get(identifier.lower(), None)
                    if report:
                        llama_report = report
                        break

        if self.current_pool_data is None and llama_report:
            self.current_pool_data = {
                **self.current_pool_data,
                "llama_report": llama_report,
            }

        if llama_report and llama_report.get("llama_combined_apy_pct") is not None:
            self.current_combined_apy_pct = (
                llama_report.get("llama_combined_apy_pct", 0) / 100
            )
        elif llama_report and llama_report.get("llama_apy_pct") is not None:
            self.current_combined_apy_pct = llama_report.get("llama_apy_pct", 0) / 100
        elif self.current_pool_data:
            self.current_combined_apy_pct = self.current_pool_data.get("apy", 0)

        pool_address = self.current_pool.get("address")
        chain_id = self.current_pool.get("chain", {}).get("id")
        user_address = self._get_vault_wallet_address()
        if (
            pool_address
            and chain_id
            and user_address
            and pool_address != self.usdc_token_info.get("address")
        ):
            try:
                (
                    success,
                    current_pool_balance_raw,
                ) = await self.balance_adapter.get_pool_balance(
                    pool_address=pool_address,
                    chain_id=chain_id,
                    user_address=user_address,
                )
                self.current_pool_balance = current_pool_balance_raw if success else 0
            except Exception as e:
                print(f"Warning: Failed to get pool balance: {e}")
                self.current_pool_balance = 0
        else:
            self.current_pool_balance = 0

        baseline_token = (
            self.usdc_token_info
            if self.usdc_token_info.get("chain", {}).get("id")
            == self.current_pool.get("chain").get("id")
            else None
        )
        if (
            baseline_token
            and self.current_pool.get("token_id") != baseline_token.get("token_id")
            and self.current_pool_balance
        ):
            return

        inferred = await self._infer_active_pool_from_wallet()
        if inferred is not None:
            inferred_token, inferred_balance, inferred_entry = inferred
            self.current_pool = inferred_token
            self.current_pool_balance = inferred_balance
            if inferred_entry:
                self.current_pool_data = inferred_entry
                llama_combined = inferred_entry.get("llama_combined_apy_pct")
                llama_apy = inferred_entry.get("llama_apy_pct")
                if llama_combined is not None:
                    self.current_combined_apy_pct = float(llama_combined) / 100
                elif llama_apy is not None:
                    self.current_combined_apy_pct = float(llama_apy) / 100
            return

        if self.usdc_token_info:
            status, raw_balance = await self.balance_adapter.get_balance(
                token_id=self.usdc_token_info.get("token_id"),
                wallet_address=self._get_vault_wallet_address(),
            )
            if not status or not raw_balance:
                return
            try:
                balance_wei = int(raw_balance)
            except (TypeError, ValueError):
                return
            if balance_wei <= 0:
                return

            self.current_pool = self.usdc_token_info
            self.current_pool_balance = balance_wei
            self.current_combined_apy_pct = 0.0
            self.current_pool_data = None

            return

        elapsed_time = time.time() - start_time
        logger.info(
            f"StablecoinYieldStrategy setup completed in {elapsed_time:.2f} seconds"
        )

    def _sum_non_gas_balance_usd(self, balances: list[dict[str, Any]] | None) -> float:
        total_usd = 0.0
        for bal in balances or []:
            if self._is_gas_balance_entry(bal):
                continue
            usd_value = bal.get("balanceUSD")
            try:
                total_usd += float(usd_value or 0.0)
            except (TypeError, ValueError):
                continue
        return total_usd

    async def _infer_active_pool_from_wallet(self):
        try:
            (
                _,
                wallet_balances,
            ) = await self.balance_adapter.get_all_balances(
                wallet_address=self._get_vault_wallet_address(),
                enrich=True,
                from_cache=False,
                add_llama=True,
            )
        except Exception:
            return None

        if not wallet_balances:
            return None

        target_chain = self.current_pool.get("chain").get("name").lower()
        usdc_token = (
            self.usdc_token_info
            if self.usdc_token_info.get("chain").get("name").lower() == target_chain
            else None
        )
        usdc_address = usdc_token.get("address").lower() if usdc_token else ""

        best_entry = None
        best_balance_wei = 0
        best_balance_usd = 0.0

        for balance in wallet_balances.get("balances"):
            if self._is_gas_balance_entry(balance):
                continue

            network = (balance.get("network") or "").lower()
            if network != target_chain:
                continue

            token_address = balance.get("tokenAddress")
            if not token_address or token_address.lower() == usdc_address:
                continue

            raw_balance = balance.get("balance_base_units")
            try:
                balance_wei = int(raw_balance)
            except (TypeError, ValueError):
                continue
            if balance_wei <= 0:
                continue

            balance_usd = float(balance.get("balanceUSD") or 0.0)
            if balance_usd <= 0:
                continue

            if best_entry is None or balance_usd > best_balance_usd:
                best_entry = balance
                best_balance_wei = balance_wei
                best_balance_usd = balance_usd

        # TODO: no successful best entry found in manual testing
        if not best_entry:
            return None

        token_id = best_entry.get("token_id")
        token_address = best_entry.get("tokenAddress")
        if not token_id and token_address:
            token_id = f"{target_chain}_{token_address.lower()}"

        if not token_id:
            return None

        success, token = await self.token_adapter.get_token(token_id)
        if not success:
            return None

        try:
            vault_address = self._get_vault_wallet_address()
            (
                success,
                onchain_balance,
            ) = await self.balance_adapter.get_balance(
                token_id=token.get("token_id"),
                wallet_address=vault_address,
            )
            if not success:
                onchain_balance = best_balance_wei
        except Exception:
            onchain_balance = best_balance_wei

        return token, onchain_balance, dict(best_entry)

    def _is_gas_balance_entry(self, balance: dict[str, Any]) -> bool:
        """Check if a balance entry represents a gas token."""
        if not self.gas_token:
            return False

        # Check by token ID
        token_id = balance.get("token_id")
        if (
            isinstance(token_id, str)
            and token_id.lower() == self.gas_token.get("id", "").lower()
        ):
            return True

        # Check by token address and network
        token_address = balance.get("tokenAddress")
        if isinstance(token_address, str):
            if token_address.lower() == self.gas_token.get("address", "").lower():
                return True

            # Check address + network combination
            network = (balance.get("network") or "").lower()
            chain_code = self.current_pool.get("chain", {}).get("code", "").lower()
            if (
                token_address.lower() == self.gas_token.get("address", "").lower()
                and network == chain_code
            ):
                return True

        return False

    async def deposit(
        self, main_token_amount: float = 0.0, gas_token_amount: float = 0.0
    ) -> StatusTuple:
        if main_token_amount == 0.0 and gas_token_amount == 0.0:
            return (
                False,
                "Either main_token_amount or gas_token_amount must be provided",
            )

        logger.info(
            f"Starting deposit process for {main_token_amount} USDC and {gas_token_amount} gas"
        )
        start_time = time.time()

        try:
            token_info = self.usdc_token_info
            self.current_pool = {
                "token_id": token_info.get("token_id"),
                "name": token_info.get("name"),
                "symbol": token_info.get("symbol"),
                "decimals": token_info.get("decimals"),
                "address": token_info.get("address"),
                "chain": token_info.get("chain"),
            }
            gas_token_id = self.gas_token.get("id")
            logger.info(
                f"Current pool set to: {token_info.get('symbol')} on {token_info.get('chain', {}).get('name')}"
            )

            # Check main wallet USDC balance if depositing main token
            if main_token_amount > 0:
                logger.info("Checking main wallet USDC balance")
                (
                    main_usdc_status,
                    main_usdc_balance,
                ) = await self.balance_adapter.get_balance(
                    token_id=token_info.get("token_id"),
                    wallet_address=self._get_main_wallet_address(),
                )
                if main_usdc_status and main_usdc_balance is not None:
                    try:
                        available_main_usdc = float(main_usdc_balance) / (
                            10 ** self.current_pool.get("decimals")
                        )
                        logger.info(f"Main wallet USDC balance: {available_main_usdc}")
                        if available_main_usdc >= 0:
                            main_token_amount = min(
                                main_token_amount, available_main_usdc
                            )
                            logger.info(
                                f"Adjusted deposit amount to available balance: {main_token_amount}"
                            )
                    except Exception as e:
                        logger.warning(f"Error processing main wallet balance: {e}")
                else:
                    logger.warning("Could not fetch main wallet USDC balance")

                if main_token_amount < self.MIN_AMOUNT_USDC:
                    logger.warning(
                        f"Deposit amount {main_token_amount} below minimum {self.MIN_AMOUNT_USDC}"
                    )
                    return (
                        False,
                        f"Minimum deposit is {self.MIN_AMOUNT_USDC} USDC on Base. Received: {main_token_amount}",
                    )

            # Check gas token amount if provided
            if gas_token_amount > 0:
                if gas_token_amount > self.GAS_MAXIMUM:
                    return (
                        False,
                        f"Gas token amount exceeds maximum configured gas buffer: {self.GAS_MAXIMUM}",
                    )

                logger.info("Checking main wallet gas token balance")
                gas_decimals = self.gas_token.get("decimals")
                gas_symbol = self.gas_token.get("symbol")
                (
                    _,
                    main_gas_raw,
                ) = await self.balance_adapter.get_balance(
                    token_id=gas_token_id,
                    wallet_address=self._get_main_wallet_address(),
                )
                main_gas_int = (
                    int(main_gas_raw)
                    if isinstance(main_gas_raw, int)
                    else int(float(main_gas_raw or 0))
                )
                main_gas_native = float(main_gas_int) / (10**gas_decimals)

                if main_gas_native < gas_token_amount:
                    return (
                        False,
                        f"Main wallet {gas_symbol} balance is less than the deposit amount: {main_gas_native} < {gas_token_amount}",
                    )

            # Check gas balances for minimum requirement (only if depositing main token)
            if main_token_amount > 0:
                logger.info("Checking gas token balances for operations")
                gas_decimals = self.gas_token.get("decimals")
                gas_symbol = self.gas_token.get("symbol")
                (
                    _,
                    main_gas_raw,
                ) = await self.balance_adapter.get_balance(
                    token_id=gas_token_id,
                    wallet_address=self._get_main_wallet_address(),
                )
                (
                    _,
                    vault_gas_raw,
                ) = await self.balance_adapter.get_balance(
                    token_id=gas_token_id,
                    wallet_address=self._get_vault_wallet_address(),
                )
                main_gas_int = (
                    int(main_gas_raw)
                    if isinstance(main_gas_raw, int)
                    else int(float(main_gas_raw or 0))
                )
                vault_gas_int = (
                    int(vault_gas_raw)
                    if isinstance(vault_gas_raw, int)
                    else int(float(vault_gas_raw or 0))
                )
                main_gas_native = float(main_gas_int) / (10**gas_decimals)
                vault_gas_native = float(vault_gas_int) / (10**gas_decimals)
                total_gas = main_gas_native + vault_gas_native
                logger.info(
                    f"Gas balances - Main: {main_gas_native} {gas_symbol}, Vault: {vault_gas_native} {gas_symbol}, Total: {total_gas} {gas_symbol}"
                )

                # Use provided gas_token_amount if available, otherwise ensure minimum
                required_gas = (
                    gas_token_amount if gas_token_amount > 0 else self.MIN_GAS
                )
                if total_gas < required_gas:
                    logger.warning(
                        f"Insufficient gas: {total_gas} < {required_gas} {gas_symbol}"
                    )
                    return (
                        False,
                        f"Need at least {required_gas} {gas_symbol} on Base for gas. You have: {total_gas}",
                    )

            # Transfer main token if provided
            if main_token_amount > 0:
                self.current_pool_balance = int(
                    main_token_amount * (10 ** self.current_pool.get("decimals"))
                )
                self.DEPOSIT_USDC = main_token_amount
                logger.info(f"Set deposit amount to {main_token_amount} USDC")

                # Transfer USDC from main to vault wallet
                logger.info("Initiating USDC transfer from main to vault wallet")
                (
                    success,
                    msg,
                ) = await self.balance_adapter.move_from_main_wallet_to_vault_wallet(
                    self.usdc_token_info.get("token_id"),
                    main_token_amount,
                    strategy_name=self.name,
                )
                if not success:
                    logger.error(f"USDC transfer failed: {msg}")
                    return (False, f"USDC transfer to vault failed: {msg}")
                logger.info("USDC transfer completed successfully")

            # Transfer gas if provided or if vault needs top-up
            if gas_token_amount > 0:
                # Get gas symbol if not already defined
                if main_token_amount == 0:
                    gas_symbol = self.gas_token.get("symbol")

                # Transfer the specified gas amount
                logger.info(
                    f"Transferring {gas_token_amount} {gas_symbol} from main wallet to vault"
                )
                (
                    success,
                    msg,
                ) = await self.balance_adapter.move_from_main_wallet_to_vault_wallet(
                    gas_token_id, gas_token_amount, strategy_name=self.name
                )
                if not success:
                    logger.error(f"Gas transfer failed: {msg}")
                    return (False, f"Gas transfer to vault failed: {msg}")
                logger.info("Gas transfer completed successfully")
            elif main_token_amount > 0 and vault_gas_native < self.MIN_GAS:
                # Auto-top-up to minimum if no gas amount specified and depositing main token
                top_up_amount = self.MIN_GAS - vault_gas_native
                logger.info(
                    f"Vault gas insufficient, transferring {top_up_amount} {gas_symbol} from main wallet"
                )
                (
                    success,
                    msg,
                ) = await self.balance_adapter.move_from_main_wallet_to_vault_wallet(
                    gas_token_id, top_up_amount, strategy_name=self.name
                )
                if not success:
                    logger.error(f"Gas transfer failed: {msg}")
                    return (False, f"Gas transfer to vault failed: {msg}")
                logger.info("Gas transfer completed successfully")

            elapsed_time = time.time() - start_time
            logger.info(f"Deposit completed successfully in {elapsed_time:.2f} seconds")
            return (
                True,
                "Deposit successful! Call update to open a position and start earning",
            )
        except Exception as e:
            logger.error(f"Deposit process failed: {e}")
            return (False, f"Deposit error: {e}")

    async def withdraw(self, amount: float | None = None) -> StatusTuple:
        logger.info(f"Starting withdrawal process for amount: {amount}")
        start_time = time.time()

        if not self.DEPOSIT_USDC:
            logger.warning("No deposits found, nothing to withdraw")
            return (
                False,
                "Nothing to withdraw from strategy, wallet should be empty already. If not, an error has happened please manually remove funds",
            )
        # Get current pool balance
        logger.info("Fetching current pool balance")
        try:
            (
                _,
                self.current_pool_balance,
            ) = await self.balance_adapter.get_pool_balance(
                pool_address=self.current_pool.get("address"),
                chain_id=self.current_pool.get("chain").get("id"),
                user_address=self._get_vault_wallet_address(),
            )
            logger.info(f"Current pool balance: {self.current_pool_balance}")
        except Exception as e:
            logger.error(f"Failed to fetch pool balance: {e}")
            self.current_pool_balance = 0

        # Check if we need to swap out of current position
        if (
            self.current_pool.get("token_id") != self.usdc_token_info.get("token_id")
            and self.current_pool_balance
        ):
            logger.info(
                f"Need to swap from {self.current_pool.get('symbol')} to USDC before withdrawal"
            )
            quotes = {}
            for attempt in range(4):
                logger.info(
                    f"Getting swap quote (attempt {attempt + 1}/4) with slippage: {DEFAULT_SLIPPAGE * (attempt + 1)}"
                )
                try:
                    success, quotes = await self.brap_adapter.get_swap_quote(
                        from_token_address=self.current_pool.get("address"),
                        to_token_address=self.usdc_token_info.get("address"),
                        from_chain_id=self.current_pool.get("chain").get("id"),
                        to_chain_id=self.usdc_token_info.get("chain").get("id"),
                        from_address=self._get_vault_wallet_address(),
                        to_address=self._get_vault_wallet_address(),
                        amount=str(self.current_pool_balance),
                        slippage=DEFAULT_SLIPPAGE * (attempt + 1),
                    )
                    if (
                        success
                        and quotes.get("quotes")
                        and quotes.get("quotes").get("best_quote")
                    ):
                        logger.info("Successfully obtained swap quote")
                        break
                except Exception as e:
                    logger.warning(f"Quote attempt {attempt + 1} failed: {e}")
                    if attempt == 3:  # Last attempt
                        logger.error("All quote attempts failed")

            best_quote = quotes.get("quotes").get("best_quote")
            if not best_quote:
                return (
                    False,
                    "Could not swap tokens out due to market conditions (balances too small to move or slippage required is too high) please manually move funds out",
                )

            if not best_quote.get("output_amount") or not best_quote.get(
                "input_amount"
            ):
                return (False, "Swap quote missing required fields")

            if not best_quote.get("from_amount_usd"):
                input_amount = int(best_quote.get("input_amount"))
                if self.current_pool.get("token_id") == self.usdc_token_info.get(
                    "token_id"
                ):
                    best_quote["from_amount_usd"] = float(input_amount) / (
                        10 ** self.current_pool.get("decimals")
                    )
                else:
                    best_quote["from_amount_usd"] = await self._get_pool_usd_value(
                        self.current_pool, input_amount
                    )

            if not best_quote.get("to_amount_usd"):
                output_amount = int(best_quote.get("output_amount"))
                best_quote["to_amount_usd"] = float(
                    output_amount
                ) / 10 ** self.usdc_token_info.get("decimals")

            if not self.brap_adapter:
                return (
                    False,
                    "BRAP adapter not initialized; cannot unwind position.",
                )

            success, swap_result = await self.brap_adapter.swap_from_quote(
                self.current_pool,
                self.usdc_token_info,
                self._get_vault_wallet_address(),
                best_quote,
                strategy_name=self.name,
            )
            if not success:
                return (
                    False,
                    f"Failed to unwind position via swap: {swap_result}",
                )

        await self._sweep_wallet(self.usdc_token_info)
        withdrawn_breakdown = []
        withdrawn_token_ids = set()

        if self.usdc_token_info.get("token_id") in withdrawn_token_ids:
            pass
        status, raw_balance = await self.balance_adapter.get_balance(
            token_id=self.usdc_token_info.get("token_id"),
            wallet_address=self._get_vault_wallet_address(),
        )
        if not status or not raw_balance:
            pass
        amount = float(raw_balance) / 10 ** self.usdc_token_info.get("decimals")
        if amount > 0:
            (
                move_status,
                move_message,
            ) = await self.balance_adapter.move_from_vault_wallet_to_main_wallet(
                self.usdc_token_info.get("token_id"),
                amount,
                strategy_name=self.name,
            )
            if not move_status:
                return (False, f"USDC return to main failed: {move_message}")

        withdrawn_breakdown.append(
            (
                self.usdc_token_info.get("symbol"),
                self.usdc_token_info.get("chain").get("name"),
                float(amount),
            )
        )
        withdrawn_token_ids.add(self.usdc_token_info.get("token_id"))

        if self.gas_token and self.gas_token.get("id") not in withdrawn_token_ids:
            status, raw_gas = await self.balance_adapter.get_balance(
                token_id=self.gas_token.get("id"),
                wallet_address=self._get_vault_wallet_address(),
            )
            if status and raw_gas:
                gas_amount = (
                    float(raw_gas) / 10 ** self.gas_token.get("decimals")
                ) * 0.9
                if gas_amount > 0:
                    (
                        move_gas_status,
                        move_gas_message,
                    ) = await self.balance_adapter.move_from_vault_wallet_to_main_wallet(
                        self.gas_token.get("id"),
                        gas_amount,
                        strategy_name=self.name,
                    )
                    if move_gas_status:
                        withdrawn_breakdown.append(
                            (
                                self.gas_token.get("symbol"),
                                self.gas_token.get("chain").get("name"),
                                float(gas_amount),
                            )
                        )
                        withdrawn_token_ids.add(self.gas_token.get("id"))

        self.DEPOSIT_USDC = 0
        self.current_pool_balance = 0

        if not withdrawn_breakdown:
            return (True, f"Successfully withdrew {amount} USDC from vault")

        breakdown_msg = ", ".join(
            f"{amount:.6f} {symbol} on {chain.capitalize()}"
            for symbol, chain, amount in withdrawn_breakdown
        )

        elapsed_time = time.time() - start_time
        logger.info(f"Withdrawal completed successfully in {elapsed_time:.2f} seconds")
        return (
            True,
            f"Successfully withdrew {amount} USDC from vault: {breakdown_msg}",
        )

    async def _get_last_rotation_time(self, wallet_address: str) -> datetime | None:
        success, data = await self.ledger_adapter.get_vault_latest_transactions(
            wallet_address=self._get_vault_wallet_address(),
        )
        if success is False:
            return None
        for transaction in data.get("transactions", []):
            op_data = transaction.get("op_data", {})
            if op_data.get("type") == "SWAP" and op_data.get(
                "to_token_id"
            ).lower() not in [
                "usd-coin-base",
                "base_0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
            ]:
                created_str = transaction.get("created")
                if not created_str:
                    continue
                try:
                    dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=UTC)
                    return dt
                except (ValueError, AttributeError):
                    continue
        return None

    async def update(self):
        logger.info("Starting strategy update process")
        start_time = time.time()

        if not self.DEPOSIT_USDC:
            logger.warning("No deposits found, cannot update strategy")
            return [False, "Nothing has been deposited in this vault, cannot update"]

        logger.info("Getting non-gas balances")
        non_gas_balances = await self._get_non_gas_balances()
        current_target = self.current_pool
        if current_target is None:
            current_target = self.usdc_token_info
            logger.info("No current pool set, using USDC as target")

        logger.info("Searching for best yield opportunities")
        should_deposit, pool_data = await self._find_best_pool()
        if not should_deposit:
            if (
                current_target
                and isinstance(current_target, dict)
                and await self._has_idle_assets(non_gas_balances, current_target)
            ):
                await self._sweep_wallet(current_target)
                await self._refresh_current_pool_balance()
                return (
                    True,
                    f"Consolidated assets into existing position {current_target.get('id')}",
                )

            if isinstance(pool_data, dict):
                message = pool_data.get(
                    "message", "No profitable pools found, staying in current pool"
                )
            else:
                message = (
                    str(pool_data)
                    if pool_data
                    else "No profitable pools found, staying in current pool"
                )
            return False, message

        if not isinstance(pool_data, dict):
            return [False, f"Invalid pool data format: {type(pool_data).__name__}"]

        target_pool = pool_data.get("target_pool")
        target_pool_data = pool_data.get("target_pool_data")
        brap_quote = pool_data.get("brap_quote")

        if not target_pool or not target_pool_data or not brap_quote:
            return [False, "Missing required pool data for rebalancing"]

        gas_status, gas_message = await self._rebalance_gas(target_pool)
        if not gas_status:
            return [False, gas_message]

        previous_pool = self.current_pool

        last_rotation = await self._get_last_rotation_time(
            wallet_address=self._get_vault_wallet_address(),
        )
        if (
            previous_pool
            and isinstance(previous_pool, dict)
            and previous_pool.get("token_id") != self.usdc_token_info.get("token_id")
            and last_rotation is not None
        ):
            now = datetime.now(UTC)
            if (now - last_rotation) < self.ROTATION_MIN_INTERVAL:
                elapsed = now - last_rotation
                remaining = self.ROTATION_MIN_INTERVAL - elapsed
                remaining_days_cooldown = max(0.0, remaining.total_seconds() / 86400)
                cooldown_notice = (
                    "Within 7-day cooldown; existing {coin} position retained. "
                    "≈{days:.1f} days until rotation window reopens."
                ).format(
                    coin=(
                        previous_pool.get("token_id", "unknown")
                        if isinstance(previous_pool, dict)
                        else "unknown"
                    ),
                    days=remaining_days_cooldown,
                )
                return (True, cooldown_notice, False)

        await self.brap_adapter.swap_from_quote(
            previous_pool,
            target_pool,
            self._get_vault_wallet_address(),
            brap_quote,
            strategy_name=self.name,
        )

        self.current_pool = target_pool
        if self.current_pool and self.current_pool.get("token_id"):
            success, pool_reports = await self.pool_adapter.get_pools_by_ids(
                pool_ids=[self.current_pool.get("token_id")]
            )
            if success and pool_reports.get("pools"):
                self.current_pool_data = pool_reports.get("pools", [])[0]
            else:
                self.current_pool_data = None
        else:
            self.current_pool_data = None
        if self.current_pool_data:
            self.current_combined_apy_pct = self.current_pool_data.get("apy", 0)
        else:
            self.current_combined_apy_pct = (
                target_pool_data.get("llama_combined_apy_pct", 0) / 100
                if target_pool_data
                else 0
            )
        output_amount = (
            brap_quote.get("output_amount")
            if brap_quote and isinstance(brap_quote, dict)
            else None
        )
        self.current_pool_balance = (
            int(output_amount) if output_amount is not None else 0
        )

        await asyncio.sleep(2)
        await self._sweep_wallet(target_pool)
        await self._refresh_current_pool_balance()

        elapsed_time = time.time() - start_time
        logger.info(
            f"Strategy update completed successfully in {elapsed_time:.2f} seconds"
        )
        return [True, "Updated successfully"]

    async def _refresh_current_pool_balance(self):
        pool = self.current_pool
        if not pool or pool.get("chain") is None:
            return

        vault_address = self._get_vault_wallet_address()
        try:
            (
                _,
                refreshed_pool_balance,
            ) = await self.balance_adapter.get_pool_balance(
                pool_address=pool.get("address"),
                chain_id=pool.get("chain").get("id"),
                user_address=vault_address,
            )
            self.current_pool_balance = int(refreshed_pool_balance)
        except Exception:
            pass

    # TODO untested
    async def _sweep_wallet(self, target_token):
        (
            _,
            wallet_balances,
        ) = await self.balance_adapter.get_all_balances(
            wallet_address=self._get_vault_wallet_address(),
            enrich=True,
            from_cache=False,
            add_llama=True,
        )
        target_chain = target_token.get("chain").get("name").lower()
        target_address = target_token.get("address").lower()

        for balance in wallet_balances.get("balances"):
            if self._is_gas_balance_entry(balance):
                continue

            balance_raw = balance.get("balance_base_units")
            token_address = balance.get("tokenAddress")
            network = balance.get("network", "").lower()

            if not balance_raw or not token_address:
                continue
            if network == target_chain and token_address.lower() == target_address:
                continue

            try:
                token_1_id = f"{network}_{token_address.lower()}"
                target_token_id = f"{target_chain}_{target_address.lower()}"

                success, msg = await self.brap_adapter.swap_from_token_ids(
                    token_1_id,
                    target_token_id,
                    self._get_vault_wallet_address(),
                    balance_raw,
                    strategy_name=self.name,
                )
                if not success:
                    return (False, f"Swap failed: {msg}")
            except Exception:
                continue

    async def _rebalance_gas(self, target_pool) -> tuple[bool, str]:
        if self.gas_token.get("chain").get("id") != target_pool.get("chain").get("id"):
            return False, "Unsupported chain for gas management."

        # TODO: do we need to categorize vault wallet addresses?
        vault_address = self._get_vault_wallet_address()

        required_gas = int(self.MIN_GAS * (10 ** self.gas_token.get("decimals")))
        _, current_gas = await self.balance_adapter.get_balance(
            token_id=self.gas_token.get("id"),
            wallet_address=vault_address,
        )
        if current_gas >= required_gas:
            return True, "Enough gas balance found."

        current_native = float(current_gas) / 10 ** self.gas_token.get("decimals")
        shortfall = max(self.MIN_GAS - current_native, 0)

        return (
            False,
            f"Vault wallet does not have enough gas. Shortfall: {shortfall} {self.gas_token.get('symbol')}",
        )

    async def _has_idle_assets(self, balances, target_token) -> bool:
        for balance in balances:
            if self._balance_matches_token(balance, target_token):
                continue
            amount = balance.get("_amount_wei")
            if isinstance(amount, int) and amount > 0:
                return True
        return False

    def _balance_matches_token(self, balance, token) -> bool:
        token_id = balance.get("token_id")
        if (
            isinstance(token_id, str)
            and token_id.lower() == token.get("token_id").lower()
        ):
            return True

        token_address = balance.get("tokenAddress")
        if not isinstance(token_address, str):
            return False

        network = (balance.get("network") or "").lower()
        chain_names = {
            getattr(token.get("chain"), "name", "").lower(),
            getattr(token.get("chain"), "code", "").lower(),
        }

        return network in chain_names and token_address.lower() == token.address.lower()

    async def _get_pool_usd_value(self, token, amount):
        chain_id = token.get("chain").get("id")
        if chain_id != self.usdc_token_info.get("chain").get("id"):
            return 0.0

        success, exit_quotes = await self.brap_adapter.get_swap_quote(
            from_token_address=token.get("address"),
            to_token_address=self.usdc_token_info.get("address"),
            from_chain_id=chain_id,
            to_chain_id=self.usdc_token_info.get("chain").get("id"),
            from_address=self._get_vault_wallet_address(),
            to_address=self._get_vault_wallet_address(),
            amount=str(amount),
        )
        if not success:
            return 0.0

        best_quote = exit_quotes.get("quotes").get("best_quote")
        current_pool_usd_value = best_quote.get("output_amount")

        return float(
            float(current_pool_usd_value) / (10 ** self.usdc_token_info.get("decimals"))
        )

    async def _get_non_gas_balances(self) -> list[dict[str, Any]]:
        results = []

        if self.current_pool != self.usdc_token_info:
            (
                status,
                balance_wei,
            ) = await self.balance_adapter.get_balance(
                token_id=self.usdc_token_info.get("token_id"),
                wallet_address=self._get_vault_wallet_address(),
            )
            if not status or not balance_wei:
                pass
            results.append(
                {
                    "token_id": self.usdc_token_info.get("token_id"),
                    "tokenAddress": self.usdc_token_info.get("address"),
                    "network": self.usdc_token_info.get("chain").get("code").upper(),
                    "_amount_wei": balance_wei,
                }
            )
        else:
            results.append(
                {
                    "token_id": self.usdc_token_info.get("token_id"),
                    "tokenAddress": self.usdc_token_info.get("address"),
                    "network": self.usdc_token_info.get("chain").get("code").upper(),
                    "_amount_wei": self.current_pool_balance
                    * (10 ** self.usdc_token_info.get("decimals")),
                }
            )

        try:
            (
                _,
                wallet_balances,
            ) = await self.balance_adapter.get_all_balances(
                wallet_address=self._get_vault_wallet_address(),
                enrich=True,
                from_cache=False,
                add_llama=True,
            )
        except Exception:
            wallet_balances = []

        for balance in wallet_balances.get("balances"):
            if self._is_gas_balance_entry(balance):
                continue

            raw = balance.get("balance_base_units")
            try:
                amount_wei = int(raw)
            except (TypeError, ValueError):
                continue
            if amount_wei <= 0:
                continue

            token_address = balance.get("tokenAddress")
            network = (balance.get("network") or "").lower()
            if not token_address or not network:
                continue

            candidate = {
                "token_id": balance.get("token_id")
                or f"{network}_{token_address.lower()}",
                "tokenAddress": token_address,
                "network": network.upper(),
                "_amount_wei": amount_wei,
            }

            exists = any(
                entry.get("token_id").lower() == candidate.get("token_id").lower()
                for entry in results
            )
            if not exists:
                results.append(candidate)

        return results

    async def _find_best_pool(self) -> tuple[bool, dict[str, Any]]:
        success, llama_data = await self.pool_adapter.get_llama_matches()
        if not success:
            return False, {"message": f"Failed to fetch Llama data: {llama_data}"}

        llama_pools = [
            pool
            for pool in llama_data.get("matches", [])
            if pool.get("llama_stablecoin")
            and pool.get("llama_il_risk") == "no"
            and pool.get("llama_tvl_usd") > self.MIN_TVL
            and pool.get("llama_apy_pct") > self.DUST_APY
            and pool.get("network", "").lower() in self.SUPPORTED_NETWORK_CODES
        ]
        llama_pools = sorted(
            llama_pools, key=lambda pool: pool.get("llama_apy_pct"), reverse=True
        )
        if not llama_pools:
            return False, {"message": "No suitable pools found."}

        for candidate in llama_pools[: self.SEARCH_DEPTH]:
            if candidate.get("address") == self.current_pool.get("address"):
                return False, {"message": "Already in the best pool, no action needed."}

            try:
                target_status, target_pool = await self.token_adapter.get_token(
                    address=candidate.get("address")
                )
                if not target_status and candidate.get("token_id"):
                    target_status, target_pool = await self.token_adapter.get_token(
                        token_id=candidate.get("token_id")
                    )
                if not target_status and candidate.get("pool_id"):
                    target_status, target_pool = await self.token_adapter.get_token(
                        token_id=candidate.get("pool_id")
                    )
                if not target_status:
                    continue
            except Exception:
                continue

            brap_quote = await self._search(
                candidate,
                self.current_pool,
                target_pool,
                self.current_combined_apy_pct,
                int(
                    self.current_pool_balance
                    * (10 ** self.current_pool.get("decimals"))
                ),
            )
            if brap_quote:
                return True, {
                    "target_pool": target_pool,
                    "target_pool_data": candidate,
                    "brap_quote": brap_quote,
                }

        return False, {"message": "No suitable pools found after searching."}

    async def _search(
        self,
        pool_data,
        current_token,
        token,
        current_combined_apy_pct,
        current_token_balance,
    ):
        if token is None or current_token is None:
            return None
        if token is None or token.get("chain") is None:
            return None
        if current_token is None or current_token.get("chain") is None:
            return None

        try:
            combined_apy_pct = pool_data.get("llama_combined_apy_pct") / 100
            success, quotes = await self.brap_adapter.get_swap_quote(
                from_token_address=current_token.get("address"),
                to_token_address=token.get("address"),
                from_chain_id=current_token.get("chain").get("id"),
                to_chain_id=token.get("chain").get("id"),
                from_address=self._get_vault_wallet_address(),
                to_address=self._get_vault_wallet_address(),
                amount=str(current_token_balance),
            )
            if not success:
                return None
            quotes_data = quotes.get("quotes") if isinstance(quotes, dict) else None
            if not isinstance(quotes_data, dict):
                return None
            best_quote = quotes_data.get("best_quote")
            if not best_quote:
                return None

            target_pool_usd_val = await self._get_pool_usd_value(
                token, best_quote.get("output_amount")
            )

            if current_token.get("token_id") != self.usdc_token_info.get("token_id"):
                current_pool_usd_val = await self._get_pool_usd_value(
                    current_token, best_quote.get("input_amount")
                )
            else:
                current_pool_usd_val = float(
                    float(self.current_pool_balance)
                    / (10 ** current_token.get("decimals"))
                )

            gas_cost = await self._get_gas_value(best_quote.get("input_amount"))
            fee_cost = (current_pool_usd_val - target_pool_usd_val) + gas_cost
            delta_combined_apy_pct = combined_apy_pct - current_combined_apy_pct

            if delta_combined_apy_pct < self.MINIMUM_APY_IMPROVEMENT:
                return None

            estimated_profit = (
                self.MINIMUM_DAYS_UNTIL_PROFIT
                * ((delta_combined_apy_pct * current_pool_usd_val) / 365)
                - fee_cost
            )

            if estimated_profit > 0:
                best_quote["from_amount_usd"] = current_pool_usd_val
                best_quote["to_amount_usd"] = target_pool_usd_val
                return best_quote

        except Exception:
            return {}

    async def _get_gas_value(self, amount):
        token = self.gas_token
        success, gas_price_data = await self.token_adapter.get_token_price(
            token.get("token_id")
        )
        if not success:
            return 0.0
        gas_price = gas_price_data.get("current_price", 0.0)
        return float(gas_price) * float(amount) / (10 ** token.get("decimals"))

    async def _status(self) -> StatusDict:
        if not self.DEPOSIT_USDC:
            (
                _,
                wallet_balances,
            ) = await self.balance_adapter.get_all_balances(
                wallet_address=self._get_main_wallet_address(),
                enrich=True,
                from_cache=False,
                add_llama=True,
            )
            total_value = self._sum_non_gas_balance_usd(wallet_balances.get("balances"))
            status_payload = {
                "info": "No recorded vault deposits; reporting current wallet holdings only.",
                "idle_usd": total_value,
            }

            return StatusDict(
                portfolio_value=total_value,
                net_deposit=0,
                strategy_status=status_payload,
            )
        (
            _,
            wallet_balances,
        ) = await self.balance_adapter.get_all_balances(
            wallet_address=self._get_vault_wallet_address(),
            enrich=True,
            from_cache=False,
            add_llama=True,
        )
        total_value = self._sum_non_gas_balance_usd(wallet_balances.get("balances"))
        status_payload = (
            {
                "current_pool": self.current_pool.get("token_id"),
                "carrying_loss": None,
                "pool_balance": self.current_pool_balance
                / (10 ** self.current_pool.get("decimals")),
                "pool_apy": f"{self.current_combined_apy_pct * 100}%",
                "pool_tvl": (
                    self.current_pool_data.get("tvl")
                    if self.current_pool_data
                    else None
                ),
            }
            if self.current_pool
            else {}
        )

        return StatusDict(
            portfolio_value=total_value,
            net_deposit=self.DEPOSIT_USDC,
            strategy_status=status_payload,
        )

    @staticmethod
    def policies() -> list[str]:
        enso_router = "0xF75584eF6673aD213a685a1B58Cc0330B8eA22Cf".lower()
        approve_enso = (
            "eth.tx.data[0..10] == '0x095ea7b3' && "
            f"eth.tx.data[34..74] == '{enso_router[2:]}'"
        )
        swap_enso = f"eth.tx.to == '{enso_router}'"
        wallet_id = "wallet.id == 'FORMAT_WALLET_ID'"
        return [f"({wallet_id}) && (({approve_enso}) || ({swap_enso})) "]

    async def partial_liquidate(self, usd_value: float) -> StatusTuple:
        (
            _,
            wallet_balances,
        ) = await self.balance_adapter.get_all_balances(
            wallet_address=self._get_vault_wallet_address(),
            enrich=True,
            from_cache=False,
            add_llama=True,
        )
        _, total_usdc_wei = await self.balance_adapter.get_balance(
            token_id=self.usdc_token_info.get("token_id"),
            wallet_address=self._get_vault_wallet_address(),
        )
        available_usdc_usd = float(total_usdc_wei or 0) / (
            10 ** self.usdc_token_info.get("decimals")
        )

        for balance in wallet_balances.get("balances"):
            if available_usdc_usd >= usd_value:
                break

            token_id = balance.get("token_id")
            if token_id == self.usdc_token_info.get("token_id"):
                continue
            if token_id == self.gas_token.get("id"):
                continue
            if self.current_pool and token_id == self.current_pool.get("token_id"):
                continue

            (
                balance_status,
                balance_wei,
            ) = await self.balance_adapter.get_balance(
                token_id=token_id,
                wallet_address=self._get_vault_wallet_address(),
            )
            if not balance_status or not balance_wei:
                continue
            price = float(balance.get("price", 0.0))
            decimals = int(balance.get("decimals", 18))
            token_usd_value = price * float(balance_wei) / (10**decimals)

            if token_usd_value > 1.0:
                needed_usd = usd_value - available_usdc_usd
                required_token_wei = int(
                    math.ceil((needed_usd * (10**decimals)) / price)
                )
                amount_to_swap = min(required_token_wei, balance_wei)
                token_address = balance.get("tokenAddress")
                network = balance.get("network", "").lower()
                token_1_id = f"{network}_{token_address.lower()}"
                try:
                    await self.brap_adapter.swap_from_token_ids(
                        token_1_id,
                        f"{self.usdc_token_info.get('chain').get('name')}_{self.usdc_token_info.get('address').lower()}",
                        self._get_vault_wallet_address(),
                        amount_to_swap,
                        strategy_name=self.name,
                    )
                    swapped_usd = (amount_to_swap / (10**decimals)) * price
                    available_usdc_usd += swapped_usd
                except Exception as e:
                    logger.error(f"Error swapping {token_address} to USDC: {e}")

        _, total_usdc_wei = await self.balance_adapter.get_balance(
            token_id=self.usdc_token_info.get("token_id"),
            wallet_address=self._get_vault_wallet_address(),
        )
        usdc_decimals = self.usdc_token_info.get("decimals")
        available_usdc_usd = float(total_usdc_wei or 0) / (10**usdc_decimals)

        if (
            available_usdc_usd < usd_value
            and self.current_pool
            and self.current_pool.get("token_id")
            != self.usdc_token_info.get("token_id")
        ):
            remaining_usd = usd_value - available_usdc_usd
            (
                _,
                pool_balance_wei,
            ) = await self.balance_adapter.get_pool_balance(
                pool_address=self.current_pool.get("address"),
                chain_id=self.current_pool.get("chain").get("id"),
                user_address=self._get_vault_wallet_address(),
            )
            pool_decimals = self.current_pool.get("decimals")
            amount_to_swap = min(
                int(pool_balance_wei or 0), int(remaining_usd * (10**pool_decimals))
            )

            try:
                await self.brap_adapter.swap_from_token_ids(
                    f"{self.current_pool.get('chain').get('code').lower()}_{self.current_pool.get('address').lower()}",
                    f"{self.usdc_token_info.get('chain').get('name')}_{self.usdc_token_info.get('address').lower()}",
                    self._get_vault_wallet_address(),
                    amount_to_swap,
                    strategy_name=self.name,
                )
            except Exception as e:
                logger.error(f"Error swapping pool to USDC: {e}")

            _, total_usdc_wei = await self.balance_adapter.get_balance(
                token_id=self.usdc_token_info.get("token_id"),
                wallet_address=self._get_vault_wallet_address(),
            )
        to_pay = min(int(total_usdc_wei or 0), int(usd_value * (10**usdc_decimals)))
        return (True, f"Partial liquidation completed. Paid {to_pay} USDC")
