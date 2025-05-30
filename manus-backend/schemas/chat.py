from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Chat title")

class ChatCreate(ChatBase):
    pass

class ChatUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Chat title")

class ChatInDB(ChatBase):
    id: str
    created_at: datetime
    updated_at: datetime

class ChatResponse(ChatInDB):
    class Config:
        from_attributes = True