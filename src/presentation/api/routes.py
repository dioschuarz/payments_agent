"""FastAPI routes."""

from fastapi import APIRouter, Depends, HTTPException

from src.presentation.api.models import (
    HealthResponse,
    WhatsAppMessageRequest,
    WhatsAppMessageResponse,
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


@router.post("/webhook/whatsapp", response_model=WhatsAppMessageResponse)
async def whatsapp_webhook(
    request: WhatsAppMessageRequest,
    agent_flow: AgentFlow = Depends(get_agent_flow),
) -> WhatsAppMessageResponse:
    """
    WhatsApp webhook endpoint.

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

