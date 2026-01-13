"""Utility functions for Chucky SDK."""

import base64
import hashlib
import hmac
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional


@dataclass
class TokenBudget:
    """Budget configuration for a token."""

    ai: int  # AI budget in microdollars (1 USD = 1,000,000)
    compute: int  # Compute budget in seconds
    window: Literal["hour", "day", "week", "month"]
    window_start: str  # ISO 8601 date string


def create_budget(
    ai_dollars: float,
    compute_hours: float,
    window: Literal["hour", "day", "week", "month"] = "day",
    window_start: Optional[datetime] = None,
) -> TokenBudget:
    """
    Create a budget configuration.

    Args:
        ai_dollars: AI budget in dollars
        compute_hours: Compute budget in hours
        window: Budget window period
        window_start: Start of budget window (default: now)

    Returns:
        TokenBudget configuration

    Example:
        ```python
        budget = create_budget(
            ai_dollars=1.00,     # $1 AI budget
            compute_hours=1,     # 1 hour compute
            window="day",
        )
        ```
    """
    if window_start is None:
        window_start = datetime.utcnow()

    return TokenBudget(
        ai=int(ai_dollars * 1_000_000),  # Convert to microdollars
        compute=int(compute_hours * 3600),  # Convert to seconds
        window=window,
        window_start=window_start.isoformat() + "Z",
    )


def extract_project_id(hmac_key: str) -> str:
    """
    @deprecated The project ID is now separate from the HMAC key for security reasons.
    Get your project ID from the Chucky portal (app.chucky.cloud) instead.

    Previously, the HMAC key embedded the project ID, but this exposed the secret
    in JWT tokens. Project IDs are now Convex document IDs visible in the portal.

    Args:
        hmac_key: Ignored (previously used to extract project ID)

    Raises:
        DeprecationWarning: Always raises directing users to get project ID from portal
    """
    raise DeprecationWarning(
        "extract_project_id() is deprecated. The project ID is now separate from the HMAC key for security. "
        "Get your project ID from the Chucky portal (app.chucky.cloud) in your project settings."
    )


def _base64url_encode(data: bytes) -> str:
    """Base64URL encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def create_token(
    user_id: str,
    project_id: str,
    secret: str,
    budget: TokenBudget,
    expires_in: int = 3600,
) -> str:
    """
    Create a JWT token for authenticating with Chucky.

    Args:
        user_id: Unique identifier for the user
        project_id: Project UUID (use extract_project_id to get from HMAC key)
        secret: HMAC secret key for signing
        budget: Budget configuration
        expires_in: Token expiry in seconds (default: 1 hour)

    Returns:
        Signed JWT token

    Example:
        ```python
        from chucky import create_token, create_budget, extract_project_id

        hmac_key = 'hk_live_938642b649c64cc3975e504c0fbcbbd8'
        project_id = extract_project_id(hmac_key)

        token = create_token(
            user_id='user-123',
            project_id=project_id,
            secret=hmac_key,
            budget=create_budget(
                ai_dollars=1.00,
                compute_hours=1,
                window='day',
            ),
        )
        ```
    """
    now = int(time.time())

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "iss": project_id,
        "iat": now,
        "exp": now + expires_in,
        "budget": {
            "ai": budget.ai,
            "compute": budget.compute,
            "window": budget.window,
            "windowStart": budget.window_start,
        },
    }

    header_b64 = _base64url_encode(json.dumps(header).encode())
    payload_b64 = _base64url_encode(json.dumps(payload).encode())

    signature = hmac.new(
        secret.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256,
    ).digest()
    signature_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_token(token: str) -> dict:
    """
    Decode a JWT token without verification.

    Args:
        token: JWT token string

    Returns:
        Dictionary with 'header' and 'payload'

    Example:
        ```python
        decoded = decode_token(token)
        print(decoded['payload']['sub'])  # User ID
        print(decoded['payload']['budget'])  # Budget limits
        ```
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token format")

    def _base64url_decode(s: str) -> bytes:
        padding = "=" * ((4 - len(s) % 4) % 4)
        return base64.urlsafe_b64decode(s + padding)

    header = json.loads(_base64url_decode(parts[0]))
    payload = json.loads(_base64url_decode(parts[1]))

    return {"header": header, "payload": payload, "signature": parts[2]}


def verify_token(token: str, secret: str) -> bool:
    """
    Verify a JWT token signature.

    Args:
        token: JWT token string
        secret: HMAC secret key

    Returns:
        True if signature is valid
    """
    parts = token.split(".")
    if len(parts) != 3:
        return False

    signature_input = f"{parts[0]}.{parts[1]}"
    expected_signature = hmac.new(
        secret.encode(),
        signature_input.encode(),
        hashlib.sha256,
    ).digest()
    expected_b64 = _base64url_encode(expected_signature)

    return parts[2] == expected_b64


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired.

    Args:
        token: JWT token string

    Returns:
        True if token is expired
    """
    try:
        decoded = decode_token(token)
        exp = decoded["payload"].get("exp", 0)
        return exp < time.time()
    except Exception:
        return True
