"""Seed data script for TAXII test server."""

import json
import uuid
from datetime import datetime, timedelta

from dev.taxii_test_server.auth import hash_password
from dev.taxii_test_server.config import DEFAULT_USERS, SERVER_TITLE, SERVER_DESCRIPTION, SERVER_CONTACT
from dev.taxii_test_server.database import get_db_session
from dev.taxii_test_server.models import APIRoot, Collection, Discovery, STIXObject, User


def seed_database():
    """Populate database with test data."""
    with get_db_session() as db:
        # Check if already seeded
        if db.query(Discovery).first():
            print("Database already seeded")
            return

        # Create separate discoveries for TAXII 2.0 and 2.1
        discovery_20 = Discovery(
            id="discovery-20",
            title=SERVER_TITLE,
            description=SERVER_DESCRIPTION,
            contact=SERVER_CONTACT,
            default="http://localhost:8000/taxii2/api1-v20/",
        )
        db.add(discovery_20)

        discovery_21 = Discovery(
            id="discovery-21",
            title=SERVER_TITLE,
            description=SERVER_DESCRIPTION,
            contact=SERVER_CONTACT,
            default="http://localhost:8000/taxii21/api1/",
        )
        db.add(discovery_21)

        # Create API roots - URLs must match the {api_root} path parameter in FastAPI routes
        api_root_20 = APIRoot(
            id="api1-v20",
            url="http://localhost:8000/taxii2/api1-v20/",  # URL path matches the ID
            title="TAXII 2.0 API Root",
            description="API root for TAXII 2.0 testing",
            versions=["taxii-2.0"],
            max_content_length="10485760",
            discovery_id="discovery-20",
        )
        db.add(api_root_20)

        api_root_21 = APIRoot(
            id="api1",
            url="http://localhost:8000/taxii21/api1/",  # URL path matches the ID
            title="TAXII 2.1 API Root",
            description="API root for TAXII 2.1 testing",
            versions=["taxii-2.1"],
            max_content_length="10485760",
            discovery_id="discovery-21",
        )
        db.add(api_root_21)

        # Create collections for both API roots
        # Collections for TAXII 2.0 root
        collection1_v20 = Collection(
            id="collection-1-v20",
            title="Malware Indicators",
            description="Collection of malware indicators",
            alias="malware-indicators",  # For TAXII 2.0
            can_read=True,
            can_write=True,
            media_types=["application/stix+json;version=2.0"],
            api_root_id="api1-v20",
            x_mitre_contents=["attack-pattern", "malware"],
            x_mitre_version="1.0",
        )
        db.add(collection1_v20)

        collection2_v20 = Collection(
            id="collection-2-v20",
            title="Threat Actors",
            description="Collection of threat actor information",
            alias="threat-actors",  # For TAXII 2.0
            can_read=True,
            can_write=False,
            media_types=["application/stix+json;version=2.0"],
            api_root_id="api1-v20",
        )
        db.add(collection2_v20)

        # Collections for TAXII 2.1 root
        collection1_v21 = Collection(
            id="collection-1",
            title="Malware Indicators",
            description="Collection of malware indicators",
            alias=None,  # No alias in TAXII 2.1
            can_read=True,
            can_write=True,
            media_types=["application/stix+json;version=2.1"],
            api_root_id="api1",
            x_mitre_contents=["attack-pattern", "malware"],
            x_mitre_version="1.0",
        )
        db.add(collection1_v21)

        collection2_v21 = Collection(
            id="collection-2",
            title="Threat Actors",
            description="Collection of threat actor information",
            alias=None,  # No alias in TAXII 2.1
            can_read=True,
            can_write=False,
            media_types=["application/stix+json;version=2.1"],
            api_root_id="api1",
        )
        db.add(collection2_v21)

        # Create sample STIX objects
        now = datetime.utcnow()
        stix_objects = [
            {
                "id": "indicator--01234567-89ab-cdef-0123-456789abcdef",
                "type": "indicator",
                "spec_version": "2.1",
                "created": (now - timedelta(days=30)).isoformat() + "Z",
                "modified": (now - timedelta(days=10)).isoformat() + "Z",
                "name": "Malicious IP",
                "description": "Known malicious IP address",
                "pattern": "[network-traffic:dst_ref.type = 'ipv4-addr' AND network-traffic:dst_ref.value = '10.0.0.1']",
                "pattern_type": "stix",
                "valid_from": (now - timedelta(days=30)).isoformat() + "Z",
                "labels": ["malicious-activity"],
            },
            {
                "id": "malware--fedcba98-7654-3210-fedc-ba9876543210",
                "type": "malware",
                "spec_version": "2.1",
                "created": (now - timedelta(days=20)).isoformat() + "Z",
                "modified": (now - timedelta(days=5)).isoformat() + "Z",
                "name": "Poison Ivy",
                "description": "Poison Ivy malware variant",
                "malware_types": ["remote-access-trojan"],
                "is_family": False,
            },
            {
                "id": "threat-actor--11111111-2222-3333-4444-555555555555",
                "type": "threat-actor",
                "spec_version": "2.1",
                "created": (now - timedelta(days=60)).isoformat() + "Z",
                "modified": (now - timedelta(days=15)).isoformat() + "Z",
                "name": "APT28",
                "description": "Russian threat actor group",
                "threat_actor_types": ["nation-state"],
                "aliases": ["Sofacy", "Pawn Storm", "Fancy Bear"],
                "first_seen": "2007-01-01T00:00:00.000Z",
                "resource_level": "government",
                "primary_motivation": "organizational-gain",
            },
            {
                "id": "attack-pattern--22222222-3333-4444-5555-666666666666",
                "type": "attack-pattern",
                "spec_version": "2.1",
                "created": (now - timedelta(days=45)).isoformat() + "Z",
                "modified": (now - timedelta(days=20)).isoformat() + "Z",
                "name": "Spear Phishing",
                "description": "Targeted phishing attack",
                "kill_chain_phases": [
                    {
                        "kill_chain_name": "mitre-attack",
                        "phase_name": "initial-access",
                    }
                ],
            },
            {
                "id": "campaign--33333333-4444-5555-6666-777777777777",
                "type": "campaign",
                "spec_version": "2.1",
                "created": (now - timedelta(days=90)).isoformat() + "Z",
                "modified": (now - timedelta(days=30)).isoformat() + "Z",
                "name": "Operation Aurora",
                "description": "Cyber espionage campaign",
                "aliases": ["Aurora", "Hydraq"],
                "first_seen": "2009-01-01T00:00:00.000Z",
                "last_seen": "2010-01-01T00:00:00.000Z",
                "objective": "intellectual-property-theft",
            },
        ]

        # Add STIX objects to database
        for obj_data in stix_objects:
            stix_obj = STIXObject(
                id=obj_data["id"],
                type=obj_data["type"],
                spec_version=obj_data.get("spec_version", "2.1"),
                created=datetime.fromisoformat(obj_data["created"].replace("Z", "+00:00")),
                modified=datetime.fromisoformat(obj_data["modified"].replace("Z", "+00:00")),
                object_data=obj_data,
                version=datetime.fromisoformat(obj_data["modified"].replace("Z", "+00:00")),
            )
            db.add(stix_obj)

            # Add to collections based on type (both 2.0 and 2.1)
            if obj_data["type"] in ["indicator", "malware", "attack-pattern"]:
                collection1_v20.objects.append(stix_obj)
                collection1_v21.objects.append(stix_obj)
            if obj_data["type"] in ["threat-actor", "campaign"]:
                collection2_v20.objects.append(stix_obj)
                collection2_v21.objects.append(stix_obj)

        # Create test users from configuration
        user_id = 1
        for username, user_config in DEFAULT_USERS.items():
            # Convert permission format
            read_perms = user_config["permissions"]["can_read"]
            write_perms = user_config["permissions"]["can_write"]

            # Handle wildcard permissions
            collections_read = None if "*" in read_perms else read_perms
            collections_write = None if "*" in write_perms else write_perms

            user = User(
                id=f"user-{user_id}",
                username=username,
                password_hash=hash_password(user_config["password"]),
                is_active=True,
                collections_read=collections_read,
                collections_write=collections_write,
            )
            db.add(user)
            user_id += 1

        # Commit all changes
        db.commit()
        print("Database seeded successfully!")
        print("\nTest Users:")
        for username, user_config in DEFAULT_USERS.items():
            print(f"  - Username: {username}, Password: {user_config['password']}")
            print(f"    {user_config['description']}")
        print("\nCollections:")
        print("  - collection-1: Malware Indicators (read/write)")
        print("  - collection-2: Threat Actors (read-only)")
        print(f"\nAdded {len(stix_objects)} STIX objects")


if __name__ == "__main__":
    from dev.taxii_test_server.database import init_db

    # Initialize database
    init_db()

    # Seed data
    seed_database()
