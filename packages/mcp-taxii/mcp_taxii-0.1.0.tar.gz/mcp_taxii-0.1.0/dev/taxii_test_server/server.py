"""FastAPI TAXII 2.0/2.1 test server."""

import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from dev.taxii_test_server.auth import check_collection_permission, optional_auth
from dev.taxii_test_server.database import get_db, init_db
from dev.taxii_test_server.models import APIRoot, Collection, Discovery, STIXObject, Status, User, collection_objects
from dev.taxii_test_server.schemas import (
    AddObjectsRequest,
    Collection20,
    Collection21,
    Discovery20Response,
    Discovery21Response,
    Envelope21,
    ManifestEntry20,
    ManifestEntry21,
    ManifestEnvelope21,
    Status20,
    Status21,
    STIXBundle,
    TAXIIError,
)

app = FastAPI(title="TAXII Test Server", version="1.0.0")


# Startup event to initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


# Helper functions
def parse_match_parameter(param: str | None) -> list[str] | None:
    """Parse comma-separated match parameters."""
    if not param:
        return None
    return [item.strip() for item in param.split(",")]


def apply_filters(
    query, added_after: str | None, match_id: str | None, match_type: str | None, match_version: str | None
):
    """Apply TAXII filtering to a query."""
    if added_after:
        # Parse RFC3339 timestamp and filter
        try:
            after_dt = datetime.fromisoformat(added_after.replace("Z", "+00:00"))
            query = query.filter(collection_objects.c.date_added >= after_dt)
        except ValueError:
            pass

    if match_id:
        id_list = parse_match_parameter(match_id)
        if id_list:
            query = query.filter(STIXObject.id.in_(id_list))

    if match_type:
        type_list = parse_match_parameter(match_type)
        if type_list:
            query = query.filter(STIXObject.type.in_(type_list))

    if match_version:
        # Handle version filtering (simplified for testing)
        if match_version == "last":
            # Get latest version
            pass  # Simplified - would need subquery for real implementation
        elif match_version == "first":
            # Get first version
            pass  # Simplified
        # For specific version, filter by timestamp

    return query


# TAXII Media Types (for discovery, collections, etc.)
TAXII_20_MEDIA_TYPE = "application/vnd.oasis.taxii+json; version=2.0"
TAXII_21_MEDIA_TYPE = "application/taxii+json;version=2.1"

# STIX Media Types (for object bundles/envelopes)
STIX_20_MEDIA_TYPE = "application/vnd.oasis.stix+json; version=2.0"
STIX_21_MEDIA_TYPE = "application/stix+json;version=2.1"


# TAXII 2.0 Endpoints
@app.get("/taxii2/")
async def discovery_20(db: Session = Depends(get_db)):
    """TAXII 2.0 Discovery endpoint."""
    # Query the TAXII 2.0 specific discovery
    discovery = db.query(Discovery).filter(Discovery.id == "discovery-20").first()
    if not discovery:
        raise HTTPException(status_code=404, detail="Discovery information not found")

    api_root_urls = [root.url for root in discovery.api_roots]

    response = Discovery20Response(
        title=discovery.title,
        description=discovery.description,
        contact=discovery.contact,
        api_roots=api_root_urls,
    )
    return JSONResponse(content=response.model_dump(), media_type=TAXII_20_MEDIA_TYPE)


@app.get("/taxii2/{api_root}/")
async def api_root_20(api_root: str, db: Session = Depends(get_db)):
    """TAXII 2.0 API Root information."""
    root = db.query(APIRoot).filter(APIRoot.id == api_root).first()
    if not root:
        raise HTTPException(status_code=404, detail="API root not found")

    return JSONResponse(
        content={
            "title": root.title,
            "description": root.description,
            "versions": root.versions,
            "max_content_length": root.max_content_length,
        },
        media_type=TAXII_20_MEDIA_TYPE,
    )


@app.get("/taxii2/{api_root}/collections/")
async def get_collections_20(
    api_root: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_auth),
):
    """TAXII 2.0 Get collections."""
    root = db.query(APIRoot).filter(APIRoot.id == api_root).first()
    if not root:
        raise HTTPException(status_code=404, detail="API root not found")

    collections = []
    for collection in root.collections:
        if check_collection_permission(user, collection.id, "read"):
            collections.append(
                Collection20(
                    id=collection.id,
                    title=collection.title,
                    description=collection.description,
                    alias=collection.alias,
                    can_read=collection.can_read,
                    can_write=collection.can_write and check_collection_permission(user, collection.id, "write"),
                    media_types=collection.media_types or [],
                ).model_dump()
            )

    return JSONResponse(content={"collections": collections}, media_type=TAXII_20_MEDIA_TYPE)


