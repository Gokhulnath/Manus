from typing import List, Optional
from supabase import Client
from datetime import datetime, timezone
import uuid

from schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, ChunkCreate, ChunkResponse, ChunkUpdate
from models.document import Document, Chunk


class DocumentService:
    def __init__(self, db: Client):
        self.db = db
        self.table_name = "documents"

    async def create_document(self, document_data: DocumentCreate) -> DocumentResponse:
        """Create a new document."""
        document = Document(
            filename=document_data.filename,
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


class ChunkService:
    def __init__(self, db: Client):
        self.db = db
        self.table_name = "chunks"

    async def create_chunk(self, chunk_data: ChunkCreate) -> ChunkResponse:
        """Create a new chunk."""
        chunk = Chunk(
            document_id=chunk_data.document_id,
            chunk_index=chunk_data.chunk_index,
            content=chunk_data.content,
            token_count=chunk_data.token_count,
            start_char_index=chunk_data.start_char_index,
            end_char_index=chunk_data.end_char_index,
            vector_id=chunk_data.vector_id
        )

        result = self.db.table(self.table_name).insert(chunk.to_dict()).execute()

        if not result.data:
            raise ValueError("Failed to create chunk")

        return ChunkResponse(**result.data[0])

    async def get_chunks(self, skip: int = 0, limit: int = 100) -> List[ChunkResponse]:
        """Get all chunks with pagination."""
        result = self.db.table(self.table_name).select("*").range(skip, skip + limit - 1).order("created_at",
                                                                                                desc=True).execute()

        return [ChunkResponse(**chunk) for chunk in result.data]

    async def get_chunk_by_id(self, chunk_id: str) -> Optional[ChunkResponse]:
        """Get a chunk by ID."""
        try:
            uuid.UUID(chunk_id)
        except ValueError:
            raise ValueError("Invalid chunk ID format")

        result = self.db.table(self.table_name).select("*").eq("id", chunk_id).execute()

        if not result.data:
            return None

        return ChunkResponse(**result.data[0])

    async def get_chunks_by_document_id(self, document_id: str) -> List[ChunkResponse]:
        """Get all chunks for a specific document."""
        try:
            uuid.UUID(document_id)
        except ValueError:
            raise ValueError("Invalid document ID format")

        result = self.db.table(self.table_name).select("*").eq("document_id", document_id).order("chunk_index").execute()

        return [ChunkResponse(**chunk) for chunk in result.data]

    async def get_chunk_by_vector_id(self, vector_id: str) -> Optional[ChunkResponse]:
        """Get a chunk by vector ID."""
        result = self.db.table(self.table_name).select("*").eq("vector_id", vector_id).execute()

        if not result.data:
            return None

        return ChunkResponse(**result.data[0])

    async def update_chunk(self, chunk_id: str, chunk_update: ChunkUpdate) -> Optional[ChunkResponse]:
        """Update a chunk."""
        try:
            uuid.UUID(chunk_id)
        except ValueError:
            raise ValueError("Invalid chunk ID format")

        existing = await self.get_chunk_by_id(chunk_id)
        if not existing:
            return None

        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}

        if chunk_update.document_id is not None:
            update_data["document_id"] = chunk_update.document_id
        if chunk_update.chunk_index is not None:
            update_data["chunk_index"] = chunk_update.chunk_index
        if chunk_update.content is not None:
            update_data["content"] = chunk_update.content
        if chunk_update.token_count is not None:
            update_data["token_count"] = chunk_update.token_count
        if chunk_update.start_char_index is not None:
            update_data["start_char_index"] = chunk_update.start_char_index
        if chunk_update.end_char_index is not None:
            update_data["end_char_index"] = chunk_update.end_char_index
        if chunk_update.vector_id is not None:
            update_data["vector_id"] = chunk_update.vector_id

        result = self.db.table(self.table_name).update(update_data).eq("id", chunk_id).execute()

        if not result.data:
            raise ValueError("Failed to update chunk")

        return ChunkResponse(**result.data[0])

    async def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a chunk."""
        try:
            uuid.UUID(chunk_id)
        except ValueError:
            raise ValueError("Invalid chunk ID format")

        existing = await self.get_chunk_by_id(chunk_id)
        if not existing:
            return False

        self.db.table(self.table_name).delete().eq("id", chunk_id).execute()
        return True

    async def delete_chunks_by_document_id(self, document_id: str) -> bool:
        """Delete all chunks for a specific document."""
        try:
            uuid.UUID(document_id)
        except ValueError:
            raise ValueError("Invalid document ID format")

        self.db.table(self.table_name).delete().eq("document_id", document_id).execute()
        return True