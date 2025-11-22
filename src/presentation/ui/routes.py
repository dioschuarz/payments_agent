"""UI routes for WhatsApp demo interface."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from src.infrastructure.security.session_manager import generate_session_id

router = APIRouter(prefix="/demo", tags=["demo"])

# Caminho para o arquivo HTML
UI_DIR = Path(__file__).parent
DEMO_HTML_PATH = UI_DIR / "demo.html"


@router.get("/", response_class=HTMLResponse)
async def demo_ui():
    """
    Serve a demo UI interface with session cookie.

    Generates a session ID and sets it as HttpOnly cookie with SameSite=Strict.
    Does not inject any sensitive variables into the HTML.
    
    Returns:
        HTMLResponse: Página HTML da interface de chat com cookie de sessão
    """
    if not DEMO_HTML_PATH.exists():
        return HTMLResponse(
            content="<h1>Demo UI not found</h1>",
            status_code=404
        )
    
    # Generate session ID
    session_id = generate_session_id()
    
    # Lê o arquivo HTML (sem injetar variáveis sensíveis)
    with open(DEMO_HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Create response with session cookie
    response = HTMLResponse(content=html_content)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="strict",
        secure=False,  # Set to True in production with HTTPS
        max_age=3600,  # 1 hour
    )
    
    return response


@router.get("/health")
async def demo_health():
    """Health check para o módulo de UI."""
    return {
        "status": "ok",
        "ui_available": DEMO_HTML_PATH.exists()
    }