@app.get("/taxii2/{api_root}/collections/{collection_id}/")
async def get_collection_20(
    api_root: str,
    collection_id: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_auth),
):
    """TAXII 2.0 Get collection details."""
    collection = (
        db.query(Collection).filter(and_(Collection.id == collection_id, Collection.api_root_id == api_root)).first()
    )

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if not check_collection_permission(user, collection_id, "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    response = Collection20(
        id=collection.id,
        title=collection.title,
        description=collection.description,
        alias=collection.alias,
        can_read=collection.can_read,
        can_write=collection.can_write and check_collection_permission(user, collection_id, "write"),
        media_types=collection.media_types or [],
    )
    return JSONResponse(content=response.model_dump(), media_type=TAXII_20_MEDIA_TYPE)


@app.get("/taxii2/{api_root}/collections/{collection_id}/objects/")
async def get_objects_20(
    api_root: str,
    collection_id: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_auth),
    added_after: str | None = Query(None, alias="added_after"),
    limit: int = Query(100, ge=1, le=1000),
    match_id: str | None = Query(None, alias="match[id]"),
    match_type: str | None = Query(None, alias="match[type]"),
    match_version: str | None = Query(None, alias="match[version]"),
):
    """TAXII 2.0 Get objects - returns STIX bundle."""
    collection = (
        db.query(Collection).filter(and_(Collection.id == collection_id, Collection.api_root_id == api_root)).first()
    )

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if not check_collection_permission(user, collection_id, "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Query objects with filters
    query = (
        db.query(STIXObject)
        .join(collection_objects, STIXObject.id == collection_objects.c.object_id)
        .filter(collection_objects.c.collection_id == collection_id)
    )

    query = apply_filters(query, added_after, match_id, match_type, match_version)
    objects = query.limit(limit).all()

    # Create STIX bundle
    bundle = STIXBundle(
        type="bundle",
        id=f"bundle--{uuid.uuid4()}",
        spec_version="2.0",
        objects=[obj.object_data for obj in objects],
    )

    return JSONResponse(
        content=bundle.model_dump(),
        media_type=STIX_20_MEDIA_TYPE,  # STIX bundles use STIX media type
    )


@app.post("/taxii2/{api_root}/collections/{collection_id}/objects/")
async def add_objects_20(
    api_root: str,
    collection_id: str,
    request: STIXBundle,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_auth),
):
    """TAXII 2.0 Add objects."""
    collection = (
        db.query(Collection).filter(and_(Collection.id == collection_id, Collection.api_root_id == api_root)).first()
    )

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if not check_collection_permission(user, collection_id, "write"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Create status object
    status_obj = Status(
        id=f"status--{uuid.uuid4()}",
        status="complete",
        total_count=str(len(request.objects)),
        success_count="0",
        failure_count="0",
    )

    successes = []
    failures = []

    # Process objects
    for obj_data in request.objects:
        try:
            # Check if object exists
            existing = db.query(STIXObject).filter(STIXObject.id == obj_data.get("id")).first()

            if not existing:
                # Create new object
                stix_obj = STIXObject(
                    id=obj_data.get("id", f"indicator--{uuid.uuid4()}"),
                    type=obj_data.get("type", "indicator"),
                    spec_version=obj_data.get("spec_version", "2.0"),
                    created=datetime.fromisoformat(obj_data.get("created", datetime.utcnow().isoformat())),
                    modified=datetime.fromisoformat(obj_data.get("modified", datetime.utcnow().isoformat())),
                    object_data=obj_data,
                )
                db.add(stix_obj)
                collection.objects.append(stix_obj)
                successes.append({"id": stix_obj.id})
            else:
                # Update existing
                existing.modified = datetime.utcnow()
                existing.object_data = obj_data
                successes.append({"id": existing.id})

        except Exception as e:
            failures.append({"id": obj_data.get("id", "unknown"), "message": str(e)})

    status_obj.success_count = str(len(successes))
    status_obj.failure_count = str(len(failures))
    status_obj.successes = successes
    status_obj.failures = failures

    db.add(status_obj)
    db.commit()

    response = Status20(
        id=status_obj.id,
        status=status_obj.status,
        total_count=int(status_obj.total_count),
        success_count=int(status_obj.success_count),
        failure_count=int(status_obj.failure_count),
        successes=successes,
        failures=failures,
    )
    return JSONResponse(content=response.model_dump(), media_type=TAXII_20_MEDIA_TYPE)


@app.get("/taxii2/{api_root}/collections/{collection_id}/manifest/")
async def get_manifest_20(
    api_root: str,
    collection_id: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_auth),
    added_after: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    match_id: str | None = Query(None, alias="match[id]"),
    match_type: str | None = Query(None, alias="match[type]"),
    match_version: str | None = Query(None, alias="match[version]"),
):
    """TAXII 2.0 Get manifest - returns list."""
    collection = (
        db.query(Collection).filter(and_(Collection.id == collection_id, Collection.api_root_id == api_root)).first()
    )

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if not check_collection_permission(user, collection_id, "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Query objects with filters
    query = (
        db.query(STIXObject, collection_objects.c.date_added)
        .join(collection_objects, STIXObject.id == collection_objects.c.object_id)
        .filter(collection_objects.c.collection_id == collection_id)
    )

    query = apply_filters(query, added_after, match_id, match_type, match_version)
    results = query.limit(limit).all()

    manifest = []
    for obj, date_added in results:
        manifest.append(
            ManifestEntry20(
                id=obj.id,
                date_added=date_added.isoformat() if date_added else None,
                version=obj.version.isoformat() if obj.version else None,
                media_types=["application/stix+json;version=2.0"],
            ).model_dump()
        )

    return JSONResponse(
        content=manifest,
        media_type=TAXII_20_MEDIA_TYPE,  # Use correct TAXII 2.0 media type
    )


# TAXII 2.1 Endpoints
@app.get("/taxii21/")
async def discovery_21(db: Session = Depends(get_db)):
    """TAXII 2.1 Discovery endpoint."""
    # Query the TAXII 2.1 specific discovery
    discovery = db.query(Discovery).filter(Discovery.id == "discovery-21").first()
    if not discovery:
        raise HTTPException(status_code=404, detail="Discovery information not found")

    api_root_urls = [root.url for root in discovery.api_roots]

    response = Discovery21Response(
        title=discovery.title,
        description=discovery.description,
        contact=discovery.contact,
        default=discovery.default,  # New in 2.1
        api_roots=api_root_urls,
    )
    return JSONResponse(content=response.model_dump(), media_type=TAXII_21_MEDIA_TYPE)


@app.get("/taxii21/{api_root}/")
async def api_root_21(api_root: str, db: Session = Depends(get_db)):
    """TAXII 2.1 API Root information."""
    root = db.query(APIRoot).filter(APIRoot.id == api_root).first()
    if not root:
        raise HTTPException(status_code=404, detail="API root not found")

    return JSONResponse(
        content={
            "title": root.title,
            "description": root.description,
            "versions": root.versions,
            "max_content_length": root.max_content_length,
        },
        media_type=TAXII_21_MEDIA_TYPE,
    )


@app.get("/taxii21/{api_root}/collections/")
async def get_collections_21(
    api_root: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_auth),
):
    """TAXII 2.1 Get collections."""
    root = db.query(APIRoot).filter(APIRoot.id == api_root).first()
    if not root:
        raise HTTPException(status_code=404, detail="API root not found")

    collections = []
    for collection in root.collections:
        if check_collection_permission(user, collection.id, "read"):
            collections.append(
                Collection21(
                    id=collection.id,
                    title=collection.title,
                    description=collection.description,
                    # No alias in TAXII 2.1
                    can_read=collection.can_read,
                    can_write=collection.can_write and check_collection_permission(user, collection.id, "write"),
                    media_types=collection.media_types or [],
                    x_mitre_contents=collection.x_mitre_contents,
                    x_mitre_version=collection.x_mitre_version,
                ).model_dump()
            )

    return JSONResponse(content={"collections": collections}, media_type=TAXII_21_MEDIA_TYPE)


