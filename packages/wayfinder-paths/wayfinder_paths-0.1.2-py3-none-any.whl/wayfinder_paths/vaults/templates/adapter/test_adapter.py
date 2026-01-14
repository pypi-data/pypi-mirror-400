"""Test template for adapters.

Quick setup:
1. Replace MyAdapter with your actual adapter class name
2. Implement test_basic_functionality with your adapter's core methods
3. Add client mocking if your adapter uses external clients
4. Run: pytest vaults/adapters/your_adapter/ -v

Note: examples.json is optional for adapters (not required).
"""

import pytest

# TODO: Replace MyAdapter with your actual adapter class name
from .adapter import MyAdapter

# For mocking clients, uncomment when needed:
# from unittest.mock import AsyncMock, patch


class TestMyAdapter:
    """Test cases for MyAdapter"""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance for testing."""
        return MyAdapter(config={})

    @pytest.mark.asyncio
    async def test_health_check(self, adapter):
        """Test adapter health check"""
        health = await adapter.health_check()
        assert isinstance(health, dict)
        assert health.get("status") in {"healthy", "unhealthy", "error"}

    @pytest.mark.asyncio
    async def test_connect(self, adapter):
        """Test adapter connection"""
        ok = await adapter.connect()
        assert isinstance(ok, bool)

    def test_capabilities(self, adapter):
        """Test adapter capabilities match manifest"""
        assert hasattr(adapter, "adapter_type")

    @pytest.mark.asyncio
    async def test_basic_functionality(self, adapter):
        """REQUIRED: Test your adapter's core functionality."""
        assert adapter is not None
