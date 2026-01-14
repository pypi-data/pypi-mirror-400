#!/usr/bin/env python3
"""
Manifest Validator

Validates all adapter and strategy manifests in the repository.
"""

import sys
from pathlib import Path

from loguru import logger

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from wayfinder_paths.core.adapters.BaseAdapter import BaseAdapter
from wayfinder_paths.core.engine.manifest import (
    load_adapter_manifest,
    load_strategy_manifest,
)
from wayfinder_paths.core.strategies.Strategy import Strategy


def verify_entrypoint(entrypoint: str) -> tuple[bool, str | None]:
    """Verify entrypoint is importable. Returns (success, error_message)."""
    try:
        module_path, class_name = entrypoint.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name], level=0)
        getattr(module, class_name)  # Verify class exists
        return True, None
    except ImportError as e:
        return False, f"Import error: {str(e)}"
    except AttributeError as e:
        return False, f"Class not found: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def verify_adapter_class(entrypoint: str) -> tuple[bool, str | None]:
    """Verify entrypoint is an adapter class."""
    valid, error = verify_entrypoint(entrypoint)
    if not valid:
        return False, error

    try:
        module_path, class_name = entrypoint.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name], level=0)
        adapter_class = getattr(module, class_name)

        if not issubclass(adapter_class, BaseAdapter):
            return False, f"{class_name} is not a BaseAdapter"
        return True, None
    except Exception as e:
        return False, f"Error verifying adapter: {str(e)}"


def verify_strategy_class(entrypoint: str) -> tuple[bool, str | None]:
    """Verify entrypoint is a strategy class."""
    valid, error = verify_entrypoint(entrypoint)
    if not valid:
        return False, error

    try:
        module_path, class_name = entrypoint.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name], level=0)
        strategy_class = getattr(module, class_name)

        if not issubclass(strategy_class, Strategy):
            return False, f"{class_name} is not a Strategy"
        return True, None
    except Exception as e:
        return False, f"Error verifying strategy: {str(e)}"


# Capabilities are only declared in manifest - no code validation needed
# Manifest is the single source of truth for capabilities


def verify_dependencies(dependencies: list[str]) -> tuple[bool, list[str]]:
    """Verify dependencies are importable. Returns (valid, error_messages)."""
    errors = []

    for dep in dependencies:
        # Try to import from core.clients
        try:
            __import__(f"core.clients.{dep}", fromlist=[dep], level=0)
        except ImportError:
            errors.append(f"Dependency '{dep}' not found in core.clients")
        except Exception as e:
            errors.append(f"Error importing dependency '{dep}': {str(e)}")

    return len(errors) == 0, errors


def validate_adapter_manifest(manifest_path: str) -> tuple[bool, list[str]]:
    """Validate adapter manifest. Returns (valid, error_messages)."""
    errors = []

    try:
        manifest = load_adapter_manifest(manifest_path)
    except Exception as e:
        return False, [f"Schema error: {str(e)}"]

    # Verify entrypoint
    valid, error = verify_adapter_class(manifest.entrypoint)
    if not valid:
        errors.append(f"Entrypoint validation failed: {error}")
        return False, errors

    # Verify dependencies
    valid, dep_errors = verify_dependencies(manifest.dependencies)
    if not valid:
        errors.extend(dep_errors)

    return len(errors) == 0, errors


def validate_strategy_manifest(manifest_path: str) -> tuple[bool, list[str]]:
    """Validate strategy manifest. Returns (valid, error_messages)."""
    errors = []

    try:
        manifest = load_strategy_manifest(manifest_path)
    except Exception as e:
        return False, [f"Schema error: {str(e)}"]

    # Verify entrypoint
    valid, error = verify_strategy_class(manifest.entrypoint)
    if not valid:
        errors.append(f"Entrypoint validation failed: {error}")
        return False, errors

    # Permissions are already validated by Pydantic model

    return len(errors) == 0, errors


def find_adapter_manifests() -> list[Path]:
    """Find all adapter manifest files."""
    manifests = []
    adapter_dir = Path(__file__).parent.parent / "vaults" / "adapters"
    if adapter_dir.exists():
        for adapter_path in adapter_dir.iterdir():
            manifest_path = adapter_path / "manifest.yaml"
            if manifest_path.exists():
                manifests.append(manifest_path)
    return manifests


def find_strategy_manifests() -> list[Path]:
    """Find all strategy manifest files."""
    manifests = []
    strategy_dir = Path(__file__).parent.parent / "vaults" / "strategies"
    if strategy_dir.exists():
        for strategy_path in strategy_dir.iterdir():
            manifest_path = strategy_path / "manifest.yaml"
            if manifest_path.exists():
                manifests.append(manifest_path)
    return manifests


def main() -> int:
    """Main validation function. Returns 0 on success, 1 on failure."""
    logger.info("Validating all manifests...")

    all_valid = True
    error_count = 0

    # Validate adapter manifests
    logger.info("\n=== Validating Adapter Manifests ===")
    adapter_manifests = find_adapter_manifests()
    for manifest_path in sorted(adapter_manifests):
        logger.info(f"Validating {manifest_path}...")
        valid, errors = validate_adapter_manifest(str(manifest_path))
        if valid:
            logger.success(f"✅ {manifest_path.name} - Valid")
        else:
            logger.error(f"❌ {manifest_path.name} - Invalid")
            for error in errors:
                logger.error(f"   {error}")
            all_valid = False
            error_count += len(errors)

    # Validate strategy manifests
    logger.info("\n=== Validating Strategy Manifests ===")
    strategy_manifests = find_strategy_manifests()
    for manifest_path in sorted(strategy_manifests):
        logger.info(f"Validating {manifest_path}...")
        valid, errors = validate_strategy_manifest(str(manifest_path))
        if valid:
            logger.success(f"✅ {manifest_path.name} - Valid")
        else:
            logger.error(f"❌ {manifest_path.name} - Invalid")
            for error in errors:
                logger.error(f"   {error}")
            all_valid = False
            error_count += len(errors)

    # Summary
    logger.info("\n=== Summary ===")
    if all_valid:
        logger.success(
            f"✅ All manifests valid! ({len(adapter_manifests)} adapters, "
            f"{len(strategy_manifests)} strategies)"
        )
        return 0
    else:
        logger.error(f"❌ Validation failed with {error_count} error(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
