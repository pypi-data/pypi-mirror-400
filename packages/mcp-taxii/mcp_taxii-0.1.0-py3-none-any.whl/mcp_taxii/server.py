"""Main MCP TAXII Server implementation using FastMCP."""

import os

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from mcp_taxii.clients.base import TAXIIClient
from mcp_taxii.clients.taxii_20 import TAXII20Client
from mcp_taxii.clients.taxii_21 import TAXII21Client

# Initialize FastMCP server
mcp = FastMCP(name="mcp-taxii", version="0.1.0")


class TAXIIConfig(BaseModel):
    """Configuration for TAXII connection."""

    url: str = Field(description="TAXII server URL")
    username: str | None = Field(None, description="Username for authentication")
    password: str | None = Field(None, description="Password for authentication")
    version: str = Field("2.1", description="TAXII version (2.0 or 2.1)")


# Global TAXII client instance
_taxii_client: TAXIIClient | None = None


@mcp.tool()
async def initialize_taxii(
    url: str | None = None,
    username: str | None = None,
    password: str | None = None,
    version: str = "2.1",
) -> str:
    """
    Initialize TAXII client connection.

    Args:
        url: TAXII server URL (uses MCPTAXII_HOST env var if not provided)
        username: Username for authentication (uses MCPTAXII_USERNAME env var if not provided)
        password: Password for authentication (uses MCPTAXII_PASSWORD env var if not provided)
        version: TAXII version to use (2.0 or 2.1, defaults to 2.1)

    Returns:
        Success message with connection details
    """
    global _taxii_client

    # Get configuration from env vars if not provided
    url = url or os.getenv("MCPTAXII_HOST")
    username = username or os.getenv("MCPTAXII_USERNAME")
    password = password or os.getenv("MCPTAXII_PASSWORD")

    if not url:
        raise ValueError("TAXII URL must be provided or set in MCPTAXII_HOST environment variable")

    config = TAXIIConfig(url=url, username=username, password=password, version=version)

    # Create appropriate client based on version
    if version == "2.0":
        _taxii_client = TAXII20Client(config)
    elif version == "2.1":
        _taxii_client = TAXII21Client(config)
    else:
        raise ValueError(f"Unsupported TAXII version: {version}. Use 2.0 or 2.1")

    # Test connection
    await _taxii_client.connect()

    return f"Successfully initialized TAXII {version} client for {url}"


@mcp.tool()
async def get_discovery() -> dict:
    """
    Get TAXII server discovery information.

    Returns:
        Discovery information including API roots
    """
    if not _taxii_client:
        raise RuntimeError("TAXII client not initialized. Call initialize_taxii first.")

    return await _taxii_client.get_discovery()


@mcp.tool()
async def get_collections(api_root: str | None = None) -> list[dict]:
    """
    Get available collections from TAXII server.

    Args:
        api_root: API root URL (uses default if not provided)

    Returns:
        List of available collections
    """
    if not _taxii_client:
        raise RuntimeError("TAXII client not initialized. Call initialize_taxii first.")

    return await _taxii_client.get_collections(api_root)


@mcp.tool()
async def get_collection_objects(
    collection_id: str,
    api_root: str | None = None,
    limit: int = 100,
    added_after: str | None = None,
    match_id: str | list[str] | None = None,
    match_type: str | list[str] | None = None,
    match_version: str | None = None,
) -> dict:
    """
    Get STIX objects from a collection.

    Args:
        collection_id: Collection ID to fetch objects from
        api_root: API root URL (uses default if not provided)
        limit: Maximum number of objects to return
        added_after: Return objects added after this timestamp (ISO format)
        match_id: Filter by STIX object ID(s)
        match_type: Filter by STIX object type(s) (e.g., indicator, malware)
        match_version: Filter by version (last, first, all, or specific timestamp)

    Returns:
        TAXII 2.0: STIX bundle with 'type', 'id', 'objects' fields
        TAXII 2.1: Envelope with 'more', 'next', 'objects' fields
    """
    if not _taxii_client:
        raise RuntimeError("TAXII client not initialized. Call initialize_taxii first.")

    return await _taxii_client.get_objects(
        collection_id, api_root, limit, added_after, match_id, match_type, match_version
    )


@mcp.tool()
async def get_object_manifest(
    collection_id: str,
    api_root: str | None = None,
    limit: int = 100,
    added_after: str | None = None,
    match_id: str | list[str] | None = None,
    match_type: str | list[str] | None = None,
    match_version: str | None = None,
) -> dict | list[dict]:
    """
    Get object manifest from a collection.

    Args:
        collection_id: Collection ID to get manifest from
        api_root: API root URL (uses default if not provided)
        limit: Maximum number of manifest entries to return
        added_after: Return objects added after this timestamp (ISO format)
        match_id: Filter by STIX object ID(s)
        match_type: Filter by STIX object type(s)
        match_version: Filter by version (last, first, all, or specific timestamp)

    Returns:
        TAXII 2.0: List of manifest entry dicts
        TAXII 2.1: Envelope with 'more', 'next', 'objects' fields containing manifest entries
    """
    if not _taxii_client:
        raise RuntimeError("TAXII client not initialized. Call initialize_taxii first.")

    return await _taxii_client.get_manifest(
        collection_id, api_root, limit, added_after, match_id, match_type, match_version
    )


@mcp.tool()
async def add_objects(collection_id: str, objects: list[dict], api_root: str | None = None) -> dict:
    """
    Add STIX objects to a collection.

    Args:
        collection_id: Collection ID to add objects to
        objects: List of STIX objects to add
        api_root: API root URL (uses default if not provided)

    Returns:
        Status of the add operation
    """
    if not _taxii_client:
        raise RuntimeError("TAXII client not initialized. Call initialize_taxii first.")

    return await _taxii_client.add_objects(collection_id, objects, api_root)


def run():
    """Run the MCP TAXII server."""
    mcp.run()


def main():
    """Main entry point for the MCP TAXII server."""
    from pathlib import Path

    # Try to load .env file if it exists
    try:
        from dotenv import load_dotenv

        env_path = Path.cwd() / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass  # dotenv not available, continue without it

    # Run the server
    run()
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
