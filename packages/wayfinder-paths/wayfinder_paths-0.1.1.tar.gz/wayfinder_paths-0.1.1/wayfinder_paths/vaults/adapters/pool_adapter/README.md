# Pool Adapter

A Wayfinder adapter that provides high-level operations for DeFi pool data and analytics. This adapter wraps the `PoolClient` to offer strategy-friendly methods for discovering, analyzing, and filtering yield opportunities.

## Capabilities

- `pool.read`: Read pool information and metadata
- `pool.analytics`: Get comprehensive pool analytics
- `pool.discovery`: Find and search pools
- `llama.data`: Access Llama protocol data
- `pool.reports`: Get pool reports and analytics

## Configuration

The adapter uses the PoolClient which automatically handles authentication and API configuration through the Wayfinder settings. No additional configuration is required.

The PoolClient will automatically:
- Use the WAYFINDER_API_URL from settings
- Handle authentication via environment variables or config.json
- Manage token refresh and retry logic

## Usage

### Initialize the Adapter

```python
from wayfinder_paths.vaults.adapters.pool_adapter.adapter import PoolAdapter

# No configuration needed - uses PoolClient with automatic settings
adapter = PoolAdapter()
```

### Get Pools by IDs

```python
success, data = await adapter.get_pools_by_ids(
    pool_ids=["pool-123", "pool-456"],
    merge_external=True
)
if success:
    pools = data.get("pools", [])
    print(f"Found {len(pools)} pools")
else:
    print(f"Error: {data}")
```

### Get All Pools

```python
success, data = await adapter.get_all_pools(merge_external=False)
if success:
    pools = data.get("pools", [])
    print(f"Total pools available: {len(pools)}")
else:
    print(f"Error: {data}")
```

### Get Combined Pool Reports

```python
success, data = await adapter.get_combined_pool_reports()
if success:
    reports = data.get("reports", [])
    print(f"Received {len(reports)} combined reports")
else:
    print(f"Error: {data}")
```

### Find High Yield Pools

```python
success, data = await adapter.find_high_yield_pools(
    min_apy=0.03,  # 3% minimum APY
    min_tvl=500000,  # $500k minimum TVL
    stablecoin_only=True,
    network_codes=["base", "ethereum"]
)
if success:
    pools = data.get("pools", [])
    print(f"Found {len(pools)} high-yield pools")
    for pool in pools:
        print(f"Pool: {pool.get('id')} - APY: {pool.get('llama_apy_pct')}%")
else:
    print(f"Error: {data}")
```

### Get Pool Analytics

```python
success, data = await adapter.get_pool_analytics(
    pool_ids=["pool-123", "pool-456"]
)
if success:
    analytics = data.get("analytics", [])
    for pool_analytics in analytics:
        pool = pool_analytics.get("pool", {})
        combined_apy = pool_analytics.get("combined_apy", 0)
        tvl_usd = pool_analytics.get("tvl_usd", 0)
        print(f"Pool: {pool.get('name')} - APY: {combined_apy:.2%} - TVL: ${tvl_usd:,.0f}")
else:
    print(f"Error: {data}")
```

### Search Pools

```python
success, data = await adapter.search_pools(
    query="USDC",
    limit=10
)
if success:
    pools = data.get("pools", [])
    print(f"Found {len(pools)} pools matching 'USDC'")
    for pool in pools:
        print(f"Pool: {pool.get('name')} - {pool.get('symbol')}")
else:
    print(f"Error: {data}")
```

### Get Llama Matches

```python
success, data = await adapter.get_llama_matches()
if success:
    matches = data.get("matches", [])
    print(f"Found {len(matches)} Llama matches")
    for match in matches:
        if match.get("llama_stablecoin"):
            print(f"Stablecoin pool: {match.get('id')} - APY: {match.get('llama_apy_pct')}%")
else:
    print(f"Error: {data}")
```

### Get Llama Reports

```python
success, data = await adapter.get_llama_reports(
    identifiers=["pool-123", "usd-coin-base", "base_0x1234..."]
)
if success:
    reports = data
    for identifier, report in reports.items():
        print(f"Report for {identifier}: APY {report.get('llama_apy_pct', 0)}%")
else:
    print(f"Error: {data}")
```

## Advanced Usage

### Filtering High Yield Pools

The `find_high_yield_pools` method provides powerful filtering capabilities:

```python
# Find stablecoin pools with high yield on specific networks
success, data = await adapter.find_high_yield_pools(
    min_apy=0.05,  # 5% minimum APY
    min_tvl=1000000,  # $1M minimum TVL
    stablecoin_only=True,  # Only stablecoin pools
    network_codes=["base", "arbitrum"]  # Specific networks
)

if success:
    pools = data.get("pools", [])
    # Pools are automatically sorted by APY (highest first)
    best_pool = pools[0] if pools else None
    if best_pool:
        print(f"Best pool: {best_pool.get('id')} - APY: {best_pool.get('llama_apy_pct')}%")
```

### Comprehensive Pool Analysis

```python
# Get detailed analytics for specific pools
success, data = await adapter.get_pool_analytics(["pool-123"])

if success:
    analytics = data.get("analytics", [])
    for pool_analytics in analytics:
        pool = pool_analytics.get("pool", {})
        llama_data = pool_analytics.get("llama_data", {})
        
        print(f"Pool: {pool.get('name')}")
        print(f"  Combined APY: {pool_analytics.get('combined_apy', 0):.2%}")
        print(f"  TVL: ${pool_analytics.get('tvl_usd', 0):,.0f}")
        print(f"  Llama APY: {llama_data.get('llama_apy_pct', 0)}%")
        print(f"  Stablecoin: {llama_data.get('llama_stablecoin', False)}")
        print(f"  IL Risk: {llama_data.get('llama_il_risk', 'unknown')}")
```

## API Endpoints

The adapter uses the following Wayfinder API endpoints:

- `GET /api/v1/public/pools/?pool_ids=X` - Get pools by IDs
- `GET /api/v1/public/pools/` - Get all pools
- `GET /api/v1/public/pools/combined/` - Get combined pool reports
- `GET /api/v1/public/pools/llama/matches/` - Get Llama matches
- `GET /api/v1/public/pools/llama/reports/` - Get Llama reports

## Error Handling

All methods return a tuple of `(success: bool, data: Any)` where:
- `success` is `True` if the operation succeeded
- `data` contains the response data on success or error message on failure

## Testing

Run the adapter tests:

```bash
pytest wayfinder_paths/vaults/adapters/pool_adapter/test_adapter.py -v
```

## Dependencies

- `PoolClient` - Low-level API client for pool operations
- `BaseAdapter` - Base adapter class with common functionality
