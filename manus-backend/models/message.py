from datetime import datetime, timezone
import uuid
from typing import Optional
from core.enums import MessageRole, MessageTask, MessageStatus


class Message:
    def __init__(
        self,
        chat_id: str,
        content: str,
        role: MessageRole,
        task: MessageTask,
        status: MessageStatus,
        id: Optional[str] = None,
        chunk_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.chat_id = chat_id
        self.chunk_id = chunk_id
        self.content = content
        self.role = role
        self.task = task
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "chunk_id": self.chunk_id,
            "content": self.content,
            "role": self.role.value,
            "task": self.task.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
