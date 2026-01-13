"""Base TAXII client interface."""

from abc import ABC, abstractmethod


class TAXIIClient(ABC):
    """Abstract base class for TAXII clients."""

    def __init__(self, config):
        """Initialize client with configuration."""
        self.config = config
        self.url = config.url
        self.username = config.username
        self.password = config.password

    @abstractmethod
    async def connect(self) -> None:
        """Test connection to TAXII server."""
        pass

    @abstractmethod
    async def get_discovery(self) -> dict:
        """Get server discovery information."""
        pass

    @abstractmethod
    async def get_collections(self, api_root: str | None = None) -> list[dict]:
        """Get available collections."""
        pass

    @abstractmethod
    async def get_objects(
        self,
        collection_id: str,
        api_root: str | None = None,
        limit: int = 100,
        added_after: str | None = None,
        match_id: str | list[str] | None = None,
        match_type: str | list[str] | None = None,
        match_version: str | list[str] | None = None,
    ) -> dict:
        """Get STIX objects from a collection.

        Returns:
            TAXII 2.0: Bundle dict with 'type', 'id', 'objects' fields
            TAXII 2.1: Envelope dict with 'more', 'next', 'objects' fields
        """
        pass

    @abstractmethod
    async def get_manifest(
        self,
        collection_id: str,
        api_root: str | None = None,
        limit: int = 100,
        added_after: str | None = None,
        match_id: str | list[str] | None = None,
        match_type: str | list[str] | None = None,
        match_version: str | list[str] | None = None,
    ) -> dict | list[dict]:
        """Get object manifest from a collection.

        Returns:
            TAXII 2.0: List of manifest entry dicts
            TAXII 2.1: Envelope dict with 'more', 'next', 'objects' fields
        """
        pass

    @abstractmethod
    async def add_objects(self, collection_id: str, objects: list[dict], api_root: str | None = None) -> dict:
        """Add STIX objects to a collection."""
        pass
