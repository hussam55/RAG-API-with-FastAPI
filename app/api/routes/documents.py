import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.document_processing.pdf_loader import extract_pages
from app.document_processing.text_splitter import split_text
from app.providers.ollama_client import OllamaClient
from app.providers.vector_store import VectorStore
from app.schemas.documents import DocumentDetail, DocumentResponse, DocumentStatus

router = APIRouter(prefix="/documents", tags=["documents"])
documents: dict[str, DocumentDetail] = {}


async def ingest(document_id: str, path: Path) -> None:
    document = documents[document_id].model_copy(update={"status": DocumentStatus.processing})
    documents[document_id] = document
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
        documents[document_id] = document.model_copy(update={"status": DocumentStatus.completed, "page_count": len(pages), "chunk_count": len(texts)})
    except Exception as exc:
        documents[document_id] = document.model_copy(update={"status": DocumentStatus.failed, "error": str(exc)})


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
    document = DocumentDetail(id=document_id, filename=file.filename or "document.pdf", status=DocumentStatus.queued, created_at=datetime.now(timezone.utc))
    documents[document_id] = document
    background_tasks.add_task(ingest, document_id, file_path)
    return document


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(document_id: str) -> DocumentDetail:
    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    return documents[document_id]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str) -> None:
    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    VectorStore().delete(document_id)
    documents.pop(document_id)
