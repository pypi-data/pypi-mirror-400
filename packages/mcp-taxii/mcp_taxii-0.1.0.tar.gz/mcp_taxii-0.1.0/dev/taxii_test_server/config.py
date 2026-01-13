"""Configuration for TAXII test server."""

import os
from typing import Optional

# Server Configuration
SERVER_TITLE = os.getenv("TAXII_SERVER_TITLE", "Test TAXII Server")
SERVER_DESCRIPTION = os.getenv("TAXII_SERVER_DESCRIPTION", "A test TAXII server supporting both 2.0 and 2.1")
SERVER_CONTACT = os.getenv("TAXII_SERVER_CONTACT", "admin@example.com")

# Default Authentication Credentials
DEFAULT_USERS = {
    "test_user": {
        "password": os.getenv("TAXII_TEST_USER_PASSWORD", "test_password"),
        "permissions": {
            "can_read": ["*"],  # Can read all collections
            "can_write": ["collection-1", "collection-1-v20"],  # Can write to specific collections
        },
        "description": "Test user with read-all, write-some permissions",
    },
    "readonly_user": {
        "password": os.getenv("TAXII_READONLY_USER_PASSWORD", "readonly_password"),
        "permissions": {
            "can_read": ["collection-1", "collection-2", "collection-1-v20", "collection-2-v20"],
            "can_write": [],  # Cannot write to any collection
        },
        "description": "Read-only user",
    },
    "admin": {
        "password": os.getenv("TAXII_ADMIN_PASSWORD", "admin_password"),
        "permissions": {
            "can_read": ["*"],  # Can read all collections
            "can_write": ["*"],  # Can write to all collections
        },
        "description": "Administrator with full access",
    },
}

# Add a default API user for programmatic access
DEFAULT_USERS["api_user"] = {
    "password": os.getenv("TAXII_API_USER_PASSWORD", "api_key_12345"),
    "permissions": {"can_read": ["*"], "can_write": ["*"]},
    "description": "API user for programmatic access",
}

# Authentication Settings
ALLOW_ANONYMOUS_READ = os.getenv("TAXII_ALLOW_ANONYMOUS_READ", "false").lower() == "true"
REQUIRE_AUTH_FOR_DISCOVERY = os.getenv("TAXII_REQUIRE_AUTH_FOR_DISCOVERY", "false").lower() == "true"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taxii_test.db")

# API Configuration
DEFAULT_API_ROOT_20 = os.getenv("TAXII_API_ROOT_20", "http://localhost:8000/taxii2/api1/")
DEFAULT_API_ROOT_21 = os.getenv("TAXII_API_ROOT_21", "http://localhost:8000/taxii21/api1/")

# Collection Configuration
DEFAULT_COLLECTIONS = [
    {
        "id": "collection-1",
        "title": "Malware Indicators",
        "description": "Collection of malware indicators",
        "can_read": True,
        "can_write": True,
    },
    {
        "id": "collection-2",
        "title": "Threat Actors",
        "description": "Collection of threat actor information",
        "can_read": True,
        "can_write": False,
    },
]


def get_user_credentials(username: str) -> Optional[dict]:
    """Get credentials for a specific user."""
    return DEFAULT_USERS.get(username)


def validate_user(username: str, password: str) -> bool:
    """Validate user credentials."""
    user = get_user_credentials(username)
    if not user:
        return False
    return user["password"] == password


def get_user_permissions(username: str) -> dict:
    """Get permissions for a specific user."""
    user = get_user_credentials(username)
    if not user:
        return {"can_read": [], "can_write": []}
    return user["permissions"]


def can_read_collection(username: str, collection_id: str) -> bool:
    """Check if user can read a collection."""
    if ALLOW_ANONYMOUS_READ and not username:
        return True

    permissions = get_user_permissions(username)
    can_read = permissions.get("can_read", [])

    # Check for wildcard permission
    if "*" in can_read:
        return True

    return collection_id in can_read


def can_write_collection(username: str, collection_id: str) -> bool:
    """Check if user can write to a collection."""
    if not username:
        return False  # Anonymous users cannot write

    permissions = get_user_permissions(username)
    can_write = permissions.get("can_write", [])

    # Check for wildcard permission
    if "*" in can_write:
        return True

    return collection_id in can_write
