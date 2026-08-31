from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_query_service
from app.schemas.queries import AnswerResponse, QuestionRequest
from app.services.errors import DocumentNotFoundError, DocumentNotReadyError, ModelUnavailableError
from app.services.query_service import QueryService

router = APIRouter(prefix="/documents", tags=["questions"])


@router.post("/{document_id}/questions", response_model=AnswerResponse)
async def ask_question(
    document_id: str,
    request: QuestionRequest,
    query_service: QueryService = Depends(get_query_service),
) -> AnswerResponse:
    try:
        return await query_service.ask(document_id, request)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    except DocumentNotReadyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ModelUnavailableError as exc:
        raise HTTPException(status_code=503, detail="The Ollama model is unavailable") from exc
