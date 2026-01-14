import sys
from pathlib import Path
from unittest.mock import AsyncMock

# Ensure wayfinder-paths is on path for tests.test_utils import
# This is a workaround until conftest loading order is resolved
_wayfinder_path_dir = Path(__file__).parent.parent.parent.parent.resolve()
_wayfinder_path_str = str(_wayfinder_path_dir)
if _wayfinder_path_str not in sys.path:
    sys.path.insert(0, _wayfinder_path_str)
elif sys.path.index(_wayfinder_path_str) > 0:
    # Move to front to take precedence
    sys.path.remove(_wayfinder_path_str)
    sys.path.insert(0, _wayfinder_path_str)

import pytest  # noqa: E402

# Import test utilities
try:
    from tests.test_utils import get_canonical_examples, load_strategy_examples
except ImportError:
    # Fallback if path setup didn't work
    import importlib.util

    test_utils_path = Path(_wayfinder_path_dir) / "tests" / "test_utils.py"
    spec = importlib.util.spec_from_file_location("tests.test_utils", test_utils_path)
    test_utils = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_utils)
    get_canonical_examples = test_utils.get_canonical_examples
    load_strategy_examples = test_utils.load_strategy_examples

from wayfinder_paths.vaults.strategies.stablecoin_yield_strategy.strategy import (  # noqa: E402
    StablecoinYieldStrategy,
)


