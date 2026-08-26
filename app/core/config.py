from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    chat_model: str = "qwen2.5:0.5b"
    embedding_model: str = "nomic-embed-text"
    chroma_path: str = "./storage/chroma"
    database_url: str = "sqlite+aiosqlite:///./storage/rag.db"
    upload_path: str = "./storage/uploads"
    chunk_size: int = 800
    chunk_overlap: int = 120
    embedding_batch_size: int = 16
    top_k: int = 5
    max_pdf_size_mb: int = 25
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
