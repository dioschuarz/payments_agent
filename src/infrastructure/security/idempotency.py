"""Idempotency check using Firestore to prevent duplicate message processing."""

import os
from datetime import datetime, timedelta
from typing import Optional

from google.cloud import firestore
from google.cloud.firestore import SERVER_TIMESTAMP


# Global Firestore client (lazy initialization)
_firestore_client: Optional[firestore.Client] = None


def _get_firestore_client() -> firestore.Client:
    """
    Get or create Firestore client instance.

    Returns:
        Firestore client instance
    """
    global _firestore_client
    if _firestore_client is None:
        project_id = os.getenv("GCP_PROJECT_ID")
        _firestore_client = firestore.Client(project=project_id)
    return _firestore_client


def check_and_record_message_id(message_id: str, ttl_seconds: int = 3600) -> bool:
    """
    Check if message ID was already processed and record it if new.

    Args:
        message_id: Unique message ID to check
        ttl_seconds: Time to live in seconds (default: 1 hour)

    Returns:
        True if message was already processed, False if new
    """
    if not message_id:
        return False

    client = _get_firestore_client()
    collection = client.collection("processed_messages")
    doc_ref = collection.document(message_id)

    # Check if document exists
    doc = doc_ref.get()
    if doc.exists:
        # Message already processed
        return True

    # Record message ID with expiration timestamp
    expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    doc_ref.set(
        {
            "message_id": message_id,
            "processed_at": SERVER_TIMESTAMP,
            "expires_at": expires_at,
        }
    )

    return False

