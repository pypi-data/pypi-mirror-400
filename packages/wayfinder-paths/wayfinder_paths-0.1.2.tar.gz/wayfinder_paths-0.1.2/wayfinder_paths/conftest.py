"""
Conftest for wayfinder-paths package tests.
Adds wayfinder-paths directory to Python path for imports.
This must run early, so imports like 'from tests.test_utils' work.
"""

import sys
from pathlib import Path

# Add wayfinder-paths directory to Python path for imports (for tests.test_utils)
# This needs to be at index 0 to take precedence over repo root 'tests/' directory
_wayfinder_path_dir = Path(__file__).parent
_wayfinder_path_str = str(_wayfinder_path_dir)


def pytest_configure(config):
    """Configure pytest - runs early to set up imports."""
    if _wayfinder_path_str not in sys.path:
        sys.path.insert(0, _wayfinder_path_str)
    elif sys.path.index(_wayfinder_path_str) > 0:
        # Move to front if it exists but isn't first
        sys.path.remove(_wayfinder_path_str)
        sys.path.insert(0, _wayfinder_path_str)


# Also set it immediately (in case pytest_configure hasn't run yet)
if _wayfinder_path_str not in sys.path:
    sys.path.insert(0, _wayfinder_path_str)
elif sys.path.index(_wayfinder_path_str) > 0:
    sys.path.remove(_wayfinder_path_str)
    sys.path.insert(0, _wayfinder_path_str)
