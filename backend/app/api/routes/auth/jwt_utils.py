"""
Auth JWT Utilities
Token generation, verification, and password hashing utilities
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
import bcrypt
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Fail-fast JWT_SECRET validation
JWT_SECRET: str = os.environ.get("JWT_SECRET_KEY", "")
if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable is not set. "
        "Configure it in Railway before deploying."
    )

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
REFRESH_TOKEN_EXPIRE_DAYS = 30


def create_access_token(client_data: Dict[str, Any]) -> str:
    """
    Create JWT access token (7-day expiration)

    Args:
        client_data: Client data dict with id, email, role, reseller_id

    Returns:
        Encoded JWT access token

    Token payload:
        - sub: client_id (standard JWT claim for user ID)
        - id: client_id
        - email: client email
        - role: client role (client/reseller/admin)
        - reseller_id: optional reseller UUID
        - exp: expiration timestamp (7 days)
        - iat: issued at timestamp
        - type: "access"
    """
    now = datetime.now(timezone.utc)
    expiration = now + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": client_data["id"],  # Standard JWT "subject" claim
        "id": client_data["id"],
        "email": client_data["email"],
        "role": client_data.get("role", "client"),
        "reseller_id": client_data.get("reseller_id"),
        "exp": expiration,
        "iat": now,
        "type": "access"
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def create_refresh_token(client_id: str) -> str:
    """
    Create JWT refresh token (30-day expiration)

    Args:
        client_id: Client UUID

    Returns:
        Encoded JWT refresh token

    Token payload:
        - sub: client_id
        - exp: expiration timestamp (30 days)
        - iat: issued at timestamp
        - type: "refresh"
    """
    now = datetime.now(timezone.utc)
    expiration = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": client_id,
        "exp": expiration,
        "iat": now,
        "type": "refresh"
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_access_token(token: str) -> str:
    """
    Verify JWT access token and extract client_id

    Args:
        token: JWT access token string

    Returns:
        Client UUID from token payload

    Raises:
        HTTPException 401: Invalid token, expired, or wrong type
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type. Expected access token."
            )

        client_id = payload.get("sub")
        if not client_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return client_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid access token: {e}")
        raise HTTPException(status_code=401, detail="Invalid access token")


def verify_refresh_token(token: str) -> str:
    """
    Verify JWT refresh token and extract client_id

    Args:
        token: JWT refresh token string

    Returns:
        Client UUID from token payload

    Raises:
        HTTPException 401: Invalid token, expired, or wrong type
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Verify token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type. Expected refresh token."
            )

        client_id = payload.get("sub")
        if not client_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return client_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid refresh token: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt (12 rounds)

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password string
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against bcrypt hash

    Args:
        plain_password: Plain text password from user
        hashed_password: Bcrypt hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


async def get_current_user_id(authorization: Optional[str]) -> str:
    """
    Extract and verify client_id from Authorization header

    Args:
        authorization: Authorization header value ("Bearer <token>")

    Returns:
        Client UUID from verified token

    Raises:
        HTTPException 401: Missing or invalid authorization header
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )

    token = authorization.replace("Bearer ", "").strip()
    client_id = verify_access_token(token)
    return client_id


def get_redirect_by_role(role: str) -> str:
    """
    Get frontend redirect path based on user role

    Args:
        role: User role (client/reseller/owner/agent)

    Returns:
        Frontend route path for navigation after login

    Role mapping:
        - client: /dashboard
        - reseller: /reseller/dashboard
        - owner: /admin/resellers (OMEGA platform owner)
        - agent: /dashboard
    """
    role_redirects = {
        "client": "/dashboard",
        "reseller": "/reseller/dashboard",
        "owner": "/admin/resellers",
        "agent": "/dashboard",
    }
    return role_redirects.get(role, "/dashboard")