@pytest.fixture
def strategy():
    """Create a strategy instance for testing with minimal config."""
    mock_config = {
        "main_wallet": {"address": "0x1234567890123456789012345678901234567890"},
        "vault_wallet": {"address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"},
    }

    s = StablecoinYieldStrategy(
        config=mock_config,
        main_wallet=mock_config["main_wallet"],
        vault_wallet=mock_config["vault_wallet"],
        simulation=True,
    )

    if hasattr(s, "balance_adapter") and s.balance_adapter:
        usdc_balance_mock = AsyncMock(return_value=(True, 60000000))
        gas_balance_mock = AsyncMock(return_value=(True, 2000000000000000))

        def get_balance_side_effect(token_id, wallet_address, **kwargs):
            if token_id == "usd-coin-base" or token_id == "usd-coin":
                return usdc_balance_mock.return_value
            elif token_id == "ethereum-base" or token_id == "ethereum":
                return gas_balance_mock.return_value
            return (True, 1000000000)

        s.balance_adapter.get_balance = AsyncMock(side_effect=get_balance_side_effect)
        s.balance_adapter.get_all_balances = AsyncMock(
            return_value=(True, {"balances": []})
        )

    if hasattr(s, "token_adapter") and s.token_adapter:
        default_usdc = {
            "id": "usd-coin-base",
            "symbol": "USDC",
            "name": "USD Coin",
            "decimals": 6,
            "address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "chain": {"code": "base", "id": 8453, "name": "Base"},
        }

        default_pool_token = {
            "id": "test-pool-base",
            "symbol": "POOL",
            "name": "Test Pool",
            "decimals": 18,
            "address": "0x1234567890123456789012345678901234567890",
            "chain": {"code": "base", "id": 8453, "name": "Base"},
        }

        def get_token_side_effect(address=None, token_id=None, **kwargs):
            if token_id == "usd-coin-base" or token_id == "usd-coin":
                return (True, default_usdc)
            elif (
                token_id == "test-pool-base"
                or address == "0x1234567890123456789012345678901234567890"
            ):
                return (True, default_pool_token)
            return (True, default_usdc)

        s.token_adapter.get_token = AsyncMock(side_effect=get_token_side_effect)
        s.token_adapter.get_gas_token = AsyncMock(
            return_value=(
                True,
                {
                    "id": "ethereum-base",
                    "symbol": "ETH",
                    "name": "Ethereum",
                    "decimals": 18,
                    "address": "0x4200000000000000000000000000000000000006",
                    "chain": {"code": "base", "id": 8453, "name": "Base"},
                },
            )
        )

    if hasattr(s, "balance_adapter") and s.balance_adapter:
        s.balance_adapter.move_from_main_wallet_to_vault_wallet = AsyncMock(
            return_value=(True, "Transfer successful (simulated)")
        )
        s.balance_adapter.move_from_vault_wallet_to_main_wallet = AsyncMock(
            return_value=(True, "Transfer successful (simulated)")
        )
        if hasattr(s.balance_adapter, "wallet_provider"):
            s.balance_adapter.wallet_provider.broadcast_transaction = AsyncMock(
                return_value=(True, {"transaction_hash": "0xDEADBEEF"})
            )

    if hasattr(s, "ledger_adapter") and s.ledger_adapter:
        s.ledger_adapter.get_vault_net_deposit = AsyncMock(
            return_value=(True, {"net_deposit": 0})
        )
        s.ledger_adapter.get_vault_transactions = AsyncMock(
            return_value=(True, {"transactions": []})
        )

    if hasattr(s, "pool_adapter") and s.pool_adapter:
        s.pool_adapter.find_high_yield_pools = AsyncMock(
            return_value=(True, {"pools": [], "total_found": 0})
        )
        s.pool_adapter.get_pools_by_ids = AsyncMock(
            return_value=(
                True,
                {"pools": [{"id": "test-pool-base", "apy": 15.0, "symbol": "POOL"}]},
            )
        )
        s.pool_adapter.get_llama_matches = AsyncMock(
            return_value=(
                True,
                {
                    "matches": [
                        {
                            "llama_stablecoin": True,
                            "llama_il_risk": "no",
                            "llama_tvl_usd": 2000000,
                            "llama_apy_pct": 5.0,
                            "network": "base",
                            "address": "0x1234567890123456789012345678901234567890",
                            "token_id": "test-pool-base",
                            "pool_id": "test-pool-base",
                            "llama_combined_apy_pct": 15.0,
                        }
                    ]
                },
            )
        )

    if hasattr(s, "brap_adapter") and s.brap_adapter:

        def get_swap_quote_side_effect(*args, **kwargs):
            to_token_address = kwargs.get("to_token_address", "")
            if to_token_address == "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913":
                return (
                    True,
                    {
                        "quotes": {
                            "best_quote": {
                                "output_amount": "99900000",
                            }
                        }
                    },
                )
            return (
                True,
                {
                    "quotes": {
                        "best_quote": {
                            "output_amount": "105000000",
                            "input_amount": "50000000000000",
                            "toAmount": "105000000",
                            "estimatedGas": "1000000000",
                            "fromAmount": "100000000",
                            "fromToken": {"symbol": "USDC"},
                            "toToken": {"symbol": "POOL"},
                        }
                    }
                },
            )

        s.brap_adapter.get_swap_quote = AsyncMock(
            side_effect=get_swap_quote_side_effect
        )

    if (
        hasattr(s, "brap_adapter")
        and s.brap_adapter
        and hasattr(s.brap_adapter, "swap_from_quote")
    ):
        s.brap_adapter.swap_from_quote = AsyncMock(return_value=None)
    if hasattr(s, "brap_adapter") and hasattr(s.brap_adapter, "wallet_provider"):
        s.brap_adapter.wallet_provider.broadcast_transaction = AsyncMock(
            return_value=(True, {"transaction_hash": "0xBEEF"})
        )

    s.DEPOSIT_USDC = 0
    s.usdc_token_info = {
        "id": "usd-coin-base",
        "symbol": "USDC",
        "name": "USD Coin",
        "decimals": 6,
        "address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "chain": {"code": "base", "id": 8453, "name": "Base"},
    }
    s.gas_token = {
        "id": "ethereum-base",
        "symbol": "ETH",
        "name": "Ethereum",
        "decimals": 18,
        "address": "0x4200000000000000000000000000000000000006",
        "chain": {"code": "base", "id": 8453, "name": "Base"},
    }
    s.current_pool = {
        "id": "usd-coin-base",
        "symbol": "USDC",
        "decimals": 6,
        "chain": {"code": "base", "id": 8453, "name": "Base"},
    }
    s.current_pool_balance = 100000000
    s.current_combined_apy_pct = 0.0
    s.current_pool_data = None

    if hasattr(s, "token_adapter") and s.token_adapter:
        if not hasattr(s.token_adapter, "get_token_price"):
            s.token_adapter.get_token_price = AsyncMock()

        def get_token_price_side_effect(token_id):
            if token_id == "ethereum-base":
                return (True, {"current_price": 2000.0})
            else:
                return (True, {"current_price": 1.0})

        s.token_adapter.get_token_price = AsyncMock(
            side_effect=get_token_price_side_effect
        )

    async def mock_sweep_wallet(target_token):
        pass

    async def mock_refresh_current_pool_balance():
        pass

    async def mock_rebalance_gas(target_pool):
        return (True, "Gas rebalanced")

    async def mock_has_idle_assets(balances, target):
        return True

    s._sweep_wallet = mock_sweep_wallet
    s._refresh_current_pool_balance = mock_refresh_current_pool_balance
    s._rebalance_gas = mock_rebalance_gas
    s._has_idle_assets = mock_has_idle_assets

    return s


