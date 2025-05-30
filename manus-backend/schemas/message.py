from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from core.enums import MessageRole, MessageTask, MessageStatus


class MessageBase(BaseModel):
    chat_id: str = Field(..., description="Associated chat ID")
    chunk_id: Optional[str] = Field(None, description="Optional reference to a chunk")
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., min_length=1, description="Message content")
    task: MessageTask = Field(..., description="Task type for this message")
    status: MessageStatus = Field(..., description="Current status of the message")


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, description="Updated message content")
    status: Optional[MessageStatus] = Field(None, description="Updated status")
    task: Optional[MessageTask] = Field(None, description="Updated task")
    chunk_id: Optional[str] = Field(None, description="Updated chunk reference")


class MessageInDB(MessageBase):
    id: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(MessageInDB):
    class Config:
        from_attributes = True