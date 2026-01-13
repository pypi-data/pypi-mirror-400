# MCP TAXII

A Model Context Protocol (MCP) server that acts as a TAXII client for AI agents, enabling them to interact with Threat Intelligence platforms using the TAXII protocol.

## Overview

MCP TAXII provides a bridge between AI agents and TAXII (Trusted Automated eXchange of Intelligence Information) servers, allowing AI systems to:
- Query threat intelligence data
- Retrieve STIX objects from TAXII collections
- Discover available threat intelligence sources
- Add new threat intelligence to collections (when permitted)

The server supports both TAXII 2.0 and TAXII 2.1 protocols.

## Features

- **TAXII 2.0 & 2.1 Support**: Compatible with both major TAXII protocol versions
- **FastMCP Framework**: Built on FastMCP for efficient MCP server implementation
- **Authentication Support**: Handles username/password authentication for TAXII servers
- **Collection Management**: Browse, query, and interact with TAXII collections
- **STIX Object Operations**: Retrieve and add STIX threat intelligence objects
- **Pagination Support**: Handles large datasets with built-in pagination (TAXII 2.1)
- **Environment Variable Configuration**: Easy setup via environment variables

## Quick Start with uvx (No Installation Required)

`uvx` is a tool that allows you to run Python packages without installing them. This is perfect for:
- **Quick testing** without cluttering your system
- **Running in CI/CD** pipelines
- **Isolated execution** without dependency conflicts
- **Always running the latest version**

### Prerequisites for uvx

```bash
# Install uv (which includes uvx)
pip install uv
# or
pipx install uv
```

### Running Directly from PyPI

Once published to PyPI, you can run MCP TAXII instantly:

```bash
# Run the latest version
uvx mcp-taxii

# Run a specific version
uvx mcp-taxii==0.1.0

# With environment configuration
MCPTAXII_HOST="http://localhost:8000/taxii21/" \
MCPTAXII_USERNAME="admin" \
MCPTAXII_PASSWORD="admin_password" \
uvx mcp-taxii
```

### Running from GitHub

For development or unreleased versions:

```bash
# Run directly from GitHub main branch
uvx --from git+https://github.com/yourusername/mcp_taxii mcp-taxii

# Run from a specific branch or tag
uvx --from git+https://github.com/yourusername/mcp_taxii@develop mcp-taxii
uvx --from git+https://github.com/yourusername/mcp_taxii@v0.2.0 mcp-taxii

# With environment variables
MCPTAXII_HOST="https://your-server.com/taxii2/" \
MCPTAXII_USERNAME="user" \
MCPTAXII_PASSWORD="pass" \
uvx --from git+https://github.com/yourusername/mcp_taxii mcp-taxii
```

### Running from Local Directory

For development:

```bash
# From the project directory
uvx --from . mcp-taxii

# From another directory
uvx --from /path/to/mcp_taxii mcp-taxii
```

## Installation

### Prerequisites

- Python 3.11 or higher
- `uv` package manager (install with `pip install uv`)
- A TAXII server to connect to (or use the included test server)

### Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd mcp_taxii
```

2. **Install uv if not already installed:**
```bash
# Using pip
pip install uv

# Or using pipx (recommended)
pipx install uv
```

3. **Install dependencies:**
```bash
uv sync --extra dev
```

4. **Configure environment variables:**

Copy the example environment file and update with your TAXII server credentials:

```bash
cp .env.example .env
# Edit .env with your TAXII server details
```

The `.env` file should contain:

```bash
# .env file
MCPTAXII_HOST="https://your-taxii-server.com/taxii2/"
MCPTAXII_USERNAME="your-username"
MCPTAXII_PASSWORD="your-password"
TAXII_VERSION="2.1"  # or "2.0" depending on your server
```

Alternatively, export them directly:

```bash
export MCPTAXII_HOST="https://your-taxii-server.com/taxii2/"
export MCPTAXII_USERNAME="your-username"
export MCPTAXII_PASSWORD="your-password"
export TAXII_VERSION="2.1"
```

### Using the Test Server (Optional)

If you don't have a TAXII server, you can use the included test server:

```bash
# Start the test server (in a separate terminal)
python dev/taxii_test_server/run_server.py --port 8000

