"""Pydantic schemas for TAXII 2.0 and 2.1 responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# Common schemas
class APIRootInfo(BaseModel):
    """API Root information."""

    url: str
    title: str
    description: str | None = None
    versions: list[str] = ["taxii-2.0", "taxii-2.1"]
    max_content_length: str | None = None


class CollectionBase(BaseModel):
    """Base collection schema."""

    id: str
    title: str
    description: str | None = None
    can_read: bool = True
    can_write: bool = True
    media_types: list[str] = Field(default_factory=lambda: ["application/stix+json;version=2.1"])


# TAXII 2.0 schemas
class Discovery20Response(BaseModel):
    """TAXII 2.0 Discovery response."""

    title: str
    description: str | None = None
    contact: str | None = None
    api_roots: list[str]  # Just URLs in 2.0


class Collection20(CollectionBase):
    """TAXII 2.0 Collection."""

    alias: str | None = None  # Only in TAXII 2.0


class STIXBundle(BaseModel):
    """STIX 2.0 Bundle for TAXII 2.0 responses."""

    type: str = "bundle"
    id: str
    spec_version: str = "2.0"
    objects: list[dict[str, Any]] = Field(default_factory=list)


class ManifestEntry20(BaseModel):
    """TAXII 2.0 Manifest entry."""

    id: str
    date_added: str | None = None
    version: str | None = None
    media_types: list[str] = Field(default_factory=list)


class Status20(BaseModel):
    """TAXII 2.0 Status response."""

    id: str
    status: str = "complete"
    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    pending_count: int = 0
    failures: list[dict] = Field(default_factory=list)
    successes: list[dict] = Field(default_factory=list)
    pendings: list[dict] = Field(default_factory=list)


# TAXII 2.1 schemas
class Discovery21Response(BaseModel):
    """TAXII 2.1 Discovery response."""

    title: str
    description: str | None = None
    contact: str | None = None
    default: str | None = None  # New in TAXII 2.1
    api_roots: list[str]


class Collection21(CollectionBase):
    """TAXII 2.1 Collection (no alias field)."""

    # Custom MITRE fields
    x_mitre_contents: list[str] | None = None
    x_mitre_version: str | None = None


class Envelope21(BaseModel):
    """TAXII 2.1 Envelope for paginated responses."""

    more: bool = False
    next: str | None = None
    objects: list[dict[str, Any]] = Field(default_factory=list)


class ManifestEntry21(BaseModel):
    """TAXII 2.1 Manifest entry."""

    id: str
    date_added: str | None = None
    version: str | None = None
    versions: list[str] | None = None  # New in TAXII 2.1
    media_types: list[str] = Field(default_factory=list)


class ManifestEnvelope21(BaseModel):
    """TAXII 2.1 Manifest envelope."""

    more: bool = False
    next: str | None = None
    objects: list[ManifestEntry21] = Field(default_factory=list)


class Status21(BaseModel):
    """TAXII 2.1 Status response."""

    id: str
    status: str = "complete"
    request_timestamp: str | None = None  # New in TAXII 2.1
    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    pending_count: int = 0
    failures: list[dict] = Field(default_factory=list)
    successes: list[dict] = Field(default_factory=list)
    pendings: list[dict] = Field(default_factory=list)


# Request schemas
class AddObjectsRequest(BaseModel):
    """Request to add objects to a collection."""

    objects: list[dict[str, Any]]  # For TAXII 2.1 envelope format


# Error schemas
class TAXIIError(BaseModel):
    """TAXII error response."""

    title: str
    description: str | None = None
    error_id: str | None = None
    error_code: str | None = None
    http_status: str | None = None
    external_details: str | None = None
    details: dict | None = None
