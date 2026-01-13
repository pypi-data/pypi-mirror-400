"""TAXII 2.1 client implementation."""

from taxii2client.v21 import ApiRoot, Collection, Server

from mcp_taxii.clients.base import TAXIIClient


class TAXII21Client(TAXIIClient):
    """TAXII 2.1 client implementation."""

    def __init__(self, config):
        """Initialize TAXII 2.1 client."""
        super().__init__(config)
        self.server = None
        self.default_api_root = None

    async def connect(self) -> None:
        """Test connection to TAXII server."""
        # Create server connection
        if self.username and self.password:
            self.server = Server(self.url, user=self.username, password=self.password)
        else:
            self.server = Server(self.url)

        # Get default API root
        try:
            api_roots = self.server.api_roots
            if api_roots:
                self.default_api_root = api_roots[0]
        except Exception as e:
            raise ConnectionError(f"Failed to connect to TAXII server: {e}") from e

    async def get_discovery(self) -> dict:
        """Get server discovery information.

        TAXII 2.1 Specification:
        - Includes 'default' field for default API root
        - API roots include version and max_content_length
        """
        if not self.server:
            raise RuntimeError("Not connected to TAXII server")

        discovery_data = {
            "title": self.server.title,
            "description": getattr(self.server, "description", None),
            "contact": getattr(self.server, "contact", None),
            "default": getattr(self.server, "default", None),  # TAXII 2.1 default API root
            "api_roots": [],
        }

        for api_root in self.server.api_roots:
            root_data = {
                "url": api_root.url,
                "title": api_root.title,
                "description": getattr(api_root, "description", None),
                "versions": getattr(api_root, "versions", ["taxii-2.1"]),
                "max_content_length": getattr(api_root, "max_content_length", None),
            }
            discovery_data["api_roots"].append(root_data)

        return discovery_data

    async def get_collections(self, api_root: str | None = None) -> list[dict]:
        """Get available collections."""
        if not self.server:
            raise RuntimeError("Not connected to TAXII server")

        # Use provided API root or default
        if api_root:
            root = ApiRoot(api_root, user=self.username, password=self.password)
        else:
            root = self.default_api_root
            if not root:
                raise ValueError("No API root available")

        collections_data = []
        for collection in root.collections:
            coll_data = {
                "id": collection.id,
                "title": collection.title,
                "description": getattr(collection, "description", None),
                # 'alias' field removed - not in TAXII 2.1 spec
                "can_read": collection.can_read,
                "can_write": collection.can_write,
                "media_types": getattr(collection, "media_types", []),
                # Custom MITRE fields
                "x_mitre_contents": getattr(collection, "x_mitre_contents", None),
                "x_mitre_version": getattr(collection, "x_mitre_version", None),
            }
            collections_data.append(coll_data)

        return collections_data

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

        TAXII 2.1 Specification:
        - Returns an envelope with 'more', 'next', and 'objects' fields
        - Supports pagination through 'next' parameter
        - Does NOT return raw objects list
        """
        if not self.server:
            raise RuntimeError("Not connected to TAXII server")

        # Get the collection
        collection = self._get_collection(collection_id, api_root)

        # Build filters
        filters = {}
        if limit:
            filters["limit"] = limit
        if added_after:
            filters["added_after"] = added_after

        # Add match filters for TAXII 2.1
        if match_id:
            if isinstance(match_id, list):
                filters["match[id]"] = ",".join(match_id)
            else:
                filters["match[id]"] = match_id

        if match_type:
            if isinstance(match_type, list):
                filters["match[type]"] = ",".join(match_type)
            else:
                filters["match[type]"] = match_type

        if match_version:
            if isinstance(match_version, list):
                filters["match[version]"] = ",".join(match_version)
            else:
                filters["match[version]"] = match_version

        # Get objects - returns envelope in TAXII 2.1
        envelope = collection.get_objects(**filters)

        if not envelope:
            # Return empty envelope if no results
            return {"more": False, "objects": []}

        # Build TAXII 2.1 envelope response
        result = {"more": getattr(envelope, "more", False), "objects": []}

        # Add 'next' field if pagination available
        if hasattr(envelope, "next") and envelope.next:
            result["next"] = envelope.next

        # Extract objects from envelope
        if hasattr(envelope, "objects"):
            result["objects"] = [obj.serialize() if hasattr(obj, "serialize") else obj for obj in envelope.objects]
        elif isinstance(envelope, dict) and "objects" in envelope:
            result["objects"] = envelope["objects"]
            # Preserve envelope fields if already in correct format
            if "more" in envelope:
                result["more"] = envelope["more"]
            if "next" in envelope:
                result["next"] = envelope["next"]

        return result

    async def get_manifest(
        self,
        collection_id: str,
        api_root: str | None = None,
        limit: int = 100,
        added_after: str | None = None,
        match_id: str | list[str] | None = None,
        match_type: str | list[str] | None = None,
        match_version: str | list[str] | None = None,
    ) -> dict:
        """Get object manifest from a collection.

        TAXII 2.1 Specification:
        - Returns an envelope with 'more' and 'objects' fields
        - Manifest entries include 'versions' for version history
        """
        if not self.server:
            raise RuntimeError("Not connected to TAXII server")

        # Get the collection
        collection = self._get_collection(collection_id, api_root)

        # Build filters
        filters = {}
        if limit:
            filters["limit"] = limit
        if added_after:
            filters["added_after"] = added_after

        # Add match filters if supported
        if match_id:
            if isinstance(match_id, list):
                filters["match[id]"] = ",".join(match_id)
            else:
                filters["match[id]"] = match_id

        if match_type:
            if isinstance(match_type, list):
                filters["match[type]"] = ",".join(match_type)
            else:
                filters["match[type]"] = match_type

        if match_version:
            if isinstance(match_version, list):
                filters["match[version]"] = ",".join(match_version)
            else:
                filters["match[version]"] = match_version

        # Get manifest - returns envelope in TAXII 2.1
        envelope = collection.get_manifest(**filters)

        if not envelope:
            # Return empty envelope if no results
            return {"more": False, "objects": []}

        # Build TAXII 2.1 envelope response
        result = {"more": getattr(envelope, "more", False), "objects": []}

        # Add 'next' field if pagination available
        if hasattr(envelope, "next") and envelope.next:
            result["next"] = envelope.next

        # Extract manifest entries from envelope
        if hasattr(envelope, "objects"):
            for obj in envelope.objects:
                manifest_entry = {
                    "id": obj.id,
                    "date_added": str(obj.date_added) if hasattr(obj, "date_added") else None,
                    "version": getattr(obj, "version", None),
                    "versions": getattr(obj, "versions", None),  # TAXII 2.1 version history
                    "media_types": getattr(obj, "media_types", []),
                }
                result["objects"].append(manifest_entry)
        elif isinstance(envelope, dict) and "objects" in envelope:
            result["objects"] = envelope["objects"]
            # Preserve envelope fields if already in correct format
            if "more" in envelope:
                result["more"] = envelope["more"]
            if "next" in envelope:
                result["next"] = envelope["next"]

        return result

    async def add_objects(self, collection_id: str, objects: list[dict], api_root: str | None = None) -> dict:
        """Add STIX objects to a collection."""
        if not self.server:
            raise RuntimeError("Not connected to TAXII server")

        # Get the collection
        collection = self._get_collection(collection_id, api_root)

        if not collection.can_write:
            raise PermissionError(f"Collection {collection_id} is not writable")

        # Create envelope with objects (TAXII 2.1 format)
        envelope = {"objects": objects}

        # Add objects to collection
        status = collection.add_objects(envelope)

        # Return TAXII 2.1 status resource
        return {
            "id": getattr(status, "id", None),
            "status": getattr(status, "status", "complete"),
            "request_timestamp": getattr(status, "request_timestamp", None),  # TAXII 2.1
            "total_count": getattr(status, "total_count", 0),
            "success_count": getattr(status, "success_count", 0),
            "failure_count": getattr(status, "failure_count", 0),
            "pending_count": getattr(status, "pending_count", 0),
            "failures": getattr(status, "failures", []),
            "successes": getattr(status, "successes", []),
            "pendings": getattr(status, "pendings", []),
        }

    def _get_collection(self, collection_id: str, api_root: str | None = None) -> Collection:
        """Get a collection by ID."""
        # Use provided API root or default
        if api_root:
            root = ApiRoot(api_root, user=self.username, password=self.password)
        else:
            root = self.default_api_root
            if not root:
                raise ValueError("No API root available")

        # Find collection by ID
        for collection in root.collections:
            if collection.id == collection_id:
                return collection

        raise ValueError(f"Collection {collection_id} not found")
