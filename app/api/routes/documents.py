import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.schemas.documents import DocumentDetail, DocumentResponse
from app.services.document_service import DocumentService
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> DocumentResponse:
    settings = get_settings()
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are supported")
    content = await file.read()
    if len(content) > settings.max_pdf_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF exceeds the configured size limit")
    document_id = str(uuid.uuid4())
    upload_path = Path(settings.upload_path)
    upload_path.mkdir(parents=True, exist_ok=True)
    file_path = upload_path / f"{document_id}.pdf"
    file_path.write_bytes(content)
    document = await DocumentService().create_document(document_id, file.filename or "document.pdf", str(file_path))
    background_tasks.add_task(IngestionService().ingest_document, document_id, file_path)
    return document


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(document_id: str) -> DocumentDetail:
    document = await DocumentService().get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str) -> None:
    deleted = await DocumentService().delete_document(document_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Document not found")
