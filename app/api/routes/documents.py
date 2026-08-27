import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status

from app.api.deps import get_document_service, get_ingestion_service, get_settings_provider
from app.core.config import Settings
from app.schemas.documents import DocumentDetail, DocumentResponse
from app.services.document_service import DocumentService
from app.services.errors import DocumentDeletionError
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/documents", tags=["documents"])
UPLOAD_CHUNK_SIZE = 1024 * 1024


async def save_upload(file: UploadFile, destination: Path, max_bytes: int) -> None:
    total_bytes = 0
    first_chunk = True
    temporary_destination = destination.with_suffix(".part")

    try:
        with temporary_destination.open("wb") as output:
            while chunk := await file.read(UPLOAD_CHUNK_SIZE):
                if first_chunk and not chunk.startswith(b"%PDF-"):
                    raise HTTPException(status_code=415, detail="Uploaded file is not a valid PDF")
                first_chunk = False
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise HTTPException(status_code=413, detail="PDF exceeds the configured size limit")
                output.write(chunk)
        temporary_destination.replace(destination)
    except Exception:
        temporary_destination.unlink(missing_ok=True)
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings_provider),
    document_service: DocumentService = Depends(get_document_service),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> DocumentResponse:

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are supported")

    document_id = str(uuid.uuid4())
    upload_path = Path(settings.upload_path)
    upload_path.mkdir(parents=True, exist_ok=True)
    file_path = upload_path / f"{document_id}.pdf"
    await save_upload(file, file_path, settings.max_pdf_size_mb * 1024 * 1024)

    try:
        document = await document_service.create_document(document_id, file.filename or "document.pdf", str(file_path))
    except Exception:
        file_path.unlink(missing_ok=True)
        raise
    background_tasks.add_task(ingestion_service.ingest_document, document_id, file_path)
    return document


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(document_id: str) -> DocumentDetail:
    document = await DocumentService().get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> None:
    try:
        deleted = await document_service.delete_document(document_id)
    except DocumentDeletionError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if deleted is None:
        raise HTTPException(status_code=404, detail="Document not found")
