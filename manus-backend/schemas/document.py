from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255, description="Document filename")
    file_path: str = Field(..., min_length=1, max_length=255, description="File path")
    file_type: str = Field(..., min_length=1, max_length=50, description="File type/extension")
    file_hash: str = Field(..., min_length=1, max_length=128, description="Unique file hash")
    total_chunks: int = Field(default=0, ge=0, description="Total number of chunks")

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    filename: Optional[str] = Field(None, min_length=1, max_length=255, description="Document filename")
    file_path: str = Field(None, min_length=1, max_length=255, description="File path")
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