from pathlib import Path

from app.core.config import get_settings
from app.document_processing.pdf_loader import extract_pages
from app.document_processing.text_splitter import split_text
from app.providers.ollama_client import OllamaClient
from app.providers.vector_store import VectorStore
from app.repositories.document_repository import DocumentRepository
from app.schemas.documents import DocumentStatus


class IngestionService:
    def __init__(self, repository: DocumentRepository | None = None) -> None:
        self.repository = repository or DocumentRepository()

    async def ingest_document(self, document_id: str, path: Path) -> None:
        await self.repository.set_status(document_id, DocumentStatus.processing)
        try:
            pages = extract_pages(path)
            settings = get_settings()
            collection = VectorStore().collection(document_id)
            client = OllamaClient()
            ids, texts, embeddings, metadatas = [], [], [], []
            for page in pages:
                for index, chunk in enumerate(split_text(page["text"], settings.chunk_size, settings.chunk_overlap)):
                    ids.append(f"{document_id}_{page['page']}_{index}")
                    texts.append(chunk)
                    embeddings.append(await client.embed(chunk))
                    metadatas.append({"page": page["page"]})
            if texts:
                collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
            await self.repository.set_status(
                document_id,
                DocumentStatus.completed,
                page_count=len(pages),
                chunk_count=len(texts),
                error=None,
            )
        except Exception as exc:
            await self.repository.set_status(document_id, DocumentStatus.failed, error=str(exc))
