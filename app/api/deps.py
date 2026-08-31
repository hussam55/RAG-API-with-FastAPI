from app.core.config import Settings, get_settings
from app.providers.ollama_client import OllamaClient
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.services.ingestion_service import IngestionService
from app.services.query_service import QueryService


def get_settings_provider() -> Settings:
    return get_settings()


def get_document_service() -> DocumentService:
    return DocumentService(repository=DocumentRepository())


def get_ingestion_service() -> IngestionService:
    return IngestionService(repository=DocumentRepository())


def get_query_service() -> QueryService:
    return QueryService(repository=DocumentRepository())


def get_ollama_client() -> OllamaClient:
    return OllamaClient()
