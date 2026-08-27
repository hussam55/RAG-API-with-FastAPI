from pathlib import Path

from app.providers.vector_store import VectorStore
from app.repositories.document_repository import DocumentRepository
from app.schemas.documents import DocumentDetail
from app.services.errors import DocumentDeletionError


class DocumentService:
    def __init__(self, repository: DocumentRepository | None = None) -> None:
        self.repository = repository or DocumentRepository()

    async def create_document(self, document_id: str, filename: str, storage_path: str) -> DocumentDetail:
        return await self.repository.create(document_id=document_id, filename=filename, storage_path=storage_path)

    async def get_document(self, document_id: str) -> DocumentDetail | None:
        return await self.repository.get(document_id)

    async def delete_document(self, document_id: str) -> DocumentDetail | None:
        storage_path = await self.repository.get_storage_path(document_id)
        if storage_path is None:
            return None

        try:
            VectorStore().delete(document_id)
        except Exception as exc:
            raise DocumentDeletionError("Unable to delete document vectors") from exc

        deleted = await self.repository.delete(document_id)
        if deleted is None:
            return None

        Path(storage_path).unlink(missing_ok=True)
        return deleted
