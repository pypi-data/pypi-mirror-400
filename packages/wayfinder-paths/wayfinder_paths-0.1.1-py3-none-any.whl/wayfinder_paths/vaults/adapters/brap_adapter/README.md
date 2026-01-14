# BRAP Adapter

A Wayfinder adapter that provides high-level operations for cross-chain swaps and quotes via the BRAP (Bridge/Router/Adapter Protocol). This adapter wraps the `BRAPClient` to offer strategy-friendly methods for getting quotes, comparing routes, and executing cross-chain transactions.

## Capabilities

- `swap.quote`: Get quotes for cross-chain swap operations
- `swap.execute`: Execute cross-chain swaps
- `bridge.quote`: Get quotes for bridge operations
- `bridge.execute`: Execute bridge operations
- `route.optimize`: Compare and optimize routes
- `fee.calculate`: Calculate fees and costs

## Configuration

The adapter uses the BRAPClient which automatically handles authentication and API configuration through the Wayfinder settings. Pass a `Web3Service` instance so it can broadcast transactions and reuse the shared `LocalTokenTxnService` for approvals.

The BRAPClient will automatically:
- Use the WAYFINDER_API_URL from settings
- Handle authentication via environment variables or config.json
- Manage token refresh and retry logic

## Usage

### Initialize the Adapter

```python
from wayfinder_paths.core.services.web3_service import DefaultWeb3Service
from wayfinder_paths.vaults.adapters.brap_adapter.adapter import BRAPAdapter

web3_service = DefaultWeb3Service(config)
adapter = BRAPAdapter(web3_service=web3_service)
```

### Get Swap Quote

```python
success, data = await adapter.get_swap_quote(
    from_token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
    to_token_address="0xB1c97a44F7552d9Dd5e5e5e5e5e5e5e5e5e5e5e5e5e",
    from_chain_id=8453,  # Base
    to_chain_id=1,       # Ethereum
    from_address="0x1234567890123456789012345678901234567890",
    to_address="0x1234567890123456789012345678901234567890",
    amount="1000000000000000000",  # 1 token (18 decimals)
    slippage=0.01  # 1% slippage
)
if success:
    quotes = data.get("quotes", {})
    best_quote = quotes.get("best_quote", {})
    print(f"Output amount: {best_quote.get('output_amount')}")
    print(f"Total fee: {best_quote.get('total_fee')}")
else:
    print(f"Error: {data}")
```

### Get Best Quote

```python
success, data = await adapter.get_best_quote(
    from_token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
    to_token_address="0xB1c97a44F7552d9Dd5e5e5e5e5e5e5e5e5e5e5e5e5e",
    from_chain_id=8453,
    to_chain_id=1,
    from_address="0x1234567890123456789012345678901234567890",
    to_address="0x1234567890123456789012345678901234567890",
    amount="1000000000000000000"
)
if success:
    print(f"Best output: {data.get('output_amount')}")
    print(f"Gas fee: {data.get('gas_fee')}")
    print(f"Bridge fee: {data.get('bridge_fee')}")
else:
    print(f"Error: {data}")
```

### Calculate Swap Fees

```python
success, data = await adapter.calculate_swap_fees(
    from_token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
    to_token_address="0xB1c97a44F7552d9Dd5e5e5e5e5e5e5e5e5e5e5e5e5e",
    from_chain_id=8453,
    to_chain_id=1,
    amount="1000000000000000000",
    slippage=0.01
)
if success:
    print(f"Input amount: {data.get('input_amount')}")
    print(f"Output amount: {data.get('output_amount')}")
    print(f"Gas fee: {data.get('gas_fee')}")
    print(f"Bridge fee: {data.get('bridge_fee')}")
    print(f"Protocol fee: {data.get('protocol_fee')}")
    print(f"Total fee: {data.get('total_fee')}")
    print(f"Price impact: {data.get('price_impact')}")
else:
    print(f"Error: {data}")
```

### Compare Routes

```python
success, data = await adapter.compare_routes(
    from_token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
    to_token_address="0xB1c97a44F7552d9Dd5e5e5e5e5e5e5e5e5e5e5e5e5e",
    from_chain_id=8453,
    to_chain_id=1,
    amount="1000000000000000000"
)
if success:
    print(f"Total routes available: {data.get('total_routes')}")
    print(f"Best route output: {data.get('best_route', {}).get('output_amount')}")
    
    for i, route in enumerate(data.get('all_routes', [])):
        print(f"Route {i+1}: Output {route.get('output_amount')}, Fee {route.get('total_fee')}")
else:
    print(f"Error: {data}")
```