@pytest.mark.asyncio
@pytest.mark.smoke
async def test_smoke(strategy):
    """REQUIRED: Basic smoke test - verifies strategy lifecycle."""
    examples = load_strategy_examples(Path(__file__))
    smoke_data = examples["smoke"]

    st = await strategy.status()
    assert isinstance(st, dict)
    assert "portfolio_value" in st or "net_deposit" in st or "strategy_status" in st

    deposit_params = smoke_data.get("deposit", {})
    ok, msg = await strategy.deposit(**deposit_params)
    assert isinstance(ok, bool)
    assert isinstance(msg, str)

    ok, msg = await strategy.update(**smoke_data.get("update", {}))
    assert isinstance(ok, bool)

    ok, msg = await strategy.withdraw(**smoke_data.get("withdraw", {}))
    assert isinstance(ok, bool)


@pytest.mark.asyncio
async def test_canonical_usage(strategy):
    """REQUIRED: Test canonical usage examples from examples.json (minimum).

    Canonical usage = all positive usage examples (excluding error cases).
    This is the MINIMUM requirement - feel free to add more test cases here.
    """
    examples = load_strategy_examples(Path(__file__))
    canonical = get_canonical_examples(examples)

    for example_name, example_data in canonical.items():
        if "deposit" in example_data:
            deposit_params = example_data.get("deposit", {})
            ok, _ = await strategy.deposit(**deposit_params)
            assert ok, f"Canonical example '{example_name}' deposit failed"

        if "update" in example_data:
            ok, msg = await strategy.update()
            assert ok, f"Canonical example '{example_name}' update failed: {msg}"

        if "status" in example_data:
            st = await strategy.status()
            assert isinstance(st, dict), (
                f"Canonical example '{example_name}' status failed"
            )


@pytest.mark.asyncio
async def test_error_cases(strategy):
    """OPTIONAL: Test error scenarios from examples.json."""
    examples = load_strategy_examples(Path(__file__))

    for example_name, example_data in examples.items():
        if isinstance(example_data, dict) and "expect" in example_data:
            expect = example_data.get("expect", {})

            if "deposit" in example_data:
                deposit_params = example_data.get("deposit", {})
                ok, _ = await strategy.deposit(**deposit_params)

                if expect.get("success") is False:
                    assert ok is False, (
                        f"Expected {example_name} deposit to fail but it succeeded"
                    )
                elif expect.get("success") is True:
                    assert ok is True, (
                        f"Expected {example_name} deposit to succeed but it failed"
                    )

            if "update" in example_data:
                ok, _ = await strategy.update()
                if "success" in expect:
                    expected_success = expect.get("success")
                    assert ok == expected_success, (
                        f"Expected {example_name} update to "
                        f"{'succeed' if expected_success else 'fail'} but got opposite"
                    )
