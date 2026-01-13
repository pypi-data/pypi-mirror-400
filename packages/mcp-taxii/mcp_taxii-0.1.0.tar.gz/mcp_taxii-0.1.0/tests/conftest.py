"""Shared pytest fixtures for MCP TAXII tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_taxii_config():
    """Create a mock TAXII configuration."""
    from mcp_taxii.server import TAXIIConfig

    return TAXIIConfig(
        url="https://test.taxii.server/taxii2/",
        username="testuser",
        password="testpass",
        version="2.1",
    )


@pytest.fixture
def mock_taxii_20_server():
    """Create a mock TAXII 2.0 server."""
    server = MagicMock()
    server.title = "Test TAXII 2.0 Server"
    server.description = "Test server for TAXII 2.0"

    # Mock API root
    api_root = MagicMock()
    api_root.url = "https://test.taxii.server/api/v1/"
    api_root.title = "Test API Root"
    api_root.description = "Test API root"
    api_root.versions = ["taxii-2.0"]
    api_root.max_content_length = 10485760

    # Mock collection
    collection = MagicMock()
    collection.id = "test-collection"
    collection.title = "Test Collection"
    collection.description = "Test collection for unit tests"
    collection.can_read = True
    collection.can_write = True
    collection.media_types = ["application/stix+json;version=2.1"]

    api_root.collections = [collection]
    server.api_roots = [api_root]

    return server


@pytest.fixture
def mock_taxii_21_server():
    """Create a mock TAXII 2.1 server."""
    server = MagicMock()
    server.title = "Test TAXII 2.1 Server"
    server.description = "Test server for TAXII 2.1"
    server.contact = "admin@test.server"

    # Mock API root
    api_root = MagicMock()
    api_root.url = "https://test.taxii.server/api/v2/"
    api_root.title = "Test API Root v2"
    api_root.description = "Test API root for v2"
    api_root.versions = ["taxii-2.1"]
    api_root.max_content_length = 10485760

    # Mock collection
    collection = MagicMock()
    collection.id = "test-collection-v2"
    collection.title = "Test Collection v2"
    collection.description = "Test collection for TAXII 2.1"
    collection.can_read = True
    collection.can_write = True
    collection.media_types = ["application/taxii+json;version=2.1"]

    api_root.collections = [collection]
    server.api_roots = [api_root]

    return server


@pytest.fixture
def sample_stix_objects():
    """Create sample STIX objects for testing."""
    return [
        {
            "type": "indicator",
            "id": "indicator--01234567-89ab-cdef-0123-456789abcdef",
            "created": "2024-01-01T00:00:00.000Z",
            "modified": "2024-01-01T00:00:00.000Z",
            "name": "Test Indicator",
            "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
            "valid_from": "2024-01-01T00:00:00.000Z",
        },
        {
            "type": "malware",
            "id": "malware--fedcba98-7654-3210-fedc-ba9876543210",
            "created": "2024-01-01T00:00:00.000Z",
            "modified": "2024-01-01T00:00:00.000Z",
            "name": "Test Malware",
            "malware_types": ["trojan"],
        },
    ]
