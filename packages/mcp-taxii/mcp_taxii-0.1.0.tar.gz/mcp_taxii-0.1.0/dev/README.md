# Development Tools

This directory contains development and testing tools for the MCP TAXII project.

## Contents

### taxii_test_server/
A fully compliant TAXII 2.0/2.1 test server built with FastAPI for testing the MCP TAXII client implementation.

## Running the TAXII Test Server

### Quick Start

```bash
# From the project root - run with default settings (port 8000)
python dev/taxii_test_server/run_server.py

# Run on a custom port
python dev/taxii_test_server/run_server.py --port 8080

# Run on port 9000 without auto-reload
python dev/taxii_test_server/run_server.py -p 9000 --no-reload

# See all options
python dev/taxii_test_server/run_server.py --help
```

Or using Docker:
```bash
cd dev/taxii_test_server
docker-compose up
```

The server will be available at http://localhost:8000 (or your specified port)

### Features
- Full TAXII 2.0 and 2.1 compliance
- SQLite database with pre-loaded STIX data
- HTTP Basic Authentication
- Support for all TAXII query parameters
- Proper envelope vs bundle response formats

### Test Credentials
- `test_user` / `test_password` - Read all, write to collection-1
- `readonly_user` / `readonly_password` - Read only access
- `admin` / `admin_password` - Full access

See `dev/taxii_test_server/README.md` for full documentation.