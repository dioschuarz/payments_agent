"""Agent flow controller - Main orchestrator."""

import logging
from typing import Union

from src.domain.exceptions import ADKServiceUnavailableError, AgentFlowError
from src.infrastructure.ai.agents.adk_orchestrator import ADKOrchestrator
from src.infrastructure.ai.retry_handler import retry_with_backoff

logger = logging.getLogger(__name__)


class AgentFlow:
    """Main agent flow controller."""

    def __init__(self, orchestrator: ADKOrchestrator):
        """
        Initialize agent flow.

        Args:
            orchestrator: ADK orchestrator
        """
        self._orchestrator = orchestrator

    async def process_message(self, session_id: str, user_input: str) -> str:
        """
        Process user message and return response.

        Args:
            session_id: Session identifier (e.g., WhatsApp phone number)
            user_input: User's message

        Returns:
            Response message

        Raises:
            AgentFlowError: If processing fails after all retries
        """
        # Second layer of retry with more conservative settings (2 retries)
        try:
            return await retry_with_backoff(
                self._orchestrator.process_message,
                session_id,
                user_input,
                max_retries=2,  # More conservative than ADKOrchestrator
                initial_backoff=1.0,  # Start with 1 second
                context={
                    "session_id": session_id,
                    "component": "AgentFlow",
                },
            )
        except ADKServiceUnavailableError as e:
            # Convert ADK error to user-friendly message
            logger.error(
                f"Agent flow failed after retries: {e}",
                extra={
                    "session_id": session_id,
                    "attempts": e.attempts,
                    "original_error": str(e.original_error) if e.original_error else None,
                },
            )
            raise AgentFlowError(
                f"Service temporarily unavailable. Please try again in a moment.",
                user_friendly_message="I'm having trouble processing your request right now. Please try again in a moment.",
                original_error=e,
            ) from e
        except Exception as e:
            # Handle any other unexpected errors
            logger.error(
                f"Unexpected error in agent flow: {e}",
                extra={"session_id": session_id, "error_type": type(e).__name__},
                exc_info=True,
            )
            raise AgentFlowError(
                f"An error occurred while processing your message: {str(e)}",
                user_friendly_message="I encountered an error processing your request. Please try again.",
                original_error=e,
            ) from e

    async def get_state(self, session_id: str):
        """
        Get current state for a session.

        Args:
            session_id: Session identifier

        Returns:
            State information (ADK manages this internally)
        """
        # ADK manages state internally via session service
        # Can be extended to expose state if needed
        return {"session_id": session_id, "note": "State managed by ADK session service"}

