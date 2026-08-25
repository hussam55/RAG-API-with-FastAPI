from fastapi import APIRouter

from app.providers.ollama_client import OllamaClient

router = APIRouter(tags=["health"])

@router.get("/")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def ready() -> dict[str, str | bool]:
    ollama_ready = await OllamaClient().is_ready()
    return {"status": "ok" if ollama_ready else "degraded", "ollama": ollama_ready}
