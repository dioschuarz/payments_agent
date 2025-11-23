"""Request and response models for API."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WhatsAppMessageRequest(BaseModel):
    """Request model for WhatsApp webhook."""

    from_number: str = Field(..., description="Sender phone number")
    message: str = Field(..., description="Message content")
    message_id: Optional[str] = Field(None, description="Message ID")
    timestamp: Optional[str] = Field(None, description="Message timestamp")


class WhatsAppMessageResponse(BaseModel):
    """Response model for WhatsApp webhook."""

    to_number: str = Field(..., description="Recipient phone number")
    message: str = Field(..., description="Response message")
    status: str = Field(default="success", description="Response status")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy", description="Service status")
    version: str = Field(default="0.1.0", description="Service version")


class DemoSendRequest(BaseModel):
    """Request model for demo send endpoint (proxy pattern)."""

    payload: Dict[str, Any] = Field(..., description="Message payload")
    access_code: str = Field(..., description="Access code for demo requests")


class MetaWebhookRequest(BaseModel):
    """Request model for Meta webhook (full format)."""

    object: str = Field(..., description="Object type")
    entry: list = Field(..., description="Entry array from Meta webhook")


def detect_webhook_format(data: Dict[str, Any]) -> str:
    """
    Detect webhook format (Meta or simplified).

    Args:
        data: Request body as dictionary

    Returns:
        "meta" if Meta format, "simplified" if simplified format
    """
    # Meta format has "object" and "entry" fields
    if "object" in data and "entry" in data:
        return "meta"
    # Simplified format has "from_number" and "message" fields
    if "from_number" in data and "message" in data:
        return "simplified"
    # Default to simplified for backward compatibility
    return "simplified"


def extract_message_id(data: Dict[str, Any]) -> Optional[str]:
    """
    Extract message ID from webhook payload (supports both formats).

    Args:
        data: Request body as dictionary

    Returns:
        Message ID if found, None otherwise
    """
    format_type = detect_webhook_format(data)

    if format_type == "meta":
        # Meta format: entry[0].changes[0].value.messages[0].id
        try:
            entry = data.get("entry", [])
            if entry and len(entry) > 0:
                changes = entry[0].get("changes", [])
                if changes and len(changes) > 0:
                    value = changes[0].get("value", {})
                    messages = value.get("messages", [])
                    if messages and len(messages) > 0:
                        return messages[0].get("id")
        except (KeyError, IndexError, TypeError):
            pass

    elif format_type == "simplified":
        # Simplified format: message_id field
        return data.get("message_id")

    return None


def normalize_to_simplified(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize webhook payload to simplified format.

    Args:
        data: Request body as dictionary (Meta or simplified format)

    Returns:
        Normalized payload in simplified format
    """
    format_type = detect_webhook_format(data)

    if format_type == "meta":
        # Extract data from Meta format
        try:
            entry = data.get("entry", [])
            if entry and len(entry) > 0:
                changes = entry[0].get("changes", [])
                if changes and len(changes) > 0:
                    value = changes[0].get("value", {})
                    messages = value.get("messages", [])
                    contacts = value.get("contacts", [])

                    if messages and len(messages) > 0:
                        message = messages[0]
                        contact = contacts[0] if contacts and len(contacts) > 0 else {}

                        return {
                            "from_number": contact.get("wa_id", ""),
                            "message": message.get("text", {}).get("body", ""),
                            "message_id": message.get("id"),
                            "timestamp": str(message.get("timestamp", "")),
                        }
        except (KeyError, IndexError, TypeError):
            pass

        # Fallback: return empty simplified format
        return {
            "from_number": "",
            "message": "",
            "message_id": None,
            "timestamp": None,
        }

    # Already in simplified format
    return data

