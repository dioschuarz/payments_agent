"""Agent flow controller - Main orchestrator."""

from typing import Union

from src.infrastructure.ai.agents.adk_orchestrator import ADKOrchestrator


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
        """
        return await self._orchestrator.process_message(session_id, user_input)

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

