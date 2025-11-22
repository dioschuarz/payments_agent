"""Session management for demo requests."""

import uuid
import re


def generate_session_id() -> str:
    """
    Generate a random session ID.

    Returns:
        UUID string as session ID
    """
    return str(uuid.uuid4())


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.

    Args:
        session_id: Session ID to validate

    Returns:
        True if valid UUID format, False otherwise
    """
    if not session_id:
        return False

    # UUID format validation (8-4-4-4-12 hex digits)
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    return bool(uuid_pattern.match(session_id))

