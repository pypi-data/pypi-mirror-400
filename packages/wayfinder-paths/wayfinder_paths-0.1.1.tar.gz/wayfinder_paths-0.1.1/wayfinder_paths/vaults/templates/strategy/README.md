# Strategy Template

This template provides the scaffolding for a new vault strategy. It mirrors the structure in `wayfinder_paths/vaults/strategies/...` and wires into the runner via a manifest.

## Quick Start

1. Copy the template to a new folder:
   ```
   cp -r wayfinder_paths/vaults/templates/strategy wayfinder_paths/vaults/strategies/my_strategy
   ```
2. Rename the class in `strategy.py` and update `manifest.yaml` so `entrypoint` points to your new module (for example `vaults.strategies.my_strategy.strategy.MyStrategy`).
3. Fill out `examples.json` with sample CLI invocations and `test_strategy.py` with at least one smoke test.
4. Implement the required strategy methods (`deposit`, `update`, `_status`, optionally override `withdraw`).

## Layout

```
my_strategy/
├── strategy.py          # Strategy implementation
├── manifest.yaml        # Entrypoint + adapter requirements + policy
├── examples.json        # Example CLI payloads
├── test_strategy.py     # Pytest-based smoke tests
└── README.md            # Strategy-specific documentation
```

## Required methods

```python
async def deposit(self, main_token_amount: float, gas_token_amount: float) -> StatusTuple:
    """Move funds from the main wallet into the vault wallet and prepare on-chain positions."""

async def update(self) -> StatusTuple:
    """Periodic rebalance/update loop."""

async def _status(self) -> StatusDict:
    """Return portfolio_value, net_deposit, and strategy_status payloads."""
```

`Strategy.withdraw` already unwinds ledger operations. Override it only if you need custom exit logic.

## Wiring adapters

Strategies typically:

1. Build a `DefaultWeb3Service` so every adapter shares a wallet provider.
2. Instantiate adapters (balance, ledger, protocol specific, etc.).
3. Register adapters via `self.register_adapters([...])` and keep references as attributes.

```python
from wayfinder_paths.core.services.web3_service import DefaultWeb3Service
from wayfinder_paths.core.strategies.Strategy import StatusDict, StatusTuple, Strategy
from wayfinder_paths.vaults.adapters.balance_adapter.adapter import BalanceAdapter


class MyStrategy(Strategy):
    name = "Demo Strategy"

    def __init__(self, config: dict | None = None):
        super().__init__()
        self.config = config or {}
        web3_service = DefaultWeb3Service(self.config)
        balance_adapter = BalanceAdapter(self.config, web3_service=web3_service)
        self.register_adapters([balance_adapter])
        self.balance_adapter = balance_adapter

    async def deposit(
        self, main_token_amount: float = 0.0, gas_token_amount: float = 0.0
    ) -> StatusTuple:
        """Perform validation, move funds, and optionally deploy capital."""
        if main_token_amount <= 0:
            return (False, "Nothing to deposit")

        success, _ = await self.balance_adapter.get_balance(
            token_id=self.config.get("token_id"),
            wallet_address=self.config.get("main_wallet", {}).get("address"),
        )
        if not success:
            return (False, "Unable to fetch balances")

        # Use BalanceAdapter (which leverages LocalTokenTxnService builders) for transfers.
        self.last_deposit = main_token_amount
        return (True, f"Deposited {main_token_amount} tokens")

    async def update(self) -> StatusTuple:
        """Execute your strategy logic periodically."""
        return (True, "No-op update")

    async def _status(self) -> StatusDict:
        """Surface state back to run_strategy.py."""
        success, balance = await self.balance_adapter.get_balance(
            token_id=self.config.get("token_id"),
            wallet_address=self.config.get("vault_wallet", {}).get("address"),
        )
        return {
            "portfolio_value": float(balance or 0),
            "net_deposit": float(getattr(self, "last_deposit", 0.0)),
            "strategy_status": {"message": "healthy" if success else "unknown"},
        }
```

## Manifest configuration

Your `manifest.yaml` should define:

```yaml
schema_version: "0.1"
entrypoint: "vaults.strategies.my_strategy.strategy.MyStrategy"
permissions:
  policy: "(wallet.id == 'FORMAT_WALLET_ID') && (eth.tx.to == '0x...')"
adapters:
  - name: "BALANCE"
    capabilities: ["wallet_read", "wallet_transfer"]
  - name: "POOL"
    capabilities: ["pool.read", "pool.analytics"]
```

## Testing

`test_strategy.py` should cover at least deposit/update/status. Use `pytest.mark.asyncio` and patch adapters or services as needed.

```python
import pytest
from wayfinder_paths.vaults.strategies.my_strategy.strategy import MyStrategy


@pytest.mark.asyncio
async def test_status_shape():
    strat = MyStrategy(config={})
    status = await strat._status()
    assert set(status) == {"portfolio_value", "net_deposit", "strategy_status"}
```

## Running the strategy locally

```bash
# Install dependencies & create wallets first
poetry install
poetry run python wayfinder_paths/scripts/make_wallets.py --default --vault

# Copy config and edit credentials
cp wayfinder_paths/config.example.json config.json

# Run your strategy
poetry run python wayfinder_paths/run_strategy.py my_strategy --action status --config $(pwd)/config.json
```

## Best practices

- Return `(success: bool, message: str)` tuples from `deposit`/`update`.
- Always populate `portfolio_value`, `net_deposit`, and `strategy_status` keys in `_status`.
- Use the adapters declared in `manifest.yaml`—they are injected via `register_adapters`.
- Keep on-chain permissions tight by scoping the manifest policy to the strategy wallet and expected contracts.
