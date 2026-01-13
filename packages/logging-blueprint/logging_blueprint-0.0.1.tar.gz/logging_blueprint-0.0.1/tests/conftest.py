"""Standard setup for pytest.

This module implements pytest's 'conftest.py' module standard, which is used to define fixtures that can be used
across multiple test modules. The fixtures defined here can be used in any test module within the same directory
or subdirectory.
"""

from pathlib import Path

import pytest


@pytest.fixture
def resources_dir() -> Path:
    """Fixture which provides the path to the resources directory."""
    conftest_path = Path(__file__)
    return conftest_path.parent / "resources"


@pytest.fixture
def examples_dir(resources_dir: Path) -> Path:
    """Fixture which provides the path to the examples directory."""
    return resources_dir / "examples"