# Configure your .env to point to the test server
MCPTAXII_HOST="http://localhost:8000/taxii21/"
MCPTAXII_USERNAME="admin"
MCPTAXII_PASSWORD="admin_password"
TAXII_VERSION="2.1"
```

## MCP Server Setup

### Running as Standalone MCP Server

```bash
# Run the MCP server
uv run python -m mcp_taxii.server
```

The server will start and listen for MCP protocol connections.

### Integrating with Claude Desktop

To use this MCP server with Claude Desktop, you have multiple options:

#### Option 1: Using uvx (Recommended - No Installation)

```json
{
  "mcpServers": {
    "mcp-taxii": {
      "command": "uvx",
      "args": ["mcp-taxii"],
      "env": {
        "MCPTAXII_HOST": "https://your-taxii-server.com/taxii2/",
        "MCPTAXII_USERNAME": "your-username",
        "MCPTAXII_PASSWORD": "your-password",
        "TAXII_VERSION": "2.1"
      }
    }
  }
}
```

#### Option 2: From GitHub with uvx

```json
{
  "mcpServers": {
    "mcp-taxii": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/yourusername/mcp_taxii", "mcp-taxii"],
      "env": {
        "MCPTAXII_HOST": "https://your-taxii-server.com/taxii2/",
        "MCPTAXII_USERNAME": "your-username",
        "MCPTAXII_PASSWORD": "your-password",
        "TAXII_VERSION": "2.1"
      }
    }
  }
}
```

#### Option 3: Local Installation

```json
{
  "mcpServers": {
    "mcp-taxii": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_taxii.server"],
      "cwd": "/path/to/mcp_taxii",
      "env": {
        "MCPTAXII_HOST": "https://your-taxii-server.com/taxii2/",
        "MCPTAXII_USERNAME": "your-username",
        "MCPTAXII_PASSWORD": "your-password",
        "TAXII_VERSION": "2.1"
      }
    }
  }
}
```

4. **Restart Claude Desktop** to load the MCP server

### Configuration Options

#### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MCPTAXII_HOST` | Base URL of your TAXII server | None | Yes* |
| `MCPTAXII_USERNAME` | Authentication username | None | Yes* |
| `MCPTAXII_PASSWORD` | Authentication password | None | Yes* |
| `TAXII_VERSION` | TAXII protocol version ("2.0" or "2.1") | "2.1" | No |
| `TAXII_VERIFY_SSL` | Verify SSL certificates | "true" | No |
| `TAXII_TIMEOUT` | Request timeout in seconds | "30" | No |

*Required unless provided via `initialize_taxii` tool

### Verifying the Setup

Once configured, you can verify the MCP server is working by asking Claude:

```
"Initialize a connection to the TAXII server and show me what collections are available"
```

Claude will use the MCP tools to connect to your TAXII server and list the available threat intelligence collections.

## Quick Start Guide

### 1. Test with Local Server Using uvx

```bash
# Terminal 1: Start test TAXII server
python dev/taxii_test_server/run_server.py

# Terminal 2: Run MCP server with uvx
MCPTAXII_HOST="http://localhost:8000/taxii21/" \
MCPTAXII_USERNAME="admin" \
MCPTAXII_PASSWORD="admin_password" \
uvx mcp-taxii
```

### 2. Connect with Production TAXII Server Using uvx

```bash
# Option A: With environment variables
MCPTAXII_HOST="https://your-taxii-server.com/taxii2/" \
MCPTAXII_USERNAME="your-username" \
MCPTAXII_PASSWORD="your-password" \
TAXII_VERSION="2.1" \
uvx mcp-taxii

# Option B: With .env file
cat > .env << EOF
MCPTAXII_HOST="https://your-taxii-server.com/taxii2/"
MCPTAXII_USERNAME="your-username"
MCPTAXII_PASSWORD="your-password"
TAXII_VERSION="2.1"
EOF

uvx mcp-taxii  # Will automatically load .env file
```

### 3. Traditional Installation Method

```bash
# Clone and install
git clone <repository-url>
cd mcp_taxii
uv sync --extra dev

# Run with uv
uv run python -m mcp_taxii.server
```

## Troubleshooting

### Common Issues

