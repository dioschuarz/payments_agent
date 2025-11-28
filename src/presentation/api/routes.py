"""FastAPI routes."""

import json
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.domain.exceptions import ADKServiceUnavailableError, AgentFlowError
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
    except HTTPException as e:
        # If it's a 429 from Cloud Armor (before reaching our code), 
        # it means rate limit was hit - this should be rare if retry logic is working
        # But if it happens, we still return 503 to avoid exposing rate limit details
        if e.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable. Please try again in a moment.",
            )
        raise
    except AgentFlowError as e:
        # Agent flow error - service unavailable after retries
        # This includes 429 errors that were retried but still failed
        # Return 503 to indicate service is temporarily unavailable (not exposing rate limit)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.user_friendly_message,
        )
    except ADKServiceUnavailableError as e:
        # ADK service unavailable - return 503
        # This includes 429 errors from Google ADK API that were retried
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later.",
        )
    except Exception as e:
        # Check for 429 errors - these should be retried internally, not exposed to user
        error_str = str(e).lower()
        is_rate_limit = (
            "429" in error_str
            or "too many requests" in error_str
            or "rate limit" in error_str
            or (hasattr(e, "status_code") and e.status_code == 429)
        )

        # If we get a 429 here, it means retry logic didn't catch it
        # Still return 503 instead of 429 to avoid exposing rate limit details
        if is_rate_limit:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable. Please try again in a moment.",
            )

        # Other errors - check if they're retryable (5xx) or not (4xx)
        is_retryable = any(
            code in error_str
            for code in ["503", "500", "502", "504", "service unavailable", "internal server error"]
        ) or hasattr(e, "status_code") and isinstance(e.status_code, int) and e.status_code >= 500

        if is_retryable:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable. Please try again later.",
            )
        else:
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
        if not demo_access_code:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="DEMO_ACCESS_CODE not configured",
            )
        # Strip whitespace (including newlines) from secret value
        demo_access_code = demo_access_code.strip()
        if demo_request.access_code != demo_access_code:
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
    except HTTPException as e:
        # If it's already a 429, it might be from Cloud Armor - add helpful message
        if e.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please wait a moment before sending another message.",
            )
        raise
    except AgentFlowError as e:
        # Agent flow error - service unavailable after retries
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.user_friendly_message,
        )
    except ADKServiceUnavailableError as e:
        # ADK service unavailable - return 503
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later.",
        )
    except Exception as e:
        # Check for 429 errors (rate limiting from Cloud Armor or API)
        error_str = str(e).lower()
        is_rate_limit = (
            "429" in error_str
            or "too many requests" in error_str
            or "rate limit" in error_str
            or (hasattr(e, "status_code") and e.status_code == 429)
        )

        if is_rate_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please wait a moment before sending another message.",
            )

        # Other errors - check if they're retryable (5xx) or not (4xx)
        is_retryable = any(
            code in error_str
            for code in ["503", "500", "502", "504", "service unavailable", "internal server error"]
        ) or hasattr(e, "status_code") and isinstance(e.status_code, int) and e.status_code >= 500

        if is_retryable:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable. Please try again later.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing message: {str(e)}",
            )

