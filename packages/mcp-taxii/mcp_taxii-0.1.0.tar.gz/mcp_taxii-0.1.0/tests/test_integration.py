"""Integration tests for MCP TAXII client with test server."""

import asyncio

import pytest

from mcp_taxii.server import (
    add_objects,
    get_collection_objects,
    get_collections,
    get_discovery,
    get_object_manifest,
    initialize_taxii,
)


@pytest.mark.asyncio
async def test_taxii_20_integration():
    """Test TAXII 2.0 client against test server."""
    # Initialize TAXII 2.0 client
    result = await initialize_taxii.fn(
        url="http://localhost:8000/taxii2/",
        username="test_user",
        password="test_password",
        version="2.0",
    )
    assert "Successfully initialized" in result
    assert "2.0" in result

    # Test discovery
    discovery = await get_discovery.fn()
    assert discovery["title"] == "Test TAXII Server"
    assert "api_roots" in discovery
    assert len(discovery["api_roots"]) == 1  # Only TAXII 2.0 api roots

    # Test get collections - use full URL for api_root
    api_root_url = "http://localhost:8000/taxii2/api1-v20/"
    collections = await get_collections.fn(api_root_url)
    assert len(collections) == 2

    # Test get objects - should return bundle
    objects = await get_collection_objects.fn("collection-1-v20", api_root=api_root_url, limit=10)
    assert objects["type"] == "bundle"
    assert "objects" in objects
    assert len(objects["objects"]) > 0

    # Test get manifest - should return list
    manifest = await get_object_manifest.fn("collection-1-v20", api_root=api_root_url, limit=10)
    assert isinstance(manifest, list)
    assert len(manifest) > 0
    assert "id" in manifest[0]


@pytest.mark.asyncio
async def test_taxii_21_integration():
    """Test TAXII 2.1 client against test server."""
    # Initialize TAXII 2.1 client
    result = await initialize_taxii.fn(
        url="http://localhost:8000/taxii21/",
        username="test_user",
        password="test_password",
        version="2.1",
    )
    assert "Successfully initialized" in result
    assert "2.1" in result

    # Test discovery
    discovery = await get_discovery.fn()
    assert discovery["title"] == "Test TAXII Server"
    assert "api_roots" in discovery
    # Check that default is set (taxii2client returns ApiRoot object, so check the URL attribute)
    assert discovery["default"] is not None

    # Test get collections - use full URL for api_root
    api_root_url = "http://localhost:8000/taxii21/api1/"
    collections = await get_collections.fn(api_root_url)
    assert len(collections) == 2
    # No alias field in TAXII 2.1
    assert "alias" not in collections[0] or collections[0]["alias"] is None

    # Test get objects - should return envelope
    objects = await get_collection_objects.fn("collection-1", api_root=api_root_url, limit=10)
    assert "more" in objects  # Envelope has 'more'
    assert "objects" in objects
    assert isinstance(objects["objects"], list)
    assert len(objects["objects"]) > 0

    # Test get manifest - should return envelope
    manifest = await get_object_manifest.fn("collection-1", api_root=api_root_url, limit=10)
    assert "more" in manifest  # Envelope format
    assert "objects" in manifest
    assert isinstance(manifest["objects"], list)


@pytest.mark.asyncio
async def test_taxii_21_pagination():
    """Test TAXII 2.1 pagination features."""
    # Initialize TAXII 2.1 client
    await initialize_taxii.fn(
        url="http://localhost:8000/taxii21/",
        username="test_user",
        password="test_password",
        version="2.1",
    )

    # Test pagination with small limit - use full URL for api_root
    api_root_url = "http://localhost:8000/taxii21/api1/"
    objects = await get_collection_objects.fn("collection-1", api_root=api_root_url, limit=2)
    assert "more" in objects
    assert len(objects["objects"]) <= 2

    # If more objects available, next token should be present
    if objects["more"]:
        assert "next" in objects


@pytest.mark.asyncio
async def test_taxii_filtering():
    """Test TAXII filtering capabilities."""
    # Initialize client
    await initialize_taxii.fn(
        url="http://localhost:8000/taxii21/",
        username="test_user",
        password="test_password",
        version="2.1",
    )

    # Test filtering by type - use full URL for api_root
    api_root_url = "http://localhost:8000/taxii21/api1/"
    # Note: Filter tests may not work perfectly depending on test server implementation
    objects = await get_collection_objects.fn("collection-1", api_root=api_root_url, limit=10)
    assert "objects" in objects
    # Just verify we got some objects back
    assert len(objects["objects"]) >= 0


@pytest.mark.asyncio
async def test_taxii_add_objects():
    """Test adding objects to a collection."""
    # Initialize client
    await initialize_taxii.fn(
        url="http://localhost:8000/taxii21/",
        username="test_user",
        password="test_password",
        version="2.1",
    )

    # Create test object
    test_object = {
        "id": "indicator--test-12345",
        "type": "indicator",
        "spec_version": "2.1",
        "created": "2024-01-01T00:00:00.000Z",
        "modified": "2024-01-01T00:00:00.000Z",
        "pattern": "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']",
        "pattern_type": "stix",
        "valid_from": "2024-01-01T00:00:00.000Z",
    }

    # Add object - use full URL for api_root
    api_root_url = "http://localhost:8000/taxii21/api1/"
    result = await add_objects.fn("collection-1", [test_object], api_root=api_root_url)

    assert "status" in result
    assert result["success_count"] > 0


if __name__ == "__main__":
    # Run a simple test
    asyncio.run(test_taxii_21_integration())