1. **Connection refused error:**
   - Ensure your TAXII server is running and accessible
   - Check the MCPTAXII_HOST is correct (including the protocol and path)
   - Verify firewall settings allow the connection

2. **Authentication failed:**
   - Double-check your username and password
   - Ensure credentials are properly set in environment variables
   - Some TAXII servers require specific authentication headers

3. **SSL Certificate errors:**
   - For self-signed certificates, set `TAXII_VERIFY_SSL="false"`
   - Ensure your system has updated CA certificates

4. **No collections returned:**
   - Verify you have permissions to view collections
   - Check if the API root path is correct
   - Try using the `get_discovery()` tool first to see available API roots

5. **MCP server not recognized by Claude:**
   - Ensure the path in `claude_desktop_config.json` is absolute
   - Restart Claude Desktop after configuration changes
   - Check Claude's developer console for error messages

### Available Tools

The MCP TAXII server provides the following tools for AI agents:

#### `initialize_taxii`
Initialize connection to a TAXII server.

Parameters:
- `url` (optional): TAXII server URL
- `username` (optional): Authentication username  
- `password` (optional): Authentication password
- `version`: TAXII version ("2.0" or "2.1", defaults to "2.1")

#### `get_discovery`
Retrieve TAXII server discovery information including available API roots.

#### `get_collections`
List available collections from the TAXII server.

Parameters:
- `api_root` (optional): Specific API root URL

#### `get_collection_objects`
Retrieve STIX objects from a specific collection.

Parameters:
- `collection_id`: ID of the collection to query
- `api_root` (optional): Specific API root URL
- `limit`: Maximum number of objects to retrieve (default: 100)
- `added_after` (optional): ISO timestamp to filter objects added after this time

#### `get_object_manifest`
Get object manifest (metadata) from a collection.

Parameters:
- `collection_id`: ID of the collection
- `api_root` (optional): Specific API root URL
- `limit`: Maximum number of manifest entries (default: 100)

#### `add_objects`
Add STIX objects to a writable collection.

Parameters:
- `collection_id`: ID of the target collection
- `objects`: List of STIX objects to add
- `api_root` (optional): Specific API root URL

### Example Integration

Here's how an AI agent might interact with the MCP TAXII server:

```python
# Initialize connection
await initialize_taxii(
    url="https://intel.example.com/taxii2/",
    username="analyst",
    password="secure_password",
    version="2.1"
)

# Discover available resources
discovery = await get_discovery()

# List collections
collections = await get_collections()

# Retrieve threat indicators
indicators = await get_collection_objects(
    collection_id="indicators-collection",
    limit=50
)

# Add new threat intelligence
new_indicators = [
    {
        "type": "indicator",
        "id": "indicator--" + str(uuid4()),
        "created": "2024-01-01T00:00:00.000Z",
        "modified": "2024-01-01T00:00:00.000Z",
        "pattern": "[file:hashes.MD5 = 'malicious_hash']",
        "valid_from": "2024-01-01T00:00:00.000Z"
    }
]
status = await add_objects("indicators-collection", new_indicators)
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run ruff format src/ tests/
```

### Linting

```bash
uv run ruff check src/ tests/
```

## Project Structure

```
mcp_taxii/
├── docs/                    # Documentation
├── aidocs/                  # AI-specific documentation
│   └── specs/              # TAXII specification docs
├── dev/                     # Development tools
│   └── taxii_test_server/  # Test TAXII server
├── src/
│   └── mcp_taxii/
│       ├── __init__.py
│       ├── server.py       # Main MCP server implementation
│       └── clients/        # TAXII client implementations
│           ├── base.py     # Abstract base client
│           ├── taxii_20.py # TAXII 2.0 client
│           └── taxii_21.py # TAXII 2.1 client
├── tests/                   # Test suite
│   ├── conftest.py         # Shared test fixtures
│   └── test_server.py      # Server tests
├── pyproject.toml          # Project configuration
├── CLAUDE.md               # AI agent instructions
└── README.md               # This file
```

## Test Server

A compliant TAXII 2.0/2.1 test server is available in the `dev/` directory for testing purposes. See [dev/taxii_test_server/README.md](dev/taxii_test_server/README.md) for details.

## License

[Specify your license here]

## Contributing

[Add contribution guidelines if applicable]