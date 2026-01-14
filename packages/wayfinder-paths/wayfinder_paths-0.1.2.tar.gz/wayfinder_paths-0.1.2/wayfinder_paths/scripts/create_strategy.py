#!/usr/bin/env python3
"""
Create a new strategy from template and generate a dedicated wallet for it.

This script:
1. Copies the strategy template to a new directory
2. Generates a wallet with label matching the strategy name
3. Updates the manifest with the strategy name
"""

import argparse
import re
import shutil
from pathlib import Path

import yaml

from wayfinder_paths.core.utils.wallets import make_random_wallet, write_wallet_to_json


def sanitize_name(name: str) -> str:
    """Convert a strategy name to a valid directory/identifier name."""
    # Replace spaces and special chars with underscores, lowercase
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    # Remove multiple underscores
    name = re.sub(r"_+", "_", name)
    # Remove leading/trailing underscores
    name = name.strip("_")
    return name.lower()


def update_manifest(manifest_path: Path, strategy_name: str, entrypoint: str) -> None:
    """Update manifest.yaml with strategy name and entrypoint."""
    with open(manifest_path) as f:
        manifest_data = yaml.safe_load(f)

    manifest_data["name"] = strategy_name
    manifest_data["entrypoint"] = entrypoint

    with open(manifest_path, "w") as f:
        yaml.dump(manifest_data, f, default_flow_style=False, sort_keys=False)


def update_strategy_file(strategy_path: Path, class_name: str) -> None:
    """Update strategy.py with new class name."""
    content = strategy_path.read_text()
    # Replace MyStrategy with the new class name
    content = content.replace("MyStrategy", class_name)
    # Replace my_strategy references in docstrings/comments
    content = re.sub(
        r"my_strategy", class_name.lower().replace("Strategy", ""), content
    )
    strategy_path.write_text(content)


def main():
    parser = argparse.ArgumentParser(
        description="Create a new strategy from template with dedicated wallet"
    )
    parser.add_argument(
        "name",
        help="Strategy name (e.g., 'my_awesome_strategy' or 'My Awesome Strategy')",
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=Path(__file__).parent.parent / "vaults" / "templates" / "strategy",
        help="Path to strategy template directory",
    )
    parser.add_argument(
        "--strategies-dir",
        type=Path,
        default=Path(__file__).parent.parent / "vaults" / "strategies",
        help="Path to strategies directory",
    )
    parser.add_argument(
        "--wallets-file",
        type=Path,
        default=Path(__file__).parent.parent.parent / "wallets.json",
        help="Path to wallets.json file",
    )
    parser.add_argument(
        "--override",
        action="store_true",
        help="Override existing strategy directory if it exists",
    )
    args = parser.parse_args()

    # Sanitize name for directory
    dir_name = sanitize_name(args.name)
    strategy_dir = args.strategies_dir / dir_name

    # Check if directory already exists
    if strategy_dir.exists() and not args.override:
        raise SystemExit(
            f"Strategy directory already exists: {strategy_dir}\n"
            "Use --override to replace it"
        )

    # Check template exists
    if not args.template_dir.exists():
        raise SystemExit(f"Template directory not found: {args.template_dir}")

    # Create strategy directory
    if strategy_dir.exists():
        print(f"Removing existing directory: {strategy_dir}")
        shutil.rmtree(strategy_dir)
    strategy_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created strategy directory: {strategy_dir}")

    # Copy template files
    template_files = [
        "strategy.py",
        "manifest.yaml",
        "test_strategy.py",
        "examples.json",
        "README.md",
    ]
    for filename in template_files:
        src = args.template_dir / filename
        if src.exists():
            dst = strategy_dir / filename
            shutil.copy2(src, dst)
            print(f"  Copied {filename}")

    # Generate class name from strategy name
    # Convert "my_awesome_strategy" -> "MyAwesomeStrategy"
    class_name = "".join(word.capitalize() for word in dir_name.split("_"))
    if not class_name.endswith("Strategy"):
        class_name += "Strategy"

    # Update strategy.py with new class name
    strategy_file = strategy_dir / "strategy.py"
    if strategy_file.exists():
        update_strategy_file(strategy_file, class_name)
        print(f"  Updated strategy.py with class name: {class_name}")

    # Generate entrypoint path
    entrypoint = f"vaults.strategies.{dir_name}.strategy.{class_name}"

    # Update manifest with name (using directory name) and entrypoint
    manifest_path = strategy_dir / "manifest.yaml"
    if manifest_path.exists():
        update_manifest(manifest_path, dir_name, entrypoint)
        print(f"  Updated manifest.yaml with name: {dir_name}")

    # Generate wallet with label matching directory name (strategy identifier)
    # If wallets.json doesn't exist, create it with a main wallet first
    if not args.wallets_file.exists():
        print("  Creating new wallets.json with main wallet...")
        main_wallet = make_random_wallet()
        main_wallet["label"] = "main"
        write_wallet_to_json(
            main_wallet,
            out_dir=args.wallets_file.parent,
            filename=args.wallets_file.name,
        )
        print(f"  Generated main wallet: {main_wallet['address']}")

    # Generate strategy wallet (will append to existing wallets.json)
    wallet = make_random_wallet()
    wallet["label"] = dir_name
    write_wallet_to_json(
        wallet, out_dir=args.wallets_file.parent, filename=args.wallets_file.name
    )
    print(f"  Generated strategy wallet: {wallet['address']} (label: {dir_name})")

    print("\n✅ Strategy created successfully!")
    print(f"   Directory: {strategy_dir}")
    print(f"   Name: {dir_name}")
    print(f"   Class: {class_name}")
    print(f"   Entrypoint: {entrypoint}")
    print(f"   Wallet: {wallet['address']}")
    print("\nNext steps:")
    print(f"   1. Edit {strategy_dir / 'strategy.py'} to implement your strategy")
    print(f"   2. Update {strategy_dir / 'manifest.yaml'} with required adapters")
    print(f"   3. Test with: just test-strategy {dir_name}")


if __name__ == "__main__":
    main()
