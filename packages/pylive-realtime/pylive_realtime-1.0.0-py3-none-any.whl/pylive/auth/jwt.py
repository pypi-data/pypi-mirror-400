"""
JWT authentication module.
"""

import jwt
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import Optional


@dataclass
class Claims:
    """JWT claims."""
    user_id: str
    username: str
    email: str = ""
    role: str = "user"
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    issuer: str = "pylive"


def sign_token(
    user_id: str,
    username: str,
    email: str,
    secret: str,
    ttl_hours: int = 24,
    role: str = "user",
    issuer: str = "pylive"
) -> str:
    """
    Create a new JWT token.

    Args:
        user_id: User identifier
        username: Username
        email: User email
        secret: JWT signing secret
        ttl_hours: Token time-to-live in hours
        role: User role
        issuer: Token issuer

    Returns:
        Signed JWT token string
    """
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=ttl_hours)

    payload = {
        "uid": user_id,
        "username": username,
        "email": email,
        "role": role,
        "iat": now,
        "exp": expires,
        "nbf": now,
        "iss": issuer,
        "sub": user_id,
    }

    return jwt.encode(payload, secret, algorithm="HS256")


def verify_token(token: str, secret: str) -> Claims:
    """
    Validate and parse a JWT token.

    Args:
        token: JWT token string
        secret: JWT signing secret

    Returns:
        Claims object with token data

    Raises:
        jwt.InvalidTokenError: If token is invalid
        jwt.ExpiredSignatureError: If token is expired
    """
    payload = jwt.decode(
        token,
        secret,
        algorithms=["HS256"],
        options={"require": ["exp", "iat", "sub"]}
    )

    return Claims(
        user_id=payload.get("uid", payload.get("sub", "")),
        username=payload.get("username", ""),
        email=payload.get("email", ""),
        role=payload.get("role", "user"),
        issued_at=datetime.fromtimestamp(payload.get("iat", 0), timezone.utc),
        expires_at=datetime.fromtimestamp(payload.get("exp", 0), timezone.utc),
        issuer=payload.get("iss", "pylive"),
    )
