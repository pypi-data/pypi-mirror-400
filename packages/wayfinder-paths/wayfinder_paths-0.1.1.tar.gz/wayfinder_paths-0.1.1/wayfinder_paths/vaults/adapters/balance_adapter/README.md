# Balance Adapter

Adapter that exposes wallet, token, and pool balances backed by `WalletClient`/`TokenClient` and now orchestrates transfers between the configured main/vault wallets (with ledger bookkeeping).

- Entrypoint: `vaults.adapters.balance_adapter.adapter.BalanceAdapter`
- Manifest: `manifest.yaml`
- Tests: `test_adapter.py`

## Capabilities

The adapter declares both `wallet_read` and `wallet_transfer` capabilities in its manifest. Transfers are executed by leveraging the shared `DefaultWeb3Service.token_transactions` helper, but ledger recording + wallet selection now live inside the adapter.

## Construction

```python
from wayfinder_paths.core.services.web3_service import DefaultWeb3Service
from wayfinder_paths.vaults.adapters.balance_adapter.adapter import BalanceAdapter

web3_service = DefaultWeb3Service(config)
balance = BalanceAdapter(config, web3_service=web3_service)
```

`web3_service` is required so the adapter can share the same wallet provider (and `TokenTxn` helper) as the rest of the strategy.

## API surface

### `get_balance(token_id: str, wallet_address: str)`
Returns the raw balance (as an integer) for a specific token on a wallet.

```python
success, balance = await balance.get_balance(
    token_id="usd-coin-base",
    wallet_address=config["main_wallet"]["address"],
)
```

### `get_pool_balance(pool_address: str, chain_id: int, user_address: str)`
Fetches the amount supplied to a specific pool, using the `/wallets/pool-balance` endpoint.

```python
success, amount = await balance.get_pool_balance(
    pool_address="0xPool",
    chain_id=8453,
    user_address=config["vault_wallet"]["address"],
)
```

### `get_all_balances(wallet_address: str, enrich=True, from_cache=False, add_llama=True)`
Returns the enriched token balance payload Wayfinder exposes (including USD value, metadata, and optional DeFi Llama overlays).

```python
success, snapshot = await balance.get_all_balances(
    wallet_address=config["vault_wallet"]["address"],
    enrich=True,
)
```

### `move_from_main_wallet_to_vault_wallet(token_id: str, amount: float, strategy_name="unknown", skip_ledger=False)`
Sends the specified token from the configured `main_wallet` to the `vault_wallet`, records the ledger deposit (unless `skip_ledger=True`), and returns the `(success, tx_result)` tuple from the underlying send helper.

```python
success, tx = await balance.move_from_main_wallet_to_vault_wallet(
    token_id="usd-coin-base",
    amount=1.5,
    strategy_name="MyStrategy",
)
```

### `move_from_vault_wallet_to_main_wallet(token_id: str, amount: float, strategy_name="unknown", skip_ledger=False)`
Mirrors the previous method but withdraws from the vault wallet back to the main wallet while recording a ledger withdrawal entry.

```python
await balance.move_from_vault_wallet_to_main_wallet(
    token_id="usd-coin-base",
    amount=0.75,
    strategy_name="MyStrategy",
)
```

All methods return `(success: bool, payload: Any)` tuples. On failure the payload is an error string.

## Usage inside strategies

```python
class MyStrategy(Strategy):
    def __init__(self, config):
        super().__init__()
        web3_service = DefaultWeb3Service(config)
        balance_adapter = BalanceAdapter(config, web3_service=web3_service)
        self.register_adapters([balance_adapter])
        self.balance_adapter = balance_adapter

    async def _status(self):
        success, pool_balance = await self.balance_adapter.get_pool_balance(
            pool_address=self.current_pool["address"],
            chain_id=self.current_pool["chain"]["id"],
            user_address=self.config["vault_wallet"]["address"],
        )
        return {"portfolio_value": float(pool_balance or 0), ...}
```

## Error handling and health checks

Any exception raised by the underlying `WalletClient`/`TokenClient` is caught and emitted as a `(False, "message")` tuple. The inherited `health_check()` method reports adapter status plus dependency status, making it safe to call from `Strategy.health_check`.
