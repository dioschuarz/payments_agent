"""HMAC signature verification for Meta webhook requests."""

import hashlib
import hmac
from typing import Optional

from fastapi import HTTPException, Request, status


async def verify_meta_signature(request: Request, secret: str) -> bool:
    """
    Verify Meta webhook signature using HMAC-SHA256.

    Args:
        request: FastAPI request object
        secret: Secret key for HMAC verification

    Returns:
        True if signature is valid, False otherwise

    Raises:
        HTTPException: If signature header is missing or invalid
    """
    # Extract signature header
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing X-Hub-Signature-256 header",
        )

    # Extract hash from header (format: sha256=HASH...)
    if not signature_header.startswith("sha256="):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid signature format",
        )

    received_hash = signature_header[7:]  # Remove "sha256=" prefix

    # Read request body as bytes
    body_bytes = request.body()
    if not body_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty request body",
        )

    # Calculate HMAC-SHA256
    calculated_hash = generate_meta_signature(body_bytes, secret)

    # Compare using constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid signature",
        )

    return True


def generate_meta_signature(payload: bytes, secret: str) -> str:
    """
    Generate Meta webhook signature using HMAC-SHA256.

    Args:
        payload: Request body as bytes
        secret: Secret key for HMAC generation

    Returns:
        Hexadecimal string of the HMAC-SHA256 hash
    """
    # Calculate HMAC-SHA256
    hmac_hash = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    )

    # Return hexadecimal string
    return hmac_hash.hexdigest()

