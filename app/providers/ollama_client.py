import httpx

from app.core.config import get_settings


class OllamaClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.chat_model = settings.chat_model
        self.embedding_model = settings.embedding_model

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
            )
            response.raise_for_status()
            return response.json()["embedding"]

    async def answer(self, question: str, context: str) -> str:
        prompt = f"Answer only from this document context. If absent, say you cannot find it.\n\nContext:\n{context}\n\nQuestion: {question}"
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.chat_model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]

    async def is_ready(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                return (await client.get(f"{self.base_url}/api/tags")).is_success
        except httpx.HTTPError:
            return False
