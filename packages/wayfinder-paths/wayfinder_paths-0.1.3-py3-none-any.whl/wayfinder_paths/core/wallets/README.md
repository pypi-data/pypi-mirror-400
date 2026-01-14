# Wallet Abstraction Layer

Wayfinder strategies interact with blockchains through a single abstraction: the `EvmTxn` interface defined in `wayfinder_paths/core/services/base.py`. The default implementation (`LocalEvmTxn`) signs transactions with private keys pulled from config/environment variables, while `WalletManager` resolves which provider to use at runtime.

## Pieces

1. **`EvmTxn` (interface)** – describes balance lookups, ERC-20 approvals, raw transaction broadcasting, and AsyncWeb3 access.
2. **`LocalEvmTxn`** – the built-in provider that signs transactions locally via `eth_account`. It handles RPC resolution, nonce management, gas estimation, and status checks.
3. **`WalletManager`** – light factory that reads `wallet_type` from strategy config and returns the appropriate `EvmTxn`. Today it always returns `LocalEvmTxn` unless you inject your own provider.
4. **`DefaultWeb3Service`** – convenience wrapper that bundles an `EvmTxn` (wallet provider) with a `LocalTokenTxnService` (transaction builders used by adapters).

## Using the defaults

```python
from wayfinder_paths.core.services.web3_service import DefaultWeb3Service
from wayfinder_paths.core.wallets.WalletManager import WalletManager

config = {...}  # contains main_wallet / vault_wallet entries
wallet_provider = WalletManager.get_provider(config)
web3_service = DefaultWeb3Service(config, wallet_provider=wallet_provider)

# Strategies typically pass web3_service.evm_transactions into adapters that require wallet access.
balance_adapter = BalanceAdapter(config, web3_service=web3_service)
```

If you want to provide a custom wallet provider (e.g., Privy, Turnkey, Fireblocks), implement the `EvmTxn` interface and hand it to `DefaultWeb3Service`/adapters directly—`WalletManager` is purely a helper.

## Implementing a custom provider

Subclass `EvmTxn` and implement every abstract method:

```python
from typing import Any
from web3 import AsyncWeb3

from wayfinder_paths.core.services.base import EvmTxn


class PrivyWallet(EvmTxn):
    def __init__(self, privy_client):
        self._client = privy_client

    async def get_balance(self, address: str, token_address: str | None, chain_id: int) -> tuple[bool, Any]:
        ...

    async def read_erc20_allowance(self, chain_id: int, token_address: str, owner_address: str, spender_address: str) -> tuple[bool, Any]:
        ...

    async def approve_token(...):
        ...

    async def broadcast_transaction(...):
        ...

    async def transaction_succeeded(self, tx_hash: str, chain_id: int, timeout: int = 120) -> bool:
        ...

    def get_web3(self, chain_id: int) -> AsyncWeb3:
        ...
```

Methods should mirror `LocalEvmTxn`’s behavior: return `(True, payload)` on success, `(False, "reason")` on failure, and expose AsyncWeb3 instances tied to the requested chain.

Once implemented:

```python
custom_wallet = PrivyWallet(privy_client)
web3_service = DefaultWeb3Service(config, wallet_provider=custom_wallet)
```

## Configuration hints

`WalletManager.get_provider` looks for `wallet_type` on the top-level config, `main_wallet`, and `vault_wallet`. Example:

```json
{
  "strategy": {
    "wallet_type": "local",
    "main_wallet": {"address": "0x...", "wallet_type": "local"},
    "vault_wallet": {"address": "0x..."}
  }
}
```

Currently only `"local"` is supported through configuration—the custom path is injection.

## Why this layer?

- Strategies never touch raw `AsyncWeb3`; they call adapters, which call clients, which call a wallet provider.
- Alternate signing backends can be plugged in without modifying strategy code.
- Tests can patch `WalletManager.get_provider` or inject stub `EvmTxn` implementations to avoid real RPC calls.
