from typing import Any

from wayfinder_paths.core.adapters.BaseAdapter import BaseAdapter


class MyAdapter(BaseAdapter):
    """
    Template adapter for a protocol/exchange integration.
    Copy this folder, rename it (e.g., my_adapter), update manifest entrypoint,
    and implement the capabilities your manifest declares.
    """

    adapter_type: str = "MY_ADAPTER"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__("my_adapter", config)

    async def connect(self) -> bool:
        """Establish connectivity to remote service(s) if needed."""
        return True

    async def example_operation(self, **kwargs) -> tuple[bool, str]:
        """
        Example operation. Replace with your adapter's real API.
        """
        return (True, "example.op executed")
