from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Document Models
class DocumentBase(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255, description="Document filename")
    file_type: str = Field(..., min_length=1, max_length=50, description="File type/extension")
    file_hash: str = Field(..., min_length=1, max_length=128, description="Unique file hash")
    total_chunks: int = Field(default=0, ge=0, description="Total number of chunks")

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    filename: Optional[str] = Field(None, min_length=1, max_length=255, description="Document filename")
    file_type: Optional[str] = Field(None, min_length=1, max_length=50, description="File type/extension")
    file_hash: Optional[str] = Field(None, min_length=1, max_length=128, description="Unique file hash")
    total_chunks: Optional[int] = Field(None, ge=0, description="Total number of chunks")

class DocumentInDB(DocumentBase):
    id: str
    created_at: datetime
    updated_at: datetime

class DocumentResponse(DocumentInDB):
    class Config:
        from_attributes = True

# Chunk Models
class ChunkBase(BaseModel):
    document_id: str = Field(..., description="Reference to parent document")
    chunk_index: int = Field(..., ge=0, description="Index of chunk within document")
    content: str = Field(..., min_length=1, description="Chunk content text")
    token_count: int = Field(..., ge=0, description="Number of tokens in chunk")
    start_char_index: int = Field(..., ge=0, description="Starting character index in original document")
    end_char_index: int = Field(..., ge=0, description="Ending character index in original document")
    vector_id: str = Field(..., min_length=1, max_length=255, description="Unique vector identifier")

class ChunkCreate(ChunkBase):
    pass

class ChunkUpdate(BaseModel):
    document_id: Optional[str] = Field(None, description="Reference to parent document")
    chunk_index: Optional[int] = Field(None, ge=0, description="Index of chunk within document")
    content: Optional[str] = Field(None, min_length=1, description="Chunk content text")
    token_count: Optional[int] = Field(None, ge=0, description="Number of tokens in chunk")
    start_char_index: Optional[int] = Field(None, ge=0, description="Starting character index in original document")
    end_char_index: Optional[int] = Field(None, ge=0, description="Ending character index in original document")
    vector_id: Optional[str] = Field(None, min_length=1, max_length=255, description="Unique vector identifier")

class ChunkInDB(ChunkBase):
    id: str
    created_at: datetime
    updated_at: datetime

class ChunkResponse(ChunkInDB):
    class Config:
        from_attributes = True