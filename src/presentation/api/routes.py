"""FastAPI routes."""

import json
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.infrastructure.security.hmac_verification import (
    generate_meta_signature,
    verify_meta_signature,
)
from src.infrastructure.security.idempotency import check_and_record_message_id
from src.infrastructure.security.session_manager import validate_session_id
from src.presentation.api.models import (
    DemoSendRequest,
    HealthResponse,
    WhatsAppMessageRequest,
    WhatsAppMessageResponse,
    detect_webhook_format,
    extract_message_id,
    normalize_to_simplified,
)
from src.presentation.agent_flow import AgentFlow

router = APIRouter()

# Global agent flow instance (will be injected in main.py)
_agent_flow: AgentFlow = None


def set_agent_flow(agent_flow: AgentFlow) -> None:
    """Set agent flow instance."""
    global _agent_flow
    _agent_flow = agent_flow


def get_agent_flow() -> AgentFlow:
    """Get agent flow instance."""
    if _agent_flow is None:
        raise HTTPException(status_code=500, detail="Agent flow not initialized")
    return _agent_flow


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")


async def verify_signature(request: Request) -> bytes:
    """
    Dependency to verify HMAC signature for webhook requests.
    Returns the body bytes for further processing.

    Raises:
        HTTPException: If signature is invalid
    
    Returns:
        bytes: Request body bytes
    """
    secret = os.getenv("META_APP_SECRET")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="META_APP_SECRET not configured",
        )
    
    # Read body once
    body_bytes = await request.body()
    
    # Verify signature
    await verify_meta_signature_with_body(request, body_bytes, secret)
    
    return body_bytes


async def verify_meta_signature_with_body(
    request: Request, body_bytes: bytes, secret: str
) -> None:
    """
    Verify Meta webhook signature with pre-read body bytes.

    Raises:
        HTTPException: If signature is invalid
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

    if not body_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty request body",
        )

    # Calculate HMAC-SHA256
    calculated_hash = generate_meta_signature(body_bytes, secret)

    # Compare using constant-time comparison to prevent timing attacks
    import hmac
    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid signature",
        )


@router.post("/webhook", response_model=WhatsAppMessageResponse)
async def webhook(
    request: Request,
    agent_flow: AgentFlow = Depends(get_agent_flow),
    body_bytes: bytes = Depends(verify_signature),
) -> WhatsAppMessageResponse:
    """
    Official webhook endpoint (Meta or internal proxy).

    This endpoint does not know about Demo. It treats all requests as official.
    Security: HMAC signature verification and idempotency check.
    """
    try:
        # Parse body (already read and verified in dependency)
        body_dict = json.loads(body_bytes.decode("utf-8"))

        # Check idempotency (anti-replay)
        message_id = extract_message_id(body_dict)
        if message_id and check_and_record_message_id(message_id):
            # Message already processed, return success without reprocessing
            # Extract from_number for response
            normalized = normalize_to_simplified(body_dict)
            return WhatsAppMessageResponse(
                to_number=normalized.get("from_number", ""),
                message="Message already processed",
                status="success",
            )

        # Normalize to simplified format
        normalized = normalize_to_simplified(body_dict)

        # Use phone number as session ID
        session_id = normalized.get("from_number", "")
        message = normalized.get("message", "")

        if not session_id or not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: from_number or message",
            )

        # Process message through agent flow
        response_message = await agent_flow.process_message(session_id, message)

        return WhatsAppMessageResponse(
            to_number=session_id,
            message=response_message,
            status="success",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}",
        )


@router.post("/demo/send", response_model=WhatsAppMessageResponse)
async def demo_send(
    request: Request,
    demo_request: DemoSendRequest,
    agent_flow: AgentFlow = Depends(get_agent_flow),
) -> WhatsAppMessageResponse:
    """
    Demo send endpoint (proxy pattern).

    Validates session, access code, signs request, and forwards to webhook.
    """
    try:
        # 1. Validate session cookie
        session_id = request.cookies.get("session_id")
        if not session_id or not validate_session_id(session_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing session",
            )

        # 2. Validate access code (early exit to save CPU)
        demo_access_code = os.getenv("DEMO_ACCESS_CODE")
        if not demo_access_code or demo_request.access_code != demo_access_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid access code",
            )

        # 3. Get secret and generate signature
        secret = os.getenv("META_APP_SECRET")
        if not secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="META_APP_SECRET not configured",
            )

        # Serialize payload to JSON bytes
        payload_bytes = json.dumps(demo_request.payload, separators=(",", ":")).encode("utf-8")
        signature = generate_meta_signature(payload_bytes, secret)

        # 4. Make loopback request to /webhook
        port = os.getenv("PORT", "8080")
        webhook_url = f"http://localhost:{port}/webhook"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                content=payload_bytes,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": f"sha256={signature}",
                },
                timeout=30.0,
            )

            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text,
                )

            return response.json()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing demo request: {str(e)}",
        )


# Legacy endpoint for backward compatibility
@router.post("/webhook/whatsapp", response_model=WhatsAppMessageResponse)
async def whatsapp_webhook(
    request: WhatsAppMessageRequest,
    agent_flow: AgentFlow = Depends(get_agent_flow),
) -> WhatsAppMessageResponse:
    """
    Legacy WhatsApp webhook endpoint (deprecated, use /webhook instead).

    Receives messages from WhatsApp and processes them through the agent.
    """
    try:
        # Use phone number as session ID
        session_id = request.from_number

        # Process message through agent flow
        response_message = await agent_flow.process_message(session_id, request.message)

        return WhatsAppMessageResponse(
            to_number=request.from_number,
            message=response_message,
            status="success",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