### Estimate Gas Costs

```python
success, data = await adapter.estimate_gas_cost(
    from_chain_id=8453,  # Base
    to_chain_id=1,       # Ethereum
    operation_type="swap"
)
if success:
    print(f"From chain: {data.get('from_chain')}")
    print(f"To chain: {data.get('to_chain')}")
    print(f"From gas estimate: {data.get('from_gas_estimate')}")
    print(f"To gas estimate: {data.get('to_gas_estimate')}")
    print(f"Total operations: {data.get('total_operations')}")
else:
    print(f"Error: {data}")
```

### Validate Swap Parameters

```python
success, data = await adapter.validate_swap_parameters(
    from_token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
    to_token_address="0xB1c97a44F7552d9Dd5e5e5e5e5e5e5e5e5e5e5e5e5e",
    from_chain_id=8453,
    to_chain_id=1,
    amount="1000000000000000000"
)
if success:
    if data.get("valid"):
        print("Parameters are valid")
        print(f"Estimated output: {data.get('estimated_output')}")
    else:
        print("Parameters are invalid:")
        for error in data.get("errors", []):
            print(f"  - {error}")
else:
    print(f"Error: {data}")
```

### Get Bridge Quote

```python
# Bridge operations use the same interface as swaps
success, data = await adapter.get_bridge_quote(
    from_token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
    to_token_address="0xB1c97a44F7552d9Dd5e5e5e5e5e5e5e5e5e5e5e5e5e",
    from_chain_id=8453,
    to_chain_id=1,
    amount="1000000000000000000",
    slippage=0.01
)
if success:
    print(f"Bridge quote received: {data.get('quotes', {}).get('best_quote', {}).get('output_amount')}")
else:
    print(f"Error: {data}")
```

## Advanced Usage

### Route Optimization

```python
# Compare multiple routes to find the best option
success, data = await adapter.compare_routes(
    from_token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
    to_token_address="0xB1c97a44F7552d9Dd5e5e5e5e5e5e5e5e5e5e5e5e5e",
    from_chain_id=8453,
    to_chain_id=1,
    amount="1000000000000000000"
)

if success:
    analysis = data.get("route_analysis", {})
    highest_output = analysis.get("highest_output")
    lowest_fees = analysis.get("lowest_fees")
    fastest = analysis.get("fastest")
    
    print(f"Highest output route: {highest_output.get('output_amount')}")
    print(f"Lowest fees route: {lowest_fees.get('total_fee')}")
    print(f"Fastest route: {fastest.get('estimated_time')} seconds")
```

### Fee Analysis

```python
# Analyze fees for a swap operation
success, data = await adapter.calculate_swap_fees(
    from_token_address="0xA0b86a33E6441c8C06DdD4D4c4c4c4c4c4c4c4c4c",
    to_token_address="0xB1c97a44F7552d9Dd5e5e5e5e5e5e5e5e5e5e5e5e5e",
    from_chain_id=8453,
    to_chain_id=1,
    amount="1000000000000000000"
)

if success:
    input_amount = int(data.get("input_amount", 0))
    output_amount = int(data.get("output_amount", 0))
    total_fee = int(data.get("total_fee", 0))
    
    # Calculate effective rate
    effective_rate = (input_amount - output_amount) / input_amount
    print(f"Effective rate: {effective_rate:.4f} ({effective_rate * 100:.2f}%)")
    print(f"Total fees: {total_fee / 1e18:.6f} tokens")
```

## API Endpoints

The adapter uses the following Wayfinder API endpoints:

- `POST /api/v1/public/quotes/` - Get swap/bridge quotes

## Error Handling

All methods return a tuple of `(success: bool, data: Any)` where:
- `success` is `True` if the operation succeeded
- `data` contains the response data on success or error message on failure

## Testing

Run the adapter tests:

```bash
pytest wayfinder_paths/vaults/adapters/brap_adapter/test_adapter.py -v
```

## Dependencies

- `BRAPClient` - Low-level API client for BRAP operations
- `BaseAdapter` - Base adapter class with common functionality
