"""Pytest configuration and fixtures."""

import pytest
import respx

from mcsrranked import MCSRRanked


@pytest.fixture
def client() -> MCSRRanked:
    """Create a test client."""
    return MCSRRanked()


@pytest.fixture
def mock_api() -> respx.MockRouter:
    """Create a mock API router."""
    with respx.mock(base_url="https://api.mcsrranked.com") as respx_mock:
        yield respx_mock
