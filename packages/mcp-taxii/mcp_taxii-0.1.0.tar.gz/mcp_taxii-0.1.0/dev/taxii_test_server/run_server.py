#!/usr/bin/env python
"""Script to run the TAXII test server."""

import argparse
import sys
import os
from pathlib import Path

# Load environment variables from .env file if it exists
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded configuration from {env_path}")
else:
    # Try .env.example as fallback
    env_example = Path(__file__).parent / ".env.example"
    if env_example.exists():
        print(f"No .env file found. Using defaults from .env.example")
        print("Copy .env.example to .env to customize settings.")

# Add parent directory to path so we can import from tests
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.chdir(Path(__file__).parent)

from dev.taxii_test_server.database import init_db
from dev.taxii_test_server.seed_data import seed_database

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the TAXII test server")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to run the server on (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload on code changes")
    parser.add_argument("--skip-seed", action="store_true", help="Skip seeding the database with test data")

    args = parser.parse_args()

    print("Initializing database...")
    init_db()

    if not args.skip_seed:
        print("Seeding database with test data...")
        seed_database()
    else:
        print("Skipping database seeding (--skip-seed flag provided)")

    print(f"\nStarting TAXII test server on http://localhost:{args.port}")
    print("Press CTRL+C to stop\n")

    import uvicorn

    uvicorn.run("dev.taxii_test_server.server:app", host=args.host, port=args.port, reload=not args.no_reload)
