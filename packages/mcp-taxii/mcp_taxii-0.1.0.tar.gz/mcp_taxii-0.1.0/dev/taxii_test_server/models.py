"""SQLAlchemy models for TAXII test server."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Many-to-many relationship between collections and STIX objects
collection_objects = Table(
    "collection_objects",
    Base.metadata,
    Column("collection_id", String, ForeignKey("collections.id"), primary_key=True),
    Column("object_id", String, ForeignKey("stix_objects.id"), primary_key=True),
    Column("date_added", DateTime, default=datetime.utcnow),
)


class Discovery(Base):
    """Discovery information model."""

    __tablename__ = "discovery"

    id = Column(String, primary_key=True, default="default")
    title = Column(String, nullable=False)
    description = Column(Text)
    contact = Column(String)
    default = Column(String)  # Default API root URL

    # Relationship to API roots
    api_roots = relationship("APIRoot", back_populates="discovery")


class APIRoot(Base):
    """API Root model."""

    __tablename__ = "api_roots"

    id = Column(String, primary_key=True)
    url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    versions = Column(JSON, default=lambda: ["taxii-2.0", "taxii-2.1"])
    max_content_length = Column(String, default="10485760")  # 10MB default

    # Foreign key to discovery
    discovery_id = Column(String, ForeignKey("discovery.id"))

    # Relationships
    discovery = relationship("Discovery", back_populates="api_roots")
    collections = relationship("Collection", back_populates="api_root")


class Collection(Base):
    """Collection model."""

    __tablename__ = "collections"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    alias = Column(String)  # Only for TAXII 2.0
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=True)
    media_types = Column(JSON, default=lambda: ["application/stix+json;version=2.1"])

    # Custom MITRE fields
    x_mitre_contents = Column(JSON)
    x_mitre_version = Column(String)

    # Foreign key to API root
    api_root_id = Column(String, ForeignKey("api_roots.id"))

    # Relationships
    api_root = relationship("APIRoot", back_populates="collections")
    objects = relationship("STIXObject", secondary=collection_objects, back_populates="collections")


class STIXObject(Base):
    """STIX Object model."""

    __tablename__ = "stix_objects"

    id = Column(String, primary_key=True)  # STIX ID
    type = Column(String, nullable=False)
    spec_version = Column(String, default="2.1")
    created = Column(DateTime)
    modified = Column(DateTime)
    created_by_ref = Column(String)
    labels = Column(JSON)
    confidence = Column(String)
    lang = Column(String)
    external_references = Column(JSON)
    object_marking_refs = Column(JSON)
    granular_markings = Column(JSON)

    # Store full STIX object as JSON
    object_data = Column(JSON, nullable=False)

    # Version tracking
    version = Column(DateTime)  # For TAXII version filtering

    # Relationships
    collections = relationship("Collection", secondary=collection_objects, back_populates="objects")


class Status(Base):
    """Status model for async operations."""

    __tablename__ = "status"

    id = Column(String, primary_key=True)
    status = Column(String, default="pending")  # pending, complete, failed
    request_timestamp = Column(DateTime, default=datetime.utcnow)
    total_count = Column(String, default="0")
    success_count = Column(String, default="0")
    failure_count = Column(String, default="0")
    pending_count = Column(String, default="0")

    # Detailed results as JSON
    failures = Column(JSON, default=list)
    successes = Column(JSON, default=list)
    pendings = Column(JSON, default=list)


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)  # Will store hashed password
    is_active = Column(Boolean, default=True)
    collections_read = Column(JSON)  # List of collection IDs user can read
    collections_write = Column(JSON)  # List of collection IDs user can write
