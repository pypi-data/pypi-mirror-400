"""TAXII 2.0 client implementation compliant with TAXII 2.0 specification."""

from taxii2client.v20 import ApiRoot, Collection, Server

from mcp_taxii.clients.base import TAXIIClient


class TAXII20Client(TAXIIClient):
    """TAXII 2.0 client implementation compliant with OASIS specification."""

    def __init__(self, config):
        """Initialize TAXII 2.0 client."""
        super().__init__(config)
        self.server = None
        self.default_api_root = None

    async def connect(self) -> None:
        """Test connection to TAXII server."""
        # Create server connection with authentication if provided
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
        """
        Get server discovery information.

        Returns discovery resource as per TAXII 2.0 spec section 4.1.
        """
        if not self.server:
            raise RuntimeError("Not connected to TAXII server")

        # Build discovery data according to spec
        discovery_data = {
            "title": self.server.title,
            "description": getattr(self.server, "description", None),
            "contact": getattr(self.server, "contact", None),  # Added per spec
            "api_roots": [],
        }

        # Add default API root if available
        if self.default_api_root:
            discovery_data["default"] = self.default_api_root.url

        # Add all API roots
        for api_root in self.server.api_roots:
            # For TAXII 2.0, API roots in discovery are just URLs
            discovery_data["api_roots"].append(api_root.url)

        return discovery_data

    async def get_collections(self, api_root: str | None = None) -> list[dict]:
        """
        Get available collections.

        Returns collections as per TAXII 2.0 spec section 5.1.
        """
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
            # Build collection data according to spec (no 'alias' field in TAXII 2.0)
            coll_data = {
                "id": collection.id,
                "title": collection.title,
                "description": getattr(collection, "description", None),
                "can_read": collection.can_read,
                "can_write": collection.can_write,
                "media_types": getattr(collection, "media_types", ["application/vnd.oasis.stix+json; version=2.0"]),
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
        """
        Get STIX objects from a collection.

        Returns STIX bundle as per TAXII 2.0 spec section 5.3.

        Args:
            collection_id: Collection to retrieve objects from
            api_root: API root URL (optional)
            limit: Maximum number of objects to return
            added_after: Return objects added after this timestamp
            match_id: Filter by STIX object ID(s)
            match_type: Filter by STIX object type(s)
            match_version: Filter by version (last, first, all, or specific timestamp)
        """
        if not self.server:
            raise RuntimeError("Not connected to TAXII server")

        # Get the collection
        collection = self._get_collection(collection_id, api_root)

        # Build filters according to spec
        filters = {}

        # Pagination limit
        if limit:
            filters["limit"] = limit

        # Temporal filter
        if added_after:
            filters["added_after"] = added_after

        # Match filters - the taxii2client library may use different parameter names
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

        # Get objects - should return a STIX bundle
        try:
            bundle = collection.get_objects(**filters)

            # The response should already be a bundle according to spec
            # If it's a bundle object, convert to dict
            if hasattr(bundle, "serialize"):
                return bundle.serialize()
            elif isinstance(bundle, dict):
                # Ensure it's a proper bundle format
                if "type" not in bundle:
                    # Wrap in bundle if needed
                    return {"type": "bundle", "id": f"bundle--{collection_id}", "objects": bundle.get("objects", [])}
                return bundle
            else:
                # Empty bundle if no results
                return {"type": "bundle", "id": f"bundle--{collection_id}", "objects": []}
        except Exception:
            # Return empty bundle on error
            return {"type": "bundle", "id": f"bundle--{collection_id}", "objects": []}

    async def get_manifest(
        self,
        collection_id: str,
        api_root: str | None = None,
        limit: int = 100,
        added_after: str | None = None,
        match_id: str | list[str] | None = None,
        match_type: str | list[str] | None = None,
        match_version: str | list[str] | None = None,
    ) -> list[dict]:
        """
        Get object manifest from a collection.

        Returns manifest entries as per TAXII 2.0 spec section 5.6.
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

        # Add match filters if supported by the library
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

        # Get manifest
        manifest = collection.get_manifest(**filters)

        # Convert to dict format per spec
        manifest_data = []
        if manifest:
            if hasattr(manifest, "objects"):
                # If manifest has objects attribute
                for obj in manifest.objects:
                    manifest_entry = {
                        "id": obj.id if hasattr(obj, "id") else obj.get("id"),
                        "date_added": str(obj.date_added) if hasattr(obj, "date_added") else obj.get("date_added"),
                        "versions": getattr(obj, "versions", obj.get("versions", [])),
                        "media_types": getattr(
                            obj, "media_types", obj.get("media_types", ["application/vnd.oasis.stix+json; version=2.0"])
                        ),
                    }
                    manifest_data.append(manifest_entry)
            elif isinstance(manifest, dict) and "objects" in manifest:
                # If manifest is already a dict with objects
                manifest_data = manifest["objects"]
            elif isinstance(manifest, list):
                # If manifest is a list of entries
                manifest_data = manifest

        return manifest_data

    async def add_objects(self, collection_id: str, objects: list[dict], api_root: str | None = None) -> dict:
        """
        Add STIX objects to a collection.

        Returns status resource as per TAXII 2.0 spec section 4.3.
        """
        if not self.server:
            raise RuntimeError("Not connected to TAXII server")

        # Get the collection
        collection = self._get_collection(collection_id, api_root)

        if not collection.can_write:
            raise PermissionError(f"Collection {collection_id} is not writable")

        # Create bundle with objects per spec
        bundle = {"type": "bundle", "id": f"bundle--add-{collection_id}", "objects": objects}

        # Add objects to collection
        try:
            status = collection.add_objects(bundle)
        except Exception as e:
            # Return error status
            return {
                "id": "status--error",
                "status": "complete",
                "total_count": len(objects),
                "success_count": 0,
                "failure_count": len(objects),
                "pending_count": 0,
                "failures": [{"id": obj.get("id", "unknown"), "message": str(e)} for obj in objects],
            }

        # Build status response according to spec
        status_response = {
            "id": getattr(status, "id", f"status--{collection_id}"),
            "status": getattr(status, "status", "complete"),
            "request_timestamp": getattr(status, "request_timestamp", None),
            "total_count": getattr(status, "total_count", len(objects)),
            "success_count": getattr(status, "success_count", 0),
            "failure_count": getattr(status, "failure_count", 0),
            "pending_count": getattr(status, "pending_count", 0),
        }

        # Add optional fields if present
        if hasattr(status, "successes"):
            status_response["successes"] = status.successes
        if hasattr(status, "failures"):
            status_response["failures"] = [
                {
                    "id": f.get("id") if isinstance(f, dict) else str(f),
                    "message": f.get("message", "") if isinstance(f, dict) else "",
                }
                for f in status.failures
            ]
        if hasattr(status, "pendings"):
            status_response["pendings"] = status.pendings

        return status_response

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
