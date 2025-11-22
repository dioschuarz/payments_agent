"""ADK-based conversation orchestrator using workflow agents and tools."""

import os
from typing import Optional

from google.adk import Agent, Runner
from google.adk.memory import InMemoryMemoryService
from google.adk.plugins import LoggingPlugin, ReflectAndRetryToolPlugin
from google.adk.sessions import InMemorySessionService

from src.domain.value_objects.countries_data import get_country_list_for_prompt
from src.infrastructure.ai.prompts.prompt_loader import PromptLoader
from src.infrastructure.ai.tools.amount_tool import create_amount_tool
from src.infrastructure.ai.tools.beneficiary_tool import create_beneficiary_tool
from src.infrastructure.ai.tools.country_tool import create_country_tool
from src.infrastructure.ai.tools.delivery_method_tool import create_delivery_method_tool
from src.infrastructure.validators.amount_validator import AmountValidator
from src.infrastructure.validators.beneficiary_validator import BeneficiaryValidator
from src.infrastructure.validators.country_validator import CountryValidator
from src.infrastructure.validators.delivery_method_validator import DeliveryMethodValidator


class ADKOrchestrator:
    """ADK-based orchestrator using agents and tools for conversation flow."""

    def __init__(
        self,
        beneficiary_validator: BeneficiaryValidator,
        country_validator: CountryValidator,
        amount_validator: AmountValidator,
        delivery_method_validator: DeliveryMethodValidator,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize ADK orchestrator.

        Args:
            beneficiary_validator: Validator for beneficiaries
            country_validator: Validator for countries
            amount_validator: Validator for amounts
            delivery_method_validator: Validator for delivery methods
            api_key: Google API key
            model: Model name to use (defaults to GEMINI_MODEL env var or "gemini-2.5-flash")
        """
        self._api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self._api_key:
            raise ValueError("GOOGLE_API_KEY must be provided or set in environment")
        
        # Get model from parameter, environment variable, or use default
        self._model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

        # Initialize prompt loader
        self._prompt_loader = PromptLoader()

        # Create ADK tools from validators
        self._beneficiary_tool = create_beneficiary_tool(beneficiary_validator)
        self._amount_tool = create_amount_tool(amount_validator)
        self._country_tool = create_country_tool(country_validator)
        self._delivery_method_tool = create_delivery_method_tool(delivery_method_validator)

        # Get country list for prompt
        country_list = get_country_list_for_prompt()

        # Load prompts from files
        agent_instruction = self._prompt_loader.load_agent_instruction(country_list)
        agent_description = self._prompt_loader.load_agent_description()

        # Create main orchestrator agent with tools
        self._agent = Agent(
            name="money_transfer_orchestrator",
            model=self._model,
            instruction=agent_instruction,
            description=agent_description,
            tools=[
                self._beneficiary_tool,
                self._amount_tool,
                self._country_tool,
                self._delivery_method_tool,
            ],
        )

        # Create ADK memory service for state management and caching
        memory_service = InMemoryMemoryService()

        # Create session service (store reference for session creation)
        self._session_service = InMemorySessionService()

        # Create Runner with session service, memory service, and plugins
        self._runner = Runner(
            app_name="money_transfer_agent",
            agent=self._agent,
            session_service=self._session_service,
            memory_service=memory_service,  # ADK memory for state and caching
            plugins=[
                LoggingPlugin(),  # ADK logging plugin
                ReflectAndRetryToolPlugin(),  # ADK retry plugin for tool failures
            ],
        )


    async def process_message(self, session_id: str, user_input: str) -> str:
        """
        Process user message and return response using ADK agent.

        Args:
            session_id: Session identifier
            user_input: User's message

        Returns:
            Response message from agent
        """
        # Ensure session exists (ADK requires session to be created first)
        # get_session returns None if session doesn't exist
        session = await self._session_service.get_session(
            app_name="money_transfer_agent",
            user_id=session_id,
            session_id=session_id,
        )
        
        # If session doesn't exist, create it
        if session is None:
            try:
                await self._session_service.create_session(
                    app_name="money_transfer_agent",
                    user_id=session_id,
                    session_id=session_id,
                )
            except Exception:
                # Session might have been created by another request, ignore
                pass

        # Create message content for ADK
        # Content is from google.genai.types (not google.adk.types)
        from google.genai.types import Content
        
        message = Content(role="user", parts=[{"text": user_input}])
        
        # Run agent and collect response
        response_text = ""
        final_response_text = ""
        
        async for event in self._runner.run_async(
            user_id=session_id,
            session_id=session_id,
            new_message=message,
        ):
            # Extract text from response events
            # ADK events have a 'content' attribute that can be Content object or other types
            if hasattr(event, 'content'):
                content = event.content
                # If content is a Content object with parts
                if hasattr(content, 'parts'):
                    for part in content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
                        elif isinstance(part, dict) and 'text' in part:
                            response_text += part['text']
                # If content has text directly
                elif hasattr(content, 'text') and content.text:
                    response_text += content.text
                # If content is a string
                elif isinstance(content, str):
                    response_text += content
            
            # Also check for text attribute directly on event
            if hasattr(event, 'text') and event.text:
                response_text += event.text
            
            # Check if this is the final response event
            if hasattr(event, 'is_final_response') and event.is_final_response:
                final_response_text = response_text
        
        # Use final response if available, otherwise use accumulated text
        result_text = final_response_text if final_response_text else response_text
        
        # If no text response, generate a default
        if not result_text:
            result_text = "I'm here to help you send money. What would you like to do?"
        
        return result_text

