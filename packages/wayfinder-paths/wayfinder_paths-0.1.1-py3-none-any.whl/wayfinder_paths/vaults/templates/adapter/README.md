# Adapter Template

Adapters expose protocol-specific capabilities to strategies. They should be thin, async wrappers around one or more clients from `wayfinder_paths.core.clients`.

## Quick start

1. Copy the template:
   ```
   cp -r wayfinder_paths/vaults/templates/adapter wayfinder_paths/vaults/adapters/my_adapter
   ```
2. Rename `MyAdapter` in `adapter.py` and update `manifest.yaml` so the `entrypoint` matches (`vaults.adapters.my_adapter.adapter.MyAdapter`).
3. Declare the capabilities your adapter will provide and list any client dependencies (e.g., `PoolClient`, `LedgerClient`).
4. Implement the public methods that fulfill those capabilities.

## Layout

```
my_adapter/
├── adapter.py          # Adapter implementation
├── manifest.yaml       # Entrypoint + capabilities + dependency list
├── examples.json       # Example payloads (optional but encouraged)
├── test_adapter.py     # Pytest smoke tests
└── README.md           # Adapter-specific notes
```

## Skeleton adapter

```python
from typing import Any

from wayfinder_paths.core.adapters.BaseAdapter import BaseAdapter
from wayfinder_paths.core.clients.PoolClient import PoolClient


class MyAdapter(BaseAdapter):
    adapter_type = "MY_ADAPTER"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__("my_adapter", config)
        self.pool_client = PoolClient()

    async def connect(self) -> bool:
        """Optional: prime caches / test connectivity."""
        return True

    async def get_pools(self, pool_ids: list[str]) -> tuple[bool, Any]:
        """Example capability that proxies PoolClient."""
        try:
            data = await self.pool_client.get_pools_by_ids(
                pool_ids=",".join(pool_ids), merge_external=True
            )
            return (True, data)
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"Failed to fetch pools: {exc}")
            return (False, str(exc))
```

Your adapter should return `(success, payload)` tuples for every operation, just like the built-in adapters do.

## Manifest

Every adapter needs a manifest describing its import path, declared capabilities, and runtime dependencies.

```yaml
schema_version: "0.1"
entrypoint: "vaults.adapters.my_adapter.adapter.MyAdapter"
capabilities:
  - "pool.read"
dependencies:
  - "PoolClient"
```

The `dependencies` list is informational today but helps reviewers understand which core clients you rely on.

## Testing

`test_adapter.py` should cover the public methods you expose. Patch out remote clients with `unittest.mock.AsyncMock` so tests run offline.

```python
import pytest
from unittest.mock import AsyncMock, patch

from wayfinder_paths.vaults.adapters.my_adapter.adapter import MyAdapter


@pytest.mark.asyncio
async def test_get_pools():
    with patch(
        "wayfinder_paths.vaults.adapters.my_adapter.adapter.PoolClient",
        return_value=AsyncMock(
            get_pools_by_ids=AsyncMock(return_value={"pools": []})
        ),
    ):
        adapter = MyAdapter(config={})
        success, data = await adapter.get_pools(["pool-1"])
        assert success is True
        assert "pools" in data
```

## Best practices

- Capabilities listed in `manifest.yaml` must correspond to methods you implement.
- Keep adapters stateless and idempotent—strategies may reuse instances across operations.
- Use `self.logger` for contextual logging (BaseAdapter has already bound the adapter name).
- Raise `NotImplementedError` for manifest capabilities you intentionally do not support yet.