@app.get("/taxii21/{api_root}/collections/{collection_id}/")
async def get_collection_21(
    api_root: str,
    collection_id: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_auth),
):
    """TAXII 2.1 Get collection details."""
    collection = (
        db.query(Collection).filter(and_(Collection.id == collection_id, Collection.api_root_id == api_root)).first()
    )

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if not check_collection_permission(user, collection_id, "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    response = Collection21(
        id=collection.id,
        title=collection.title,
        description=collection.description,
        # No alias in TAXII 2.1
        can_read=collection.can_read,
        can_write=collection.can_write and check_collection_permission(user, collection_id, "write"),
        media_types=collection.media_types or [],
        x_mitre_contents=collection.x_mitre_contents,
        x_mitre_version=collection.x_mitre_version,
    )
    return JSONResponse(content=response.model_dump(), media_type=TAXII_21_MEDIA_TYPE)


@app.get("/taxii21/{api_root}/collections/{collection_id}/objects/")
async def get_objects_21(
    api_root: str,
    collection_id: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_auth),
    added_after: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    next: str | None = Query(None),  # Pagination token
    match_id: str | None = Query(None, alias="match[id]"),
    match_type: str | None = Query(None, alias="match[type]"),
    match_version: str | None = Query(None, alias="match[version]"),
):
    """TAXII 2.1 Get objects - returns envelope."""
    collection = (
        db.query(Collection).filter(and_(Collection.id == collection_id, Collection.api_root_id == api_root)).first()
    )

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if not check_collection_permission(user, collection_id, "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Handle pagination token
    offset = 0
    if next:
        try:
            offset = int(next)
        except ValueError:
            pass

    # Query objects with filters
    query = (
        db.query(STIXObject)
        .join(collection_objects, STIXObject.id == collection_objects.c.object_id)
        .filter(collection_objects.c.collection_id == collection_id)
    )

    query = apply_filters(query, added_after, match_id, match_type, match_version)

    # Get total count for pagination
    total_count = query.count()

    # Apply pagination
    objects = query.offset(offset).limit(limit).all()

    # Check if more objects available
    has_more = (offset + len(objects)) < total_count
    next_token = str(offset + limit) if has_more else None

    # Create envelope
    envelope = Envelope21(
        more=has_more,
        next=next_token,
        objects=[obj.object_data for obj in objects],
    )

    return JSONResponse(
        content=envelope.model_dump(),
        media_type=TAXII_21_MEDIA_TYPE,  # TAXII 2.1 envelopes use TAXII media type
    )


@app.post("/taxii21/{api_root}/collections/{collection_id}/objects/")
async def add_objects_21(
    api_root: str,
    collection_id: str,
    request: AddObjectsRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_auth),
):
    """TAXII 2.1 Add objects."""
    collection = (
        db.query(Collection).filter(and_(Collection.id == collection_id, Collection.api_root_id == api_root)).first()
    )

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if not check_collection_permission(user, collection_id, "write"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Create status object
    status_obj = Status(
        id=f"status--{uuid.uuid4()}",
        status="complete",
        request_timestamp=datetime.utcnow(),
        total_count=str(len(request.objects)),
        success_count="0",
        failure_count="0",
    )

    successes = []
    failures = []

    # Process objects
    for obj_data in request.objects:
        try:
            # Check if object exists
            existing = db.query(STIXObject).filter(STIXObject.id == obj_data.get("id")).first()

            if not existing:
                # Create new object
                stix_obj = STIXObject(
                    id=obj_data.get("id", f"indicator--{uuid.uuid4()}"),
                    type=obj_data.get("type", "indicator"),
                    spec_version=obj_data.get("spec_version", "2.1"),
                    created=datetime.fromisoformat(obj_data.get("created", datetime.utcnow().isoformat())),
                    modified=datetime.fromisoformat(obj_data.get("modified", datetime.utcnow().isoformat())),
                    object_data=obj_data,
                )
                db.add(stix_obj)
                collection.objects.append(stix_obj)
                successes.append({"id": stix_obj.id})
            else:
                # Update existing
                existing.modified = datetime.utcnow()
                existing.object_data = obj_data
                successes.append({"id": existing.id})

        except Exception as e:
            failures.append({"id": obj_data.get("id", "unknown"), "message": str(e)})

    status_obj.success_count = str(len(successes))
    status_obj.failure_count = str(len(failures))
    status_obj.successes = successes
    status_obj.failures = failures

    db.add(status_obj)
    db.commit()

    response = Status21(
        id=status_obj.id,
        status=status_obj.status,
        request_timestamp=status_obj.request_timestamp.isoformat() if status_obj.request_timestamp else None,
        total_count=int(status_obj.total_count),
        success_count=int(status_obj.success_count),
        failure_count=int(status_obj.failure_count),
        successes=successes,
        failures=failures,
    )
    return JSONResponse(content=response.model_dump(), media_type=TAXII_21_MEDIA_TYPE)


@app.get("/taxii21/{api_root}/collections/{collection_id}/manifest/")
async def get_manifest_21(
    api_root: str,
    collection_id: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_auth),
    added_after: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    next: str | None = Query(None),  # Pagination token
    match_id: str | None = Query(None, alias="match[id]"),
    match_type: str | None = Query(None, alias="match[type]"),
    match_version: str | None = Query(None, alias="match[version]"),
):
    """TAXII 2.1 Get manifest - returns envelope."""
    collection = (
        db.query(Collection).filter(and_(Collection.id == collection_id, Collection.api_root_id == api_root)).first()
    )

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if not check_collection_permission(user, collection_id, "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Handle pagination token
    offset = 0
    if next:
        try:
            offset = int(next)
        except ValueError:
            pass

    # Query objects with filters
    query = (
        db.query(STIXObject, collection_objects.c.date_added)
        .join(collection_objects, STIXObject.id == collection_objects.c.object_id)
        .filter(collection_objects.c.collection_id == collection_id)
    )

    query = apply_filters(query, added_after, match_id, match_type, match_version)

    # Get total count for pagination
    total_count = query.count()

    # Apply pagination
    results = query.offset(offset).limit(limit).all()

    # Check if more objects available
    has_more = (offset + len(results)) < total_count
    next_token = str(offset + limit) if has_more else None

    manifest_entries = []
    for obj, date_added in results:
        manifest_entries.append(
            ManifestEntry21(
                id=obj.id,
                date_added=date_added.isoformat() if date_added else None,
                version=obj.version.isoformat() if obj.version else None,
                versions=None,  # Would need version history tracking
                media_types=["application/stix+json;version=2.1"],
            )
        )

    # Create envelope
    envelope = ManifestEnvelope21(
        more=has_more,
        next=next_token,
        objects=manifest_entries,
    )

    return JSONResponse(
        content=envelope.model_dump(),
        media_type=TAXII_21_MEDIA_TYPE,  # Use correct TAXII 2.1 media type
    )


# Status endpoints
@app.get("/taxii2/{api_root}/status/{status_id}/")
async def get_status_20(
    api_root: str,
    status_id: str,
    db: Session = Depends(get_db),
):
    """TAXII 2.0 Get status."""
    status_obj = db.query(Status).filter(Status.id == status_id).first()
    if not status_obj:
        raise HTTPException(status_code=404, detail="Status not found")

    response = Status20(
        id=status_obj.id,
        status=status_obj.status,
        total_count=int(status_obj.total_count),
        success_count=int(status_obj.success_count),
        failure_count=int(status_obj.failure_count),
        pending_count=int(status_obj.pending_count),
        successes=status_obj.successes or [],
        failures=status_obj.failures or [],
        pendings=status_obj.pendings or [],
    )
    return JSONResponse(content=response.model_dump(), media_type=TAXII_20_MEDIA_TYPE)


@app.get("/taxii21/{api_root}/status/{status_id}/")
async def get_status_21(
    api_root: str,
    status_id: str,
    db: Session = Depends(get_db),
):
    """TAXII 2.1 Get status."""
    status_obj = db.query(Status).filter(Status.id == status_id).first()
    if not status_obj:
        raise HTTPException(status_code=404, detail="Status not found")

    response = Status21(
        id=status_obj.id,
        status=status_obj.status,
        request_timestamp=status_obj.request_timestamp.isoformat() if status_obj.request_timestamp else None,
        total_count=int(status_obj.total_count),
        success_count=int(status_obj.success_count),
        failure_count=int(status_obj.failure_count),
        pending_count=int(status_obj.pending_count),
        successes=status_obj.successes or [],
        failures=status_obj.failures or [],
        pendings=status_obj.pendings or [],
    )
    return JSONResponse(content=response.model_dump(), media_type=TAXII_21_MEDIA_TYPE)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "TAXII Test Server"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
