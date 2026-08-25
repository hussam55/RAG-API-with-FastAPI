import chromadb

from app.core.config import get_settings


class VectorStore:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=get_settings().chroma_path)

    def collection(self, document_id: str):
        return self.client.get_or_create_collection(f"document_{document_id}")

    def delete(self, document_id: str) -> None:
        self.client.delete_collection(f"document_{document_id}")
