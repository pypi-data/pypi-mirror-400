# Ledger Adapter

A Wayfinder adapter that provides high-level operations for vault transaction history and bookkeeping. This adapter wraps the `LedgerClient` to offer strategy-friendly methods for recording and retrieving vault operations.

## Capabilities

- `ledger.read`: Read vault transaction data and net deposits
- `ledger.write`: Record deposits, withdrawals, and operations
- `vault.transactions`: Access vault transaction history
- `vault.deposits`: Record deposit transactions
- `vault.withdrawals`: Record withdrawal transactions
- `vault.operations`: Record vault operations (swaps, rebalances, etc.)

## Configuration

The adapter uses the LedgerClient which automatically handles authentication and API configuration through the Wayfinder settings. No additional configuration is required.

The LedgerClient will automatically:
- Use the WAYFINDER_API_URL from settings
- Handle authentication via environment variables or config.json
- Manage token refresh and retry logic

## Usage

### Initialize the Adapter

```python
from wayfinder_paths.vaults.adapters.ledger_adapter.adapter import LedgerAdapter

# No configuration needed - uses LedgerClient with automatic settings
adapter = LedgerAdapter()
```

### Get Vault Transaction History

```python
success, data = await adapter.get_vault_transactions(
    wallet_address="0x1234567890123456789012345678901234567890",
    limit=10,
    offset=0
)
if success:
    transactions = data.get("transactions", [])
    print(f"Found {len(transactions)} transactions")
else:
    print(f"Error: {data}")
```

### Get Net Deposit Amount

```python
success, data = await adapter.get_vault_net_deposit(
    wallet_address="0x1234567890123456789012345678901234567890"
)
if success:
    net_deposit = data.get("net_deposit", 0)
    print(f"Net deposit: {net_deposit} USDC")
else:
    print(f"Error: {data}")
```

### Record a Deposit

```python
success, data = await adapter.record_deposit(
    wallet_address="0x1234567890123456789012345678901234567890",
    chain_id=8453,
    token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
    token_amount="1000000000000000000",
    usd_value="1000.00",
    strategy_name="StablecoinYieldStrategy"
)
if success:
    print(f"Deposit recorded: {data.get('transaction_id')}")
else:
    print(f"Error: {data}")
```

### Record a Withdrawal

```python
success, data = await adapter.record_withdrawal(
    wallet_address="0x1234567890123456789012345678901234567890",
    chain_id=8453,
    token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
    token_amount="500000000000000000",
    usd_value="500.00",
    strategy_name="StablecoinYieldStrategy"
)
if success:
    print(f"Withdrawal recorded: {data.get('transaction_id')}")
else:
    print(f"Error: {data}")
```

### Record an Operation or Cashflow

```python
success, op = await adapter.record_operation(
    wallet_address=vault_address,
    operation_data={
        "type": "SWAP",
        "from_token": "...",
        "to_token": "...",
        "amount_in": "1000000000000000000",
        "amount_out": "995000000000000000",
    },
    usd_value="1000.00",
    strategy_name="StablecoinYieldStrategy",
)

success, cashflow = await adapter.record_cashflow(
    wallet_address=vault_address,
    block_timestamp=int(time.time()),
    token_addr="0x...",
    amount="250000000000000000",
    description="reward",
    strategy_name="StablecoinYieldStrategy",
)
```

### Latest Transactions and Summaries

```python
success, latest = await adapter.get_vault_latest_transactions(wallet_address=vault_address)
success, summary = await adapter.get_transaction_summary(wallet_address=vault_address, limit=5)
if success:
    print(f"Total transactions: {summary.get('total_transactions')}")
```

## API Endpoints

The adapter uses the following Wayfinder API endpoints:

- `GET /api/v1/public/vaults/transactions/` - Get vault transactions
- `GET /api/v1/public/vaults/net-deposit/` - Get net deposit amount
- `POST /api/v1/public/vaults/deposits/` - Record a deposit
- `POST /api/v1/public/vaults/withdrawals/` - Record a withdrawal
- `POST /api/v1/public/vaults/operations/` - Record an operation

## Error Handling

All methods return a tuple of `(success: bool, data: Any)` where:
- `success` is `True` if the operation succeeded
- `data` contains the response data on success or error message on failure

## Testing

Run the adapter tests:

```bash
pytest wayfinder_paths/vaults/adapters/ledger_adapter/test_adapter.py -v
```

## Dependencies

- `LedgerClient` - Low-level API client for ledger operations
- `BaseAdapter` - Base adapter class with common functionality
