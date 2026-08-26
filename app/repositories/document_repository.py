from datetime import datetime, timezone

from sqlalchemy import select

from app.db.models import DocumentRecord
from app.db.session import SessionFactory
from app.schemas.documents import DocumentDetail, DocumentStatus


class DocumentRepository:
    @staticmethod
    def _to_schema(record: DocumentRecord) -> DocumentDetail:
        return DocumentDetail(
            id=record.id,
            filename=record.filename,
            status=DocumentStatus(record.status),
            created_at=record.created_at,
            page_count=record.page_count,
            chunk_count=record.chunk_count,
            error=record.error,
        )

    async def create(self, document_id: str, filename: str, storage_path: str) -> DocumentDetail:
        async with SessionFactory() as session:
            record = DocumentRecord(
                id=document_id,
                filename=filename,
                storage_path=storage_path,
                status=DocumentStatus.queued.value,
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return self._to_schema(record)

    async def get(self, document_id: str) -> DocumentDetail | None:
        async with SessionFactory() as session:
            record = await session.get(DocumentRecord, document_id)
            if record is None:
                return None
            return self._to_schema(record)

    async def get_storage_path(self, document_id: str) -> str | None:
        async with SessionFactory() as session:
            record = await session.get(DocumentRecord, document_id)
            if record is None:
                return None
            return record.storage_path

    async def set_status(
        self,
        document_id: str,
        status: DocumentStatus,
        page_count: int | None = None,
        chunk_count: int | None = None,
        error: str | None = None,
    ) -> None:
        async with SessionFactory() as session:
            record = await session.get(DocumentRecord, document_id)
            if record is None:
                return
            record.status = status.value
            record.page_count = page_count
            record.chunk_count = chunk_count
            record.error = error
            record.updated_at = datetime.now(timezone.utc)
            await session.commit()

    async def delete(self, document_id: str) -> DocumentDetail | None:
        async with SessionFactory() as session:
            record = await session.get(DocumentRecord, document_id)
            if record is None:
                return None
            snapshot = self._to_schema(record)
            await session.delete(record)
            await session.commit()
            return snapshot

    async def exists(self, document_id: str) -> bool:
        async with SessionFactory() as session:
            result = await session.execute(select(DocumentRecord.id).where(DocumentRecord.id == document_id))
            return result.scalar_one_or_none() is not None
