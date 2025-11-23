"""Main FastAPI application entry point."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.infrastructure.ai.agents.adk_orchestrator import ADKOrchestrator
from src.infrastructure.config.service_factory import ServiceFactory
from src.infrastructure.validators.amount_validator import AmountValidator
from src.infrastructure.validators.beneficiary_validator import BeneficiaryValidator
from src.infrastructure.validators.country_validator import CountryValidator
from src.infrastructure.validators.delivery_method_validator import DeliveryMethodValidator
from src.presentation.agent_flow import AgentFlow
from src.presentation.api.middleware import ErrorHandlingMiddleware, LoggingMiddleware
from src.presentation.api.routes import router
from src.presentation.ui.routes import router as ui_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Send Money Agent",
    description="Conversational agent for money transfers",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Note: Caching and session management are now handled by ADK
# - ADK Memory Service handles caching and state
# - ADK Session Service handles session management
# No custom CacheManager or SessionManager needed

# Initialize service factory and create services
service_factory = ServiceFactory()

# Create services using factory (supports both mock and HTTP based on config)
beneficiary_service = service_factory.create_beneficiary_service()
country_service = service_factory.create_country_service()
amount_service = service_factory.create_amount_validation_service()
delivery_method_service = service_factory.create_delivery_method_service()

# Initialize validators with services (no cache manager - ADK handles caching)
beneficiary_validator = BeneficiaryValidator(beneficiary_service)
country_validator = CountryValidator(country_service)
amount_validator = AmountValidator(amount_service)
delivery_method_validator = DeliveryMethodValidator(delivery_method_service)

# Initialize ADK orchestrator (replaces ConversationOrchestrator, StateManager, CacheManager)
# ADK orchestrator uses agents, tools, memory service, and plugins
# Model name is read from GEMINI_MODEL environment variable (defaults to "gemini-2.5-flash")
adk_orchestrator = ADKOrchestrator(
    beneficiary_validator=beneficiary_validator,
    country_validator=country_validator,
    amount_validator=amount_validator,
    delivery_method_validator=delivery_method_validator,
    api_key=os.getenv("GOOGLE_API_KEY"),
    model=os.getenv("GEMINI_MODEL"),  # Will use default if not set
)

# Initialize agent flow with ADK orchestrator
agent_flow = AgentFlow(adk_orchestrator)


# Dependency injection for routes
async def get_agent_flow() -> AgentFlow:
    """Get agent flow instance."""
    return agent_flow


# Set agent flow in routes module
from src.presentation.api.routes import set_agent_flow

set_agent_flow(agent_flow)

# Include routes
app.include_router(router)

# Include UI routes
app.include_router(ui_router)


@app.get("/")
async def root():
    """Root endpoint - redirects to demo UI."""
    return RedirectResponse(url="/demo/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
