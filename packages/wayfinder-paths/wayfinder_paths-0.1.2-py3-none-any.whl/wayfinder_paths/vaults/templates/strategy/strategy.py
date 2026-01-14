from wayfinder_paths.core.strategies.Strategy import StatusDict, StatusTuple, Strategy


class MyStrategy(Strategy):
    name = "My Strategy"
    description = "Short description of what the strategy does."
    summary = "One-line summary for discovery."

    def __init__(self):
        super().__init__()

    async def setup(self):
        """Optional initialization logic."""
        return None

    async def deposit(
        self, main_token_amount: float, gas_token_amount: float
    ) -> StatusTuple:
        """Deposit funds into the strategy.

        Args:
            main_token_amount: Amount of the main token to deposit (e.g., USDC, USDT0)
            gas_token_amount: Amount of gas token to deposit (e.g., ETH, HYPE)
        """
        return (True, "Deposit successful")

    async def withdraw(self, amount: float | None = None) -> StatusTuple:
        """Withdraw funds from the strategy.

        This method is required. The base Strategy class provides a default
        implementation that unwinds all ledger operations. You can either:
        1. Call the parent implementation (as shown here, recommended for most cases)
        2. Override this method for custom withdrawal logic (e.g., unwinding specific positions,
           converting tokens, handling partial withdrawals)

        Args:
            amount: Optional amount to withdraw. If None, withdraws all funds.
        """
        # Call parent implementation which unwinds all ledger operations
        return await super().withdraw(amount=amount)

    async def update(self) -> StatusTuple:
        """Rebalance or update positions."""
        return (True, "Update successful")

    async def _status(self) -> StatusDict:
        """Report strategy status."""
        return {
            "portfolio_value": 0.0,
            "net_deposit": 0.0,
            "strategy_status": {},
        }

    @staticmethod
    def policies() -> list[str]:
        """Return policy strings used to scope on-chain permissions."""
        return []
