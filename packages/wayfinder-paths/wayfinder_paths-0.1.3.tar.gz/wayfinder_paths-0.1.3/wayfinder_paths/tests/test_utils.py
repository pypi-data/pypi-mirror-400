"""Shared utilities for testing strategies and adapters."""

import json
from pathlib import Path
from typing import Any


def load_strategy_examples(strategy_test_file: Path) -> dict[str, Any]:
    """Load examples.json for a strategy test file.

    This is REQUIRED for all strategy tests. The examples.json file serves
    as both documentation and test data, ensuring tests stay in sync with examples.

    Args:
        strategy_test_file: Path to the test_strategy.py file

    Returns:
        Dictionary containing examples from examples.json

    Raises:
        FileNotFoundError: If examples.json does not exist
        json.JSONDecodeError: If examples.json is invalid JSON
    """
    examples_path = strategy_test_file.parent / "examples.json"

    if not examples_path.exists():
        raise FileNotFoundError(
            f"examples.json is REQUIRED for strategy tests. "
            f"Create it at: {examples_path}\n"
            f"See TESTING.md for the required structure."
        )

    with open(examples_path) as f:
        return json.load(f)


def get_canonical_examples(examples: dict[str, Any]) -> dict[str, Any]:
    """Extract canonical usage examples from examples.json.

    Canonical usage is defined as the primary, documented usage patterns
    that demonstrate how the strategy should be used. This includes:
    - 'smoke' example: The basic lifecycle test (deposit → update → status → withdraw)
    - Any examples without 'expect' fields (positive usage patterns)

    Args:
        examples: The full examples.json dictionary

    Returns:
        Dictionary of canonical examples keyed by their example name
    """
    canonical = {}

    # 'smoke' is always canonical
    if "smoke" in examples:
        canonical["smoke"] = examples["smoke"]

    # Any example without 'expect' is considered canonical usage
    for name, example_data in examples.items():
        if name == "smoke":
            continue  # Already added
        if isinstance(example_data, dict) and "expect" not in example_data:
            canonical[name] = example_data

    return canonical
