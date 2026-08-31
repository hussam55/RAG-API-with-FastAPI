from fastapi import APIRouter, Depends

from app.api.deps import get_ollama_client
from app.providers.ollama_client import OllamaClient

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def ready(ollama_client: OllamaClient = Depends(get_ollama_client)) -> dict[str, str | bool]:
    ollama_ready = await ollama_client.is_ready()
    return {"status": "ok" if ollama_ready else "degraded", "ollama": ollama_ready}
