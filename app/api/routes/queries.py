import httpx
from fastapi import APIRouter, HTTPException

from app.api.routes.documents import documents
from app.providers.ollama_client import OllamaClient
from app.providers.vector_store import VectorStore
from app.schemas.documents import DocumentStatus
from app.schemas.queries import AnswerResponse, QuestionRequest, Source

router = APIRouter(prefix="/documents", tags=["questions"])


@router.post("/{document_id}/questions", response_model=AnswerResponse)
async def ask_question(document_id: str, request: QuestionRequest) -> AnswerResponse:
    document = documents.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.status != DocumentStatus.completed:
        raise HTTPException(status_code=409, detail=f"Document is {document.status}")
    client = OllamaClient()
    try:
        query_embedding = await client.embed(request.question)
        results = VectorStore().collection(document_id).query(query_embeddings=[query_embedding], n_results=request.top_k)
        texts = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        answer = await client.answer(request.question, "\n\n".join(texts))
    except (httpx.HTTPError, KeyError) as exc:
        raise HTTPException(status_code=503, detail="The Ollama model is unavailable") from exc
    sources = [Source(page=item["page"], text=text) for item, text in zip(metadatas, texts)] if request.include_sources else []
    return AnswerResponse(document_id=document_id, question=request.question, answer=answer, sources=sources)
