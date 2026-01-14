import os
import traceback
from abc import ABC, abstractmethod
from typing import Any, TypedDict

from loguru import logger

from wayfinder_paths.core.services.base import Web3Service


class StatusDict(TypedDict):
    portfolio_value: float
    net_deposit: float
    strategy_status: Any


StatusTuple = tuple[bool, str]


class Strategy(ABC):
    name: str = None
    description: str = None
    summary: str = None

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        *,
        main_wallet: dict[str, Any] | None = None,
        vault_wallet: dict[str, Any] | None = None,
        simulation: bool = False,
        web3_service: Web3Service = None,
        api_key: str | None = None,
    ):
        self.adapters = {}
        self.ledger = None
        self.logger = logger.bind(strategy=self.__class__.__name__)
        if api_key:
            os.environ["WAYFINDER_API_KEY"] = api_key

    async def setup(self):
        """Initialize strategy-specific setup after construction"""
        pass

    async def log(self, msg: str) -> None:
        """Log messages - can be overridden by subclasses"""
        self.logger.info(msg)

    async def temp_ui_message(self, msg: str) -> None:
        """Hook for temporary UI messages (e.g., progress) to the chat window."""
        # No-op by default; strategies/hosts can override
        return None

    async def quote(self):
        """Get quotes for potential trades - optional for strategies"""
        pass

    @abstractmethod
    async def deposit(self, **kwargs) -> StatusTuple:
        """
        Deposit funds into the strategy
        Returns: (success: bool, message: str)
        """
        pass

    async def withdraw(self, **kwargs) -> StatusTuple:
        """
        Withdraw funds from the strategy
        Default implementation unwinds all operations
        Returns: (success: bool, message: str)
        """
        if hasattr(self, "ledger") and self.ledger:
            while self.ledger.positions.operations:
                node = self.ledger.positions.operations[-1]
                adapter = self.adapters.get(node.adapter)
                if adapter and hasattr(adapter, "unwind_op"):
                    await adapter.unwind_op(node)
                self.ledger.positions.operations.pop()

            await self.ledger.save()

        return (True, "Withdrawal complete")

    @abstractmethod
    async def update(self) -> StatusTuple:
        """
        Update strategy positions/rebalance
        Returns: (success: bool, message: str)
        """
        pass

    @staticmethod
    def policies() -> list[str]:
        """Return policy strings for this strategy (Django-compatible)."""
        raise NotImplementedError

    @abstractmethod
    async def _status(self) -> StatusDict:
        """
        Return status payload. Subclasses should implement this.
        Should include Django-compatible keys (portfolio_value, net_deposit, strategy_status).
        Backward-compatible keys (active_amount, total_earned) may also be included.
        """
        pass

    async def status(self) -> StatusDict:
        """
        Wrapper to compute and return strategy status. In Django, this also snapshots.
        Here we simply delegate to _status for compatibility.
        """
        return await self._status()

    def register_adapters(self, adapters: list[Any]) -> None:
        """Register adapters for use by the strategy"""
        self.adapters = {}
        for adapter in adapters:
            if hasattr(adapter, "adapter_type"):
                self.adapters[adapter.adapter_type] = adapter
            elif hasattr(adapter, "__class__"):
                self.adapters[adapter.__class__.__name__] = adapter

    def unwind_on_error(self, func):
        """
        Decorator to unwind operations on error
        Useful for deposit operations that need cleanup on failure
        """

        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception:
                trace = traceback.format_exc()
                try:
                    await self.withdraw()
                    return (
                        False,
                        f"Strategy failed during operation and was unwound. Failure: {trace}",
                    )
                except Exception:
                    trace2 = traceback.format_exc()
                    return (
                        False,
                        f"Strategy failed and unwinding also failed. Operation error: {trace}. Unwind error: {trace2}",
                    )
            finally:
                if hasattr(self, "ledger") and self.ledger:
                    await self.ledger.save()

        return wrapper

    @classmethod
    def get_metadata(cls) -> dict[str, Any]:
        """
        Return metadata about this strategy
        Can be overridden to provide discovery information
        """
        return {
            "name": cls.name,
            "description": cls.description,
            "summary": cls.summary,
        }

    async def health_check(self) -> dict[str, Any]:
        """
        Check strategy health and dependencies
        """
        health = {"status": "healthy", "strategy": self.name, "adapters": {}}

        for name, adapter in self.adapters.items():
            if hasattr(adapter, "health_check"):
                health["adapters"][name] = await adapter.health_check()
            else:
                health["adapters"][name] = {"status": "unknown"}

        return health

    async def partial_liquidate(self, usd_value: float) -> StatusTuple:
        """
        Partially liquidate strategy positions by USD value
        Optional method that can be overridden by subclasses
        Returns: (success: bool, message: str)
        """
        return (False, "Partial liquidation not implemented for this strategy")
