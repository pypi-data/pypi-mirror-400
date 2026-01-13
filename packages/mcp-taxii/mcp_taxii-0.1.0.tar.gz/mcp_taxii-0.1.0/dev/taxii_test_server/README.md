# TAXII 2.0/2.1 Test Server

A FastAPI-based TAXII server supporting both 2.0 and 2.1 specifications for testing the MCP TAXII client.

## Features

- Full TAXII 2.0 and 2.1 compliance
- SQLite database backend
- HTTP Basic Authentication
- Sample STIX data pre-loaded
- Support for all TAXII query parameters
- Proper envelope vs bundle responses
- Docker support

## Quick Start

### Option 1: Run with Python

From the project root directory:
```bash
# Run with default settings (port 8000)
python dev/taxii_test_server/run_server.py

# Run on a custom port
python dev/taxii_test_server/run_server.py --port 8080

# Run without auto-reload
python dev/taxii_test_server/run_server.py --no-reload

# Run without seeding test data (e.g., if database already exists)
python dev/taxii_test_server/run_server.py --skip-seed

# Combine options
python dev/taxii_test_server/run_server.py -p 9000 --host localhost --no-reload
```

#### Command Line Options
- `--port`, `-p`: Port to run the server on (default: 8000)
- `--host`: Host to bind the server to (default: 0.0.0.0)
- `--no-reload`: Disable auto-reload on code changes
- `--skip-seed`: Skip seeding the database with test data

### Option 2: Run with Docker

```bash
docker-compose up
```

The server will be available at http://localhost:8000 (or your specified port)

## Endpoints

### TAXII 2.0
- Discovery: `GET /taxii2/`
- API Root: `GET /taxii2/api1/`
- Collections: `GET /taxii2/api1/collections/`
- Collection: `GET /taxii2/api1/collections/{id}/`
- Objects: `GET /taxii2/api1/collections/{id}/objects/`
- Add Objects: `POST /taxii2/api1/collections/{id}/objects/`
- Manifest: `GET /taxii2/api1/collections/{id}/manifest/`
- Status: `GET /taxii2/api1/status/{id}/`

### TAXII 2.1
- Discovery: `GET /taxii21/`
- API Root: `GET /taxii21/api1/`
- Collections: `GET /taxii21/api1/collections/`
- Collection: `GET /taxii21/api1/collections/{id}/`
- Objects: `GET /taxii21/api1/collections/{id}/objects/`
- Add Objects: `POST /taxii21/api1/collections/{id}/objects/`
- Manifest: `GET /taxii21/api1/collections/{id}/manifest/`
- Status: `GET /taxii21/api1/status/{id}/`

## Test Users

| Username | Password | Permissions |
|----------|----------|-------------|
| test_user | test_password | Read all, write to collection-1 |
| readonly_user | readonly_password | Read only |
| admin | admin_password | Full access |

## Collections

1. **collection-1: Malware Indicators**
   - Contains: indicators, malware, attack patterns
   - Permissions: read/write

2. **collection-2: Threat Actors**
   - Contains: threat actors, campaigns
   - Permissions: read-only

## Query Parameters

All object retrieval endpoints support:
- `added_after`: RFC3339 timestamp
- `limit`: Maximum results (1-1000)
- `match[id]`: Filter by object IDs
- `match[type]`: Filter by object types
- `match[version]`: Version filtering

TAXII 2.1 additionally supports:
- `next`: Pagination token

## Key Differences

### TAXII 2.0
- Returns STIX bundles from objects endpoint
- Collections have `alias` field
- Manifest returns list
- No `default` field in discovery

### TAXII 2.1
- Returns envelopes with pagination from objects endpoint
- No `alias` field in collections
- Manifest returns envelope
- Includes `default` field in discovery
- Status includes `request_timestamp`

## Testing with MCP TAXII Client

```python
from mcp_taxii.server import initialize_taxii, get_collections, get_collection_objects

# Initialize client
await initialize_taxii(
    url="http://localhost:8000/taxii21/",
    username="test_user",
    password="test_password",
    version="2.1"
)

# Get collections
collections = await get_collections("api1")

# Get objects
objects = await get_collection_objects("collection-1")
```

## Development

The server uses:
- **FastAPI** for the web framework
- **SQLAlchemy** for ORM
- **SQLite** for database
- **Pydantic** for data validation

## Health Check

```bash
curl http://localhost:8000/health
```