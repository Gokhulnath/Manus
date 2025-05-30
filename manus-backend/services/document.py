from typing import List, Optional
from supabase import Client
from datetime import datetime, timezone
import uuid
from schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from models.document import Document


class DocumentService:
    def __init__(self, db: Client):
        self.db = db
        self.table_name = "documents"

    async def create_document(self, document_data: DocumentCreate) -> DocumentResponse:
        """Create a new document."""
        document = Document(
            filename=document_data.filename,
            file_path=document_data.file_path,
            file_type=document_data.file_type,
            file_hash=document_data.file_hash,
            total_chunks=document_data.total_chunks
        )

        result = self.db.table(self.table_name).insert(document.to_dict()).execute()

        if not result.data:
            raise ValueError("Failed to create document")

        return DocumentResponse(**result.data[0])

    async def get_documents(self, skip: int = 0, limit: int = 100) -> List[DocumentResponse]:
        """Get all documents with pagination."""
        result = self.db.table(self.table_name).select("*").range(skip, skip + limit - 1).order("created_at",
                                                                                                 desc=True).execute()

        return [DocumentResponse(**document) for document in result.data]

    async def get_document_by_id(self, document_id: str) -> Optional[DocumentResponse]:
        """Get a document by ID."""
        try:
            uuid.UUID(document_id)
        except ValueError:
            raise ValueError("Invalid document ID format")

        result = self.db.table(self.table_name).select("*").eq("id", document_id).execute()

        if not result.data:
            return None

        return DocumentResponse(**result.data[0])

    async def get_document_by_filename(self, filename: str) -> Optional[DocumentResponse]:
        """Get a document by file path."""
        result = self.db.table(self.table_name).select("*").eq("filename", filename).execute()

        if not result.data:
            return None

        return DocumentResponse(**result.data[0])

    async def get_document_by_hash(self, file_hash: str) -> Optional[DocumentResponse]:
        """Get a document by file hash."""
        result = self.db.table(self.table_name).select("*").eq("file_hash", file_hash).execute()

        if not result.data:
            return None

        return DocumentResponse(**result.data[0])

    async def update_document(self, document_id: str, document_update: DocumentUpdate) -> Optional[DocumentResponse]:
        """Update a document."""
        try:
            uuid.UUID(document_id)
        except ValueError:
            raise ValueError("Invalid document ID format")

        existing = await self.get_document_by_id(document_id)
        if not existing:
            return None

        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}

        if document_update.filename is not None:
            update_data["filename"] = document_update.filename
        if document_update.file_path is not None:
            update_data["file_path"] = document_update.file_path
        if document_update.file_type is not None:
            update_data["file_type"] = document_update.file_type
        if document_update.file_hash is not None:
            update_data["file_hash"] = document_update.file_hash
        if document_update.total_chunks is not None:
            update_data["total_chunks"] = document_update.total_chunks

        result = self.db.table(self.table_name).update(update_data).eq("id", document_id).execute()

        if not result.data:
            raise ValueError("Failed to update document")

        return DocumentResponse(**result.data[0])

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        try:
            uuid.UUID(document_id)
        except ValueError:
            raise ValueError("Invalid document ID format")

        existing = await self.get_document_by_id(document_id)
        if not existing:
            return False

        self.db.table(self.table_name).delete().eq("id", document_id).execute()
        return True