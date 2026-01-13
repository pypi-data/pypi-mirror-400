"""Authentication middleware for TAXII server."""

import base64
import hashlib
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from dev.taxii_test_server.config import ALLOW_ANONYMOUS_READ
from dev.taxii_test_server.database import get_db
from dev.taxii_test_server.models import User

security = HTTPBasic()


def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(plain_password) == hashed_password


def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    db: Session = Depends(get_db),
) -> User | None:
    """Get current authenticated user."""
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


def optional_auth(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """Optional authentication - returns None if no auth provided."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    try:
        scheme, credentials = auth_header.split(" ", 1)
        if scheme.lower() != "basic":
            return None

        decoded = base64.b64decode(credentials).decode("utf-8")
        username, password = decoded.split(":", 1)

        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            return user if user.is_active else None
    except Exception:
        pass

    return None


def check_collection_permission(user: User | None, collection_id: str, permission: str = "read") -> bool:
    """Check if user has permission for a collection."""
    if not user:
        # Allow anonymous read access if configured
        if permission == "read" and ALLOW_ANONYMOUS_READ:
            return True
        return False  # No anonymous write access

    if permission == "read":
        allowed_collections = user.collections_read
    elif permission == "write":
        allowed_collections = user.collections_write
    else:
        return False

    # If no specific collections configured (None), allow all
    if allowed_collections is None:
        return True

    return collection_id in allowed_collections
