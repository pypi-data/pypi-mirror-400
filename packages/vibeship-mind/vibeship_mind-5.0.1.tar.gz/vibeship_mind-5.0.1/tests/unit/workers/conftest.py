"""Pytest configuration for Temporal worker tests.

These tests require Temporal's workflow environment which has sandbox
restrictions that conflict with numpy imports. They are marked as 'temporal'
tests and may need special handling in CI environments.
"""

import pytest


def pytest_collection_modifyitems(items):
    """Mark all tests in this directory as 'temporal' tests."""
    for item in items:
        if "workers" in str(item.fspath):
            item.add_marker(pytest.mark.temporal)
