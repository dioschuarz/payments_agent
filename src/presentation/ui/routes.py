"""UI routes for WhatsApp demo interface."""

from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/demo", tags=["demo"])

# Caminho para o arquivo HTML
UI_DIR = Path(__file__).parent
DEMO_HTML_PATH = UI_DIR / "demo.html"


@router.get("/", response_class=HTMLResponse)
async def demo_ui():
    """
    Serve a demo UI interface.
    
    Returns:
        HTMLResponse: Página HTML da interface de chat
    """
    if not DEMO_HTML_PATH.exists():
        return HTMLResponse(
            content="<h1>Demo UI not found</h1>",
            status_code=404
        )
    
    # Lê o arquivo HTML e retorna
    with open(DEMO_HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


@router.get("/health")
async def demo_health():
    """Health check para o módulo de UI."""
    return {
        "status": "ok",
        "ui_available": DEMO_HTML_PATH.exists()
    }

