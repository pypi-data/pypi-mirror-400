"""Tests for MCP TAXII server."""

import os
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_initialize_taxii_with_params(mock_taxii_config):
    """Test initializing TAXII client with parameters."""
    # Import the actual function from the module
    from mcp_taxii.server import initialize_taxii

    with patch("mcp_taxii.server.TAXII21Client") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        # Call the actual function, not the FunctionTool wrapper
        result = await initialize_taxii.fn(
            url="https://test.server/taxii2/",
            username="user",
            password="pass",
            version="2.1",
        )

        assert "Successfully initialized TAXII 2.1 client" in result
        assert "https://test.server/taxii2/" in result
        mock_client.connect.assert_called_once()


@pytest.mark.asyncio
async def test_initialize_taxii_with_env_vars():
    """Test initializing TAXII client with environment variables."""
    from mcp_taxii.server import initialize_taxii

    with patch.dict(
        os.environ,
        {
            "MCPTAXII_HOST": "https://env.server/taxii2/",
            "MCPTAXII_USERNAME": "envuser",
            "MCPTAXII_PASSWORD": "envpass",
        },
    ):
        with patch("mcp_taxii.server.TAXII21Client") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            result = await initialize_taxii.fn()

            assert "Successfully initialized TAXII 2.1 client" in result
            assert "https://env.server/taxii2/" in result
            mock_client.connect.assert_called_once()


@pytest.mark.asyncio
async def test_initialize_taxii_no_url():
    """Test initializing TAXII client without URL should fail."""
    from mcp_taxii.server import initialize_taxii

    with pytest.raises(ValueError, match="TAXII URL must be provided"):
        await initialize_taxii.fn(username="user", password="pass")


@pytest.mark.asyncio
async def test_initialize_taxii_version_20():
    """Test initializing TAXII 2.0 client."""
    from mcp_taxii.server import initialize_taxii

    with patch("mcp_taxii.server.TAXII20Client") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        result = await initialize_taxii.fn(
            url="https://test.server/taxii2/",
            version="2.0",
        )

        assert "Successfully initialized TAXII 2.0 client" in result
        mock_client_class.assert_called_once()
        mock_client.connect.assert_called_once()


@pytest.mark.asyncio
async def test_initialize_taxii_invalid_version():
    """Test initializing TAXII with invalid version."""
    from mcp_taxii.server import initialize_taxii

    with pytest.raises(ValueError, match="Unsupported TAXII version"):
        await initialize_taxii.fn(
            url="https://test.server/taxii2/",
            version="1.0",
        )


@pytest.mark.asyncio
async def test_get_discovery_not_initialized():
    """Test getting discovery without initialization."""
    # Reset global client
    import mcp_taxii.server
    from mcp_taxii.server import get_discovery

    mcp_taxii.server._taxii_client = None

    with pytest.raises(RuntimeError, match="TAXII client not initialized"):
        await get_discovery.fn()


@pytest.mark.asyncio
async def test_get_discovery_success():
    """Test getting discovery information."""
    import mcp_taxii.server
    from mcp_taxii.server import get_discovery

    mock_client = AsyncMock()
    mock_client.get_discovery.return_value = {
        "title": "Test Server",
        "api_roots": ["https://test.server/api/v1/"],
    }
    mcp_taxii.server._taxii_client = mock_client

    result = await get_discovery.fn()

    assert result["title"] == "Test Server"
    assert "api_roots" in result
    mock_client.get_discovery.assert_called_once()


@pytest.mark.asyncio
async def test_get_collections_success():
    """Test getting collections."""
    import mcp_taxii.server
    from mcp_taxii.server import get_collections

    mock_client = AsyncMock()
    mock_client.get_collections.return_value = [
        {"id": "collection-1", "title": "Collection 1"},
        {"id": "collection-2", "title": "Collection 2"},
    ]
    mcp_taxii.server._taxii_client = mock_client

    result = await get_collections.fn()

    assert len(result) == 2
    assert result[0]["id"] == "collection-1"
    mock_client.get_collections.assert_called_once_with(None)


@pytest.mark.asyncio
async def test_get_collection_objects_success(sample_stix_objects):
    """Test getting objects from collection."""
    import mcp_taxii.server
    from mcp_taxii.server import get_collection_objects

    mock_client = AsyncMock()
    mock_client.get_objects.return_value = sample_stix_objects
    mcp_taxii.server._taxii_client = mock_client

    result = await get_collection_objects.fn("test-collection", limit=50)

    assert len(result) == 2
    assert result[0]["type"] == "indicator"
    # Updated to match new signature with additional filter parameters
    mock_client.get_objects.assert_called_once_with("test-collection", None, 50, None, None, None, None)


@pytest.mark.asyncio
async def test_get_object_manifest_success():
    """Test getting object manifest."""
    import mcp_taxii.server
    from mcp_taxii.server import get_object_manifest

    mock_client = AsyncMock()
    mock_client.get_manifest.return_value = [
        {
            "id": "indicator--01234567-89ab-cdef-0123-456789abcdef",
            "date_added": "2024-01-01T00:00:00.000Z",
        }
    ]
    mcp_taxii.server._taxii_client = mock_client

    result = await get_object_manifest.fn("test-collection")

    assert len(result) == 1
    assert result[0]["id"] == "indicator--01234567-89ab-cdef-0123-456789abcdef"
    # Updated to match new signature with additional filter parameters
    mock_client.get_manifest.assert_called_once_with("test-collection", None, 100, None, None, None, None)


@pytest.mark.asyncio
async def test_add_objects_success(sample_stix_objects):
    """Test adding objects to collection."""
    import mcp_taxii.server
    from mcp_taxii.server import add_objects

    mock_client = AsyncMock()
    mock_client.add_objects.return_value = {
        "status": "success",
        "total_count": 2,
        "success_count": 2,
        "failure_count": 0,
    }
    mcp_taxii.server._taxii_client = mock_client

    result = await add_objects.fn("test-collection", sample_stix_objects)

    assert result["status"] == "success"
    assert result["success_count"] == 2
    mock_client.add_objects.assert_called_once_with("test-collection", sample_stix_objects, None)
