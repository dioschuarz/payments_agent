"""Request and response models for API."""

from typing import Optional

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

