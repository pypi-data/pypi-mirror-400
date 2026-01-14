# Token Adapter

A Wayfinder adapter that wraps the `_get_token_via_api` method for fetching token data via HeadlessAPIViewSet endpoints. This adapter supports both address and token_id lookups.

## Capabilities

- `token.read`: Retrieve token information by address or token ID

## Configuration

The adapter uses the TokenClient which automatically handles authentication and API configuration through the Wayfinder settings. No additional configuration is required.

The TokenClient will automatically:
- Use the WAYFINDER_API_URL from settings
- Handle authentication via environment variables or config.json
- Manage token refresh and retry logic

## Usage

### Initialize the Adapter

```python
from wayfinder_paths.vaults.adapters.token_adapter.adapter import TokenAdapter

# No configuration needed - uses TokenClient with automatic settings
adapter = TokenAdapter()
```

### Get Token Metadata

Both contract addresses and token ids are supported with the same method. Pass whichever identifier you have:

```python
success, data = await adapter.get_token("0x1234...")        # by address
# or
success, data = await adapter.get_token("usd-coin-base")    # by token id

if success:
    print(data)
else:
    print(f"Error: {data}")
```

### Get Token Price

```python
success, data = await adapter.get_token_price("token-123")
if success:
    print(f"Price: ${data['current_price']}")
    print(f"24h Change: {data['price_change_percentage_24h']}%")
else:
    print(f"Error: {data}")
```

### Get Gas Token

```python
success, data = await adapter.get_gas_token("base")
if success:
    print(f"Gas token: {data['symbol']} - {data['name']}")
    print(f"Address: {data['address']}")
else:
    print(f"Error: {data}")
```

### Get Token (Flexible)

```python
# Try by address first, then by token_id
success, data = await adapter.get_token(address="0x1234...", token_id="token-123")
if success:
    print(f"Token data: {data}")
else:
    print(f"Error: {data}")
```

## API Endpoints

The adapter uses the following existing public API endpoints:

1. **Token Details** (by address): `GET /public/tokens/detail/?query={address}&get_chart=false`
2. **Token by ID**: `GET /public/tokens/lookup/?token_id={token_id}`

## Error Handling

All methods return a tuple of `(success: bool, data: Any)` where:
- `success` indicates whether the operation was successful
- `data` contains either the token information (on success) or an error message (on failure)

## Health Check

The adapter includes a health check that tests connectivity to the API:

```python
health = await adapter.health_check()
print(f"Status: {health['status']}")
```

## Examples

See `examples.json` for more detailed usage examples.
