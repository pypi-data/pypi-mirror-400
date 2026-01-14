"""Pytest configuration and fixtures for pywincode tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_bytes() -> bytes:
    """Provide sample bytes for testing."""
    return b"hello world"


@pytest.fixture
def binary_data() -> bytes:
    """Provide binary data with all byte values."""
    return bytes(range(256))


@pytest.fixture
def large_bytes() -> bytes:
    """Provide large byte sequence for performance testing."""
    return b"x" * 100000
