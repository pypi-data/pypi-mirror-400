#!/usr/bin/env python3
"""
Strategy Runner
Main entry point for running vault strategies locally
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from loguru import logger

from wayfinder_paths.core.config import VaultConfig, load_config_from_env
from wayfinder_paths.core.engine.manifest import load_manifest, validate_manifest
from wayfinder_paths.core.engine.VaultJob import VaultJob


def load_strategy(
    strategy_name: str,
    *,
    strategy_config: dict | None = None,
    simulation: bool = False,
    api_key: str | None = None,
):
    """
    Dynamically load a strategy by name using its manifest

    Args:
        strategy_name: Name of the strategy to load (directory name in vaults/strategies/)
        strategy_config: Configuration dict for the strategy
        simulation: Enable simulation mode for testing
        api_key: Optional API key for service account authentication

    Returns:
        Strategy instance
    """
    # Find strategy manifest by scanning for manifest.yaml in the strategy directory
    strategies_dir = Path(__file__).parent / "vaults" / "strategies"
    strategy_dir = strategies_dir / strategy_name
    manifest_path = strategy_dir / "manifest.yaml"

    if not manifest_path.exists():
        # List available strategies for better error message
        available = []
        if strategies_dir.exists():
            for path in strategies_dir.iterdir():
                if path.is_dir() and (path / "manifest.yaml").exists():
                    available.append(path.name)
        available_str = ", ".join(available) if available else "none"
        raise ValueError(
            f"Unknown strategy: {strategy_name}. Available strategies: {available_str}"
        )

    # Load manifest and use its entrypoint
    manifest = load_manifest(str(manifest_path))
    module_path, class_name = manifest.entrypoint.rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    strategy_class = getattr(module, class_name)

    return strategy_class(
        config=strategy_config, simulation=simulation, api_key=api_key
    )


def load_config(
    config_path: str | None = None, strategy_name: str | None = None
) -> VaultConfig:
    """
    Load configuration from file or environment

    Args:
        config_path: Optional path to config file
        strategy_name: Optional strategy name for per-strategy wallet lookup

    Returns:
        VaultConfig instance
    """
    if config_path and Path(config_path).exists():
        logger.info(f"Loading config from {config_path}")
        with open(config_path) as f:
            config_data = json.load(f)
        return VaultConfig.from_dict(config_data, strategy_name=strategy_name)
    else:
        logger.info("Loading config from environment variables")
        config = load_config_from_env()
        if strategy_name:
            config.strategy_config["_strategy_name"] = strategy_name
            config.__post_init__()
        return config


async def run_strategy(
    strategy_name: str | None = None,
    config_path: str | None = None,
    action: str = "run",
    manifest_path: str | None = None,
    simulation: bool = False,
    **kwargs,
):
    """
    Run a vault strategy

    Args:
        strategy_name: Name of the strategy to run
        config_path: Optional path to config file
        action: Action to perform (run, deposit, withdraw, status)
        **kwargs: Additional arguments for the action
    """
    try:
        # Determine strategy name for wallet lookup BEFORE loading config
        # This ensures wallets are properly matched during config initialization
        manifest = None
        strategy_name_for_wallet = None
        if manifest_path:
            logger.debug(f"Loading strategy via manifest: {manifest_path}")
            manifest = load_manifest(manifest_path)
            validate_manifest(manifest)
            # Extract directory name from manifest path for wallet lookup
            # Use the directory name (strategy identifier) for wallet lookup
            manifest_dir = Path(manifest_path).parent
            strategies_dir = Path(__file__).parent / "vaults" / "strategies"
            try:
                # Try to get relative path - if it's under strategies_dir, use directory name
                rel_path = manifest_dir.relative_to(strategies_dir)
                strategy_name_for_wallet = (
                    rel_path.parts[0] if rel_path.parts else manifest_dir.name
                )
            except ValueError:
                # Not under strategies_dir, fallback to directory name or manifest name
                strategy_name_for_wallet = manifest_dir.name or manifest.name
        else:
            if not strategy_name:
                raise ValueError("Either strategy_name or --manifest must be provided")
            logger.debug(f"Loading strategy by name: {strategy_name}")
            # Use directory name (strategy_name) directly for wallet lookup
            strategy_name_for_wallet = strategy_name

        # Load configuration with strategy name for wallet lookup
        logger.debug(f"Config path provided: {config_path}")
        config = load_config(config_path, strategy_name=strategy_name_for_wallet)
        logger.debug(
            "Loaded config: creds=%s wallets(main=%s vault=%s)",
            "yes"
            if (config.user.username and config.user.password)
            or config.user.refresh_token
            else "no",
            (config.user.main_wallet_address or "none"),
            (config.user.vault_wallet_address or "none"),
        )

        # Validate required configuration
        # No user id required; authentication is via credentials or refresh token

        # Load strategy with the enriched config
        if manifest_path:
            # Load strategy class from manifest
            module_path, class_name = manifest.entrypoint.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            strategy_class = getattr(module, class_name)
            strategy = strategy_class(
                config=config.strategy_config, simulation=simulation
            )
            logger.info(
                f"Loaded strategy from manifest: {strategy_name_for_wallet or 'unnamed'}"
            )
        else:
            strategy = load_strategy(
                strategy_name,
                strategy_config=config.strategy_config,
                simulation=simulation,
            )
            logger.info(f"Loaded strategy: {strategy.name}")

        # Create vault job
        vault_job = VaultJob(strategy, config)

        # Setup vault job
        logger.info("Setting up vault job...")
        logger.debug(
            "Auth mode: %s",
            "credentials"
            if (config.user.username and config.user.password)
            or config.user.refresh_token
            else "missing",
        )
        await vault_job.setup()

        # Execute action
        if action == "run":
            logger.info("Starting continuous execution...")
            await vault_job.run_continuous(interval_seconds=kwargs.get("interval"))

        elif action == "deposit":
            main_token_amount = kwargs.get("main_token_amount")
            gas_token_amount = kwargs.get("gas_token_amount")

            if main_token_amount is None and gas_token_amount is None:
                raise ValueError(
                    "Either main token amount or gas token amount required for deposit (use --main-token-amount and/or --gas-token-amount)"
                )

            # Default to 0.0 if not provided
            if main_token_amount is None:
                main_token_amount = 0.0
            if gas_token_amount is None:
                gas_token_amount = 0.0

            result = await vault_job.execute_strategy(
                "deposit",
                main_token_amount=main_token_amount,
                gas_token_amount=gas_token_amount,
            )
            logger.info(f"Deposit result: {result}")

        elif action == "withdraw":
            amount = kwargs.get("amount")
            result = await vault_job.execute_strategy("withdraw", amount=amount)
            logger.info(f"Withdraw result: {result}")

        elif action == "status":
            result = await vault_job.execute_strategy("status")
            logger.info(f"Status: {json.dumps(result, indent=2)}")

        elif action == "update":
            result = await vault_job.execute_strategy("update")
            logger.info(f"Update result: {result}")

        elif action == "partial-liquidate":
            usd_value = kwargs.get("amount")
            if not usd_value:
                raise ValueError("Amount (USD value) required for partial-liquidate")
            result = await vault_job.execute_strategy(
                "partial_liquidate", usd_value=usd_value
            )
            logger.info(f"Partial liquidation result: {result}")

        elif action == "policy":
            policies: list[str] = []

            try:
                spols = getattr(strategy, "policies", None)
                if callable(spols):
                    result = spols()  # type: ignore[misc]
                    if isinstance(result, list) and result:
                        policies = [p for p in result if isinstance(p, str)]
            except Exception:
                pass

            if not policies and manifest and getattr(manifest, "permissions", None):
                try:
                    mpol = manifest.permissions.get("policy")
                    if isinstance(mpol, str):
                        policies = [mpol]
                    elif isinstance(mpol, list):
                        policies = [p for p in mpol if isinstance(p, str)]
                except Exception:
                    pass

            seen = set()
            deduped: list[str] = []
            for p in policies:
                if p not in seen:
                    seen.add(p)
                    deduped.append(p)

            # Get wallet_id from CLI arg, config, or leave as None
            wallet_id = kwargs.get("wallet_id")
            if not wallet_id:
                wallet_id = config.strategy_config.get("wallet_id")
            if not wallet_id:
                wallet_id = config.system.wallet_id

            # Render policies with wallet_id if available
            if wallet_id:
                rendered = [
                    p.replace("FORMAT_WALLET_ID", str(wallet_id)) for p in deduped
                ]
            else:
                rendered = deduped
                logger.info(
                    "Policy rendering without wallet_id - policies contain FORMAT_WALLET_ID placeholder"
                )

            logger.info(json.dumps({"policies": rendered}, indent=2))

        elif action == "script":
            duration = kwargs.get("duration") or 300
            logger.info(f"Running script mode for {duration}s...")
            task = asyncio.create_task(
                vault_job.run_continuous(interval_seconds=kwargs.get("interval") or 60)
            )
            await asyncio.sleep(duration)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info("Script mode execution completed")

        else:
            raise ValueError(f"Unknown action: {action}")

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    finally:
        if "vault_job" in locals():
            await vault_job.stop()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run vault strategies")
    parser.add_argument(
        "strategy",
        nargs="?",
        help="Strategy to run (stablecoin_yield_strategy)",
    )
    parser.add_argument(
        "--manifest",
        help="Path to strategy manifest YAML (alternative to strategy name)",
    )
    parser.add_argument(
        "--config", help="Path to config file (defaults to environment variables)"
    )
    parser.add_argument(
        "--action",
        default="run",
        choices=[
            "run",
            "deposit",
            "withdraw",
            "status",
            "update",
            "policy",
            "script",
            "partial-liquidate",
        ],
        help="Action to perform (default: run)",
    )
    parser.add_argument(
        "--amount",
        type=float,
        help="Amount for withdraw/partial-liquidate actions",
    )
    parser.add_argument(
        "--main-token-amount",
        "--main_token_amount",
        type=float,
        dest="main_token_amount",
        help="Main token amount for deposit action",
    )
    parser.add_argument(
        "--gas-token-amount",
        "--gas_token_amount",
        type=float,
        dest="gas_token_amount",
        default=0.0,
        help="Gas token amount for deposit action (default: 0.0)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        help="Update interval in seconds for continuous/script modes",
    )
    parser.add_argument(
        "--duration", type=int, help="Duration in seconds for script action"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--simulation",
        action="store_true",
        help="Run in simulation mode (no real transactions)",
    )
    parser.add_argument(
        "--wallet-id",
        help="Wallet ID for policy rendering (replaces FORMAT_WALLET_ID in policies)",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = "DEBUG" if args.debug else "INFO"
    logger.remove()
    logger.add(sys.stderr, level=log_level)

    # Run strategy
    asyncio.run(
        run_strategy(
            strategy_name=args.strategy,
            config_path=args.config,
            action=args.action,
            manifest_path=args.manifest,
            amount=args.amount,
            main_token_amount=args.main_token_amount,
            gas_token_amount=args.gas_token_amount,
            interval=args.interval,
            duration=args.duration,
            simulation=args.simulation,
            wallet_id=getattr(args, "wallet_id", None),
        )
    )


if __name__ == "__main__":
    main()
