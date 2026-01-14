"""Wayfinder Path - Trading strategies and adapters for automated vault management"""

__version__ = "0.1.0"

# Re-export commonly used items for convenience
from wayfinder_paths.core import (
    BaseAdapter,
    StatusDict,
    StatusTuple,
    Strategy,
    VaultJob,
)

__all__ = [
    "__version__",
    "BaseAdapter",
    "Strategy",
    "StatusDict",
    "StatusTuple",
    "VaultJob",
]
