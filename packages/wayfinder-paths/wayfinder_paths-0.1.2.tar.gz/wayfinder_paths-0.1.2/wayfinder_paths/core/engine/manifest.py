from typing import Any

import yaml
from pydantic import BaseModel, Field, validator


class AdapterRequirement(BaseModel):
    name: str = Field(
        ..., description="Adapter symbolic name (e.g., BALANCE, HYPERLIQUID)"
    )
    capabilities: list[str] = Field(default_factory=list)


class AdapterManifest(BaseModel):
    schema_version: str = Field(default="0.1")
    entrypoint: str
    capabilities: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)

    @validator("entrypoint")
    def validate_entrypoint(cls, v: str) -> str:
        if "." not in v:
            raise ValueError("entrypoint must be a full import path")
        return v

    @validator("capabilities")
    def validate_capabilities(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("capabilities cannot be empty")
        return v

    @validator("dependencies")
    def validate_dependencies(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("dependencies cannot be empty")
        return v


class StrategyManifest(BaseModel):
    schema_version: str = Field(default="0.1")
    entrypoint: str = Field(
        ...,
        description="Python path to class, e.g. vaults.strategies.funding_rate_strategy.FundingRateStrategy",
    )
    name: str | None = Field(
        default=None,
        description="Unique name identifier for this strategy instance. Used to look up dedicated wallet in wallets.json by label.",
    )
    permissions: dict[str, Any] = Field(default_factory=dict)
    adapters: list[AdapterRequirement] = Field(default_factory=list)

    @validator("entrypoint")
    def validate_entrypoint(cls, v: str) -> str:
        if "." not in v:
            raise ValueError(
                "entrypoint must be a full import path to a Strategy class"
            )
        return v

    @validator("permissions")
    def validate_permissions(cls, v: dict) -> dict:
        if "policy" not in v:
            raise ValueError("permissions.policy is required")
        if not v["policy"]:
            raise ValueError("permissions.policy cannot be empty")
        return v

    @validator("adapters")
    def validate_adapters(cls, v: list) -> list:
        if not v:
            raise ValueError("adapters cannot be empty")
        return v


def load_adapter_manifest(path: str) -> AdapterManifest:
    with open(path) as f:
        data = yaml.safe_load(f)
    return AdapterManifest(**data)


def load_strategy_manifest(path: str) -> StrategyManifest:
    with open(path) as f:
        data = yaml.safe_load(f)
    return StrategyManifest(**data)


def load_manifest(path: str) -> StrategyManifest:
    """Legacy function for backward compatibility."""
    return load_strategy_manifest(path)


def validate_manifest(manifest: StrategyManifest) -> None:
    # Simple v0.1 rules: require at least one adapter and permissions.policy
    if not manifest.adapters:
        raise ValueError("Manifest must declare at least one adapter")
    if "policy" not in manifest.permissions:
        raise ValueError("Manifest.permissions must include 'policy'")
