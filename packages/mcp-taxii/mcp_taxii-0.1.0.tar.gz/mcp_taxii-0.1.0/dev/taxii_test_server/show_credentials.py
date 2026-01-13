#!/usr/bin/env python
"""Display the configured credentials for the TAXII test server."""

import os
import sys
from pathlib import Path
from tabulate import tabulate

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dev.taxii_test_server.config import DEFAULT_USERS, ALLOW_ANONYMOUS_READ, REQUIRE_AUTH_FOR_DISCOVERY


def main():
    print("\n" + "=" * 60)
    print("TAXII Test Server - Authentication Configuration")
    print("=" * 60)

    # General settings
    print("\nGeneral Settings:")
    print(f"  - Allow Anonymous Read: {ALLOW_ANONYMOUS_READ}")
    print(f"  - Require Auth for Discovery: {REQUIRE_AUTH_FOR_DISCOVERY}")

    # User credentials
    print("\nConfigured Users:")
    print("-" * 60)

    table_data = []
    for username, user_config in DEFAULT_USERS.items():
        permissions = user_config["permissions"]
        read_perm = "All" if "*" in permissions["can_read"] else f"{len(permissions['can_read'])} collections"
        write_perm = "All" if "*" in permissions["can_write"] else f"{len(permissions['can_write'])} collections"

        table_data.append([username, user_config["password"], read_perm, write_perm, user_config["description"]])

    headers = ["Username", "Password", "Read Access", "Write Access", "Description"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    print("\n" + "=" * 60)
    print("Environment Variables:")
    print("-" * 60)
    print("You can override these defaults by setting environment variables:")
    print("  TAXII_TEST_USER_PASSWORD    - Change test_user password")
    print("  TAXII_READONLY_USER_PASSWORD - Change readonly_user password")
    print("  TAXII_ADMIN_PASSWORD         - Change admin password")
    print("  TAXII_API_USER_PASSWORD      - Change api_user password")
    print("  TAXII_ALLOW_ANONYMOUS_READ   - Set to 'true' for anonymous read access")
    print("\nOr create a .env file in the server directory with these settings.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
