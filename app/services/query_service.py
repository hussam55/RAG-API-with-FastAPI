import httpx

from app.providers.ollama_client import OllamaClient
from app.providers.vector_store import VectorStore
from app.repositories.document_repository import DocumentRepository
from app.schemas.documents import DocumentStatus
from app.schemas.queries import AnswerResponse, QuestionRequest, Source
from app.services.errors import DocumentNotFoundError, DocumentNotReadyError, ModelUnavailableError


class QueryService:
    def __init__(self, repository: DocumentRepository | None = None) -> None:
        self.repository = repository or DocumentRepository()

    async def ask(self, document_id: str, request: QuestionRequest) -> AnswerResponse:
        document = await self.repository.get(document_id)
        if document is None:
            raise DocumentNotFoundError()
        if document.status != DocumentStatus.completed:
            raise DocumentNotReadyError(str(document.status))

        client = OllamaClient()
        try:
            query_embedding = await client.embed(request.question)
            results = VectorStore().collection(document_id).query(query_embeddings=[query_embedding], n_results=request.top_k)
            texts = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            answer = await client.answer(request.question, "\n\n".join(texts))
        except (httpx.HTTPError, KeyError) as exc:
            raise ModelUnavailableError() from exc

        sources = [Source(page=item["page"], text=text) for item, text in zip(metadatas, texts)] if request.include_sources else []
        return AnswerResponse(document_id=document_id, question=request.question, answer=answer, sources=sources)
